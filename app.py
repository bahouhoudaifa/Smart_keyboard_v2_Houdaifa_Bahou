"""Lab 02 - Smart Keyboard V1 (Streamlit UI). Run:  streamlit run app.py"""
import html

import streamlit as st

from src.pipeline import NGramModel, EOS, load_documents, backoff_top_k

st.set_page_config(page_title="Smart Keyboard", page_icon="⌨️", layout="centered")

# --------------------------------------------------------------------------- #
# Styling
# --------------------------------------------------------------------------- #
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700&family=Figtree:wght@400;500;600&display=swap');

:root {
  --ink: #1b2430;
  --muted: #667085;
  --canvas: #e9edf4;
  --surface: #ffffff;
  --line: #d5dce8;
  --accent: #2f5bea;
  --accent-soft: #e4eafd;
  --warn-bg: #fff4dd;
  --warn-ink: #7a5200;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header[data-testid="stHeader"] { display: none; }

html, body, [data-testid="stAppViewContainer"], .stApp {
  background: var(--canvas);
  color: var(--ink);
  font-family: 'Figtree', system-ui, sans-serif;
}
.block-container { max-width: 760px; padding-top: 3.5rem; padding-bottom: 3rem; }

/* Title block */
.app-title {
  font-family: 'Bricolage Grotesque', 'Figtree', sans-serif;
  font-weight: 700; font-size: 2.6rem; letter-spacing: -0.02em;
  line-height: 1.05; margin: 0 0 .5rem 0; color: var(--ink);
}
.app-sub { color: var(--muted); font-size: 1.02rem; margin: 0 0 2rem 0; max-width: 56ch; }

/* Text input */
.stTextInput label p { font-weight: 600; color: var(--ink); font-size: .95rem; }
.stTextInput div[data-baseweb="input"] {
  background: var(--surface); border: 1.5px solid var(--line);
  border-radius: 16px; box-shadow: 0 1px 2px rgba(27,36,48,.06);
  transition: border-color .15s, box-shadow .15s;
}
.stTextInput div[data-baseweb="input"]:focus-within {
  border-color: var(--accent); box-shadow: 0 0 0 4px var(--accent-soft);
}
.stTextInput input {
  font-family: 'Figtree', sans-serif; font-size: 1.25rem; padding: .9rem 1rem;
  color: var(--ink); background: transparent;
}

/* Suggestion header */
.sug-head { display: flex; align-items: center; justify-content: space-between;
  margin: 2rem 0 .75rem 0; }
.sug-head h3 { font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.25rem;
  margin: 0; font-weight: 600; color: var(--ink); }
.pill { background: var(--accent-soft); color: var(--accent); font-weight: 600;
  font-size: .82rem; padding: .3rem .75rem; border-radius: 999px; }

/* Suggestion keys */
.stButton > button {
  width: 100%; min-height: 3.6rem; border-radius: 14px;
  background: var(--surface); color: var(--ink);
  border: 1.5px solid var(--line); box-shadow: 0 2px 0 var(--line);
  font-family: 'Figtree', sans-serif; font-size: 1.05rem; font-weight: 600;
  transition: transform .08s, box-shadow .08s, border-color .15s;
}
.stButton > button:hover { border-color: var(--accent); color: var(--accent); }
.stButton > button:active { transform: translateY(2px); box-shadow: 0 0 0 var(--line); }
.stButton > button:focus-visible { outline: 3px solid var(--accent-soft); outline-offset: 2px; }

/* Best suggestion is highlighted */
.st-key-sug_0 button {
  background: var(--accent); color: #fff; border-color: var(--accent);
  box-shadow: 0 2px 0 #2347b8;
}
.st-key-sug_0 button:hover { background: #2549c4; color: #fff; border-color: #2549c4; }
.st-key-sug_0 button p { color: #fff; }

/* Probability bar under each key */
.bar { height: 6px; background: var(--line); border-radius: 99px; margin: .55rem 0 .25rem 0; overflow: hidden; }
.bar span { display: block; height: 100%; background: var(--accent); border-radius: 99px; }
.pct { text-align: center; font-size: .85rem; font-weight: 600; color: var(--muted); }

/* Clear button (secondary) */
.st-key-clear button { min-height: 2.4rem; font-size: .9rem; box-shadow: none; color: var(--muted); }

/* Notices */
.notice { background: var(--warn-bg); color: var(--warn-ink); border-radius: 14px;
  padding: .8rem 1rem; margin-top: 1rem; font-size: .95rem; }
.notice code { background: rgba(0,0,0,.07); padding: .1rem .4rem; border-radius: 6px; }
.empty { background: var(--surface); border: 1.5px dashed var(--line); color: var(--muted);
  border-radius: 14px; padding: .9rem 1rem; margin-top: 1rem; font-size: .95rem; }

.footnote { color: var(--muted); font-size: .85rem; margin-top: 2.5rem; max-width: 60ch; }

@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<h1 class="app-title">Smart Keyboard</h1>'
    '<p class="app-sub">Start a sentence and tap a suggestion to keep going. '
    "</p>",
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------- #
# Model
# --------------------------------------------------------------------------- #
@st.cache_resource
def get_models():
    docs = load_documents()
    sentences = [s for d in docs.values() for s in d]
    return [NGramModel(sentences, n, 0.1) for n in (3, 2, 1)], sentences


(tri, bi, uni), sentences = get_models()

# --------------------------------------------------------------------------- #
# State & callbacks
# --------------------------------------------------------------------------- #
if "text" not in st.session_state:
    st.session_state.text = "the happy girls "


def pick(word: str) -> None:
    """Append the chosen suggestion to the sentence, like a phone keyboard."""
    current = st.session_state.text.rstrip()
    st.session_state.text = current + "." if word == EOS else f"{current} {word} "


def clear() -> None:
    st.session_state.text = ""


# --------------------------------------------------------------------------- #
# Input
# --------------------------------------------------------------------------- #
text = st.text_input("Your sentence", key="text", placeholder="Type the beginning of a sentence…")
words = text.lower().replace(".", " . ").split()
if not words:
    st.markdown(
        '<div class="empty">Nothing typed yet. These are the words sentences usually start with.</div>',
        unsafe_allow_html=True,
    )

# --------------------------------------------------------------------------- #
# Suggestions
# --------------------------------------------------------------------------- #
suggestions, order = backoff_top_k(tri, bi, uni, words, 5)

st.markdown(
    f'<div class="sug-head"><h3>Suggestions</h3>'
    f'<span class="pill">{html.escape(str(order))} model · top 5</span></div>',
    unsafe_allow_html=True,
)

top_p = max((p for _, p in suggestions), default=1) or 1
cols = st.columns(5, gap="small")
for i, (col, (w, p)) in enumerate(zip(cols, suggestions)):
    label = "End ." if w == EOS else w
    with col:
        st.button(label, key=f"sug_{i}", on_click=pick, args=(w,))
        st.markdown(
            f'<div class="bar"><span style="width:{p / top_p * 100:.0f}%"></span></div>'
            f'<div class="pct">{p:.1%}</div>',
            unsafe_allow_html=True,
        )

st.write("")
st.button("Clear sentence", key="clear", on_click=clear)

