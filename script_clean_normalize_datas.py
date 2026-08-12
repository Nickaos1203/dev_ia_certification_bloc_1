import json
import re
from pathlib import Path
from urllib.parse import urlparse

# Configuration
INPUT_FILE = Path("videogames_dataset.json")
OUTPUT_FILE = Path("videogames_dataset_clean.json")


# Nettoyage des textes
def clean_text(value):
    """
    Nettoie une valeur textuelle :
    - None reste None
    - suppression des espaces en début/fin
    - remplacement des espaces multiples
    - normalisation des retours à la ligne
    """

    if value is None:
        return None

    if not isinstance(value, str):
        value = str(value)

    value = value.strip()

    # Remplace \n, \r\n, \t et espaces multiples
    value = re.sub(r"\s+", " ", value)

    return value if value else None


# ============================================================
# Nettoyage des listes
# ============================================================

def clean_list(values):
    """
    Nettoie une liste de valeurs textuelles :
    - supprime les valeurs nulles
    - supprime les chaînes vides
    - supprime les espaces inutiles
    - supprime les doublons
    - conserve l'ordre initial
    """

    if values is None:
        return []

    # Permet de gérer également une valeur unique
    if isinstance(values, str):
        values = [values]

    cleaned = []

    for value in values:
        value = clean_text(value)
        if value and value not in cleaned:
            cleaned.append(value)
    return cleaned


# Nettoyage des scores
def clean_score(value, minimum, maximum):
    """
    Convertit un score en float et vérifie sa plage.

    Si la valeur est invalide ou hors plage :
    - retourne None
    - ajoute un avertissement
    """

    if value is None:
        return None

    try:
        score = float(str(value).strip())
    except (ValueError, TypeError):
        return None

    if not minimum <= score <= maximum:
        return None

    return score


# ============================================================
# Validation URL
# ============================================================

def clean_url(value):
    value = clean_text(value)
    if not value:
        return None

    try:
        parsed = urlparse(value)
        if parsed.scheme not in ("http", "https"):
            return None
        if not parsed.netloc:
            return None
        return value

    except Exception:
        return None


# Normalisation des données
def clean_game(game, index):

    errors = []
    warnings = []

    # URL
    url = clean_url(game.get("url"))
    if not url:
        errors.append("URL absente ou invalide")

    # Titre
    titre = clean_text(game.get("titre"))
    if not titre:
        errors.append("Titre absent")

    # Editeur
    editeur = clean_text(game.get("editeur"))

    # None est conservé comme NULL PostgreSQL
    if editeur is None:
        warnings.append("Editeur absent")

    # Description
    description = clean_text(game.get("description"))

    # Plateformes
    plateformes = clean_list(
        game.get("plateformes", [])
    )
    if not plateformes:
        warnings.append("Aucune plateforme")

    # Genre
    # Dans le JSON source :
    # "genre": "Action RPG"
    # On le transforme en :
    # "genres": ["Action RPG"]
    # afin de pouvoir gérer ensuite une relation N-N.
    genre = clean_text(game.get("genre"))
    genres = []
    if genre:
        genres = [genre]
    else:
        warnings.append("Genre absent")

    # Score Metacritic
    score_metacritic = clean_score(
        game.get("score_metacritic"),
        minimum=0,
        maximum=100
    )
    if (
        game.get("score_metacritic") is not None
        and score_metacritic is None
    ):
        warnings.append(
            f"Score Metacritic invalide : "
            f"{game.get('score_metacritic')}"
        )

    # Score utilisateur
    score_utilisateurs = clean_score(
        game.get("score_utilisateurs"),
        minimum=0,
        maximum=10
    )
    if (
        game.get("score_utilisateurs") is not None
        and score_utilisateurs is None
    ):
        warnings.append(
            f"Score utilisateur invalide : "
            f"{game.get('score_utilisateurs')}"
        )

    # Objet normalisé
    cleaned_game = {
        "url": url,
        "titre": titre,
        "editeur": editeur,
        "description": description,
        "score_metacritic": score_metacritic,
        "score_utilisateurs": score_utilisateurs,
        "plateformes": plateformes,
        "genres": genres
    }
    return cleaned_game, errors, warnings


# Chargement du JSON
def load_json(filepath):

    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

# Nettoyage du dataset
def clean_dataset(data):
    cleaned_games = []
    errors = []
    warnings = []
    urls = set()

    for index, game in enumerate(data, start=1):
        cleaned_game, game_errors, game_warnings = clean_game(
            game,
            index
        )


        # Gestion des doublons d'URL
        url = cleaned_game["url"]
        if url:
            if url in urls:
                game_errors.append(
                    f"URL dupliquée : {url}"
                )
            else:
                urls.add(url)

        # Stockage des erreurs
        if game_errors:
            errors.append({
                "index": index,
                "titre": cleaned_game["titre"],
                "errors": game_errors
            })

        # Stockage des warnings
        if game_warnings:
            warnings.append({
                "index": index,
                "titre": cleaned_game["titre"],
                "warnings": game_warnings
            })

        # On conserve uniquement les jeux sans erreur bloquante
        if not game_errors:
            cleaned_games.append(cleaned_game)

    return cleaned_games, errors, warnings


# Sauvegarde
def save_json(data, filepath):
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )


# Programme principal
def main():
    print("Chargement du fichier...")
    data = load_json(INPUT_FILE)
    print(f"{len(data)} jeux chargés.")

    # Nettoyage
    cleaned_games, errors, warnings = clean_dataset(data)

    # Sauvegarde
    save_json(
        cleaned_games,
        OUTPUT_FILE
    )

    # Rapport
    print()
    print("=" * 50)
    print("RÉSULTAT DU NETTOYAGE")
    print("=" * 50)

    print(f"Jeux source       : {len(data)}")
    print(f"Jeux valides      : {len(cleaned_games)}")
    print(f"Jeux avec erreurs : {len(errors)}")
    print(f"Jeux avec warning : {len(warnings)}")

    print()
    print(f"Fichier généré : {OUTPUT_FILE}")


    # Affichage des erreurs
    if errors:
        print()
        print("ERREURS :")

        for error in errors:
            print(
                f"- Jeu #{error['index']} "
                f"({error['titre']})"
            )

            for message in error["errors"]:
                print(f"    {message}")


    # Affichage des warnings
    if warnings:
        print()
        print("WARNINGS :")

        for warning in warnings:
            print(
                f"- Jeu #{warning['index']} "
                f"({warning['titre']})"
            )

            for message in warning["warnings"]:
                print(f"    {message}")


if __name__ == "__main__":
    main()