# Smart Keyboard V1

Application de prédiction du mot suivant, développée avec Streamlit et un modèle de langue à n-grammes.

## Lancer l’application

Depuis le dossier du projet, active l’environnement virtuel puis lance :

```powershell
.venv\Scripts\Activate.ps1
streamlit run app.py
```

L’application s’ouvre dans le navigateur. Saisis un début de phrase dans le champ **Your sentence**.

## Fonctionnalités

- L’interface affiche jusqu’à **cinq suggestions** pour le mot suivant, au lieu de trois.
- Chaque suggestion indique une probabilité estimée. Cliquer sur une suggestion l’ajoute à la phrase.
- Le bouton **Clear sentence** efface la saisie.
- Un mot absent du corpus est traité comme inconnu (`<unk>`). L’application ne montre pas de message d’erreur et continue à proposer des mots connus du corpus.
- Le modèle utilise un repli (*back-off*) : il cherche d’abord un contexte trigramme, puis bigramme, et enfin unigramme si le contexte plus précis n’a pas été rencontré.

## Changements apportés

1. Le nombre de suggestions demandé au modèle est passé de trois à cinq.
2. L’interface crée cinq emplacements pour afficher ces suggestions.
3. Le message signalant les mots hors vocabulaire a été retiré. Le modèle les remplace en interne par `<unk>` pour poursuivre le calcul des suggestions.
4. L’en-tête des suggestions indique le modèle utilisé et le nombre de résultats affichés.

## Captures d’écran

Ajoute ici les captures d’exécution de l’application. Par exemple, une capture avec une phrase connue du corpus et une autre avec un mot absent du corpus, pour montrer que les suggestions continuent sans message d’erreur.

<!-- Exemple après ajout des fichiers :
![Cinq suggestions pour une phrase](docs/captures/suggestions-5-mots.png)
![Suggestions avec un mot absent du corpus](docs/captures/mot-hors-corpus.png)
-->

## Fichiers principaux

- `app.py` : interface Streamlit, saisie du texte et affichage des suggestions.
- `src/pipeline.py` : modèles n-grammes, traitement des mots inconnus et mécanisme de back-off.
- `data/corpus.csv` : corpus utilisé pour entraîner les modèles.
- `config.toml` : configuration visuelle et paramètre de collecte des statistiques de Streamlit.
- `results/` : résultats des évaluations du modèle.

## Configuration Streamlit (`config.toml`)

Le fichier `config.toml` contient les réglages d’apparence de Streamlit : thème clair, couleur principale bleue, fond gris clair, arrière-plan secondaire blanc, couleur du texte et police sans sérif. Il désactive également la collecte des statistiques d’utilisation (`gatherUsageStats = false`).

**Emplacement à noter :** Streamlit charge automatiquement sa configuration projet depuis `.streamlit/config.toml`. Le fichier du projet est actuellement à la racine sous le nom `config.toml`; pour que ses réglages soient appliqués au lancement, place-le dans le dossier `.streamlit` (`.streamlit/config.toml`).
