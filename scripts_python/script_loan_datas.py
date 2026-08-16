import json
import os
import psycopg2
from dotenv import load_dotenv


# Configuration
JSON_FILE = "videogames_dataset_clean.json"


# Chargement des variables d'environnement
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


# Chargement du JSON comprenant les données à importer dans postgresql
with open(JSON_FILE, "r", encoding="utf-8") as file:
    games = json.load(file)

print(f"{len(games)} jeux à importer.")


# Connexion PostgreSQL
conn = psycopg2.connect(
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)


# Import
try:
    with conn.cursor() as cur:
        for game in games:

            # Insertion du jeu vidéo
            cur.execute(
                """
                INSERT INTO jeuvideo (
                    url,
                    titre,
                    editeur,
                    description,
                    score_metacritic,
                    score_utilisateurs
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                ON CONFLICT (url)
                DO UPDATE SET
                    titre = EXCLUDED.titre,
                    editeur = EXCLUDED.editeur,
                    description = EXCLUDED.description,
                    score_metacritic = EXCLUDED.score_metacritic,
                    score_utilisateurs = EXCLUDED.score_utilisateurs
                RETURNING id;
                """,
                (
                    game["url"],
                    game["titre"],
                    game.get("editeur"),
                    game.get("description"),
                    game.get("score_metacritic"),
                    game.get("score_utilisateurs")
                )
            )
            jeuvideo_id = cur.fetchone()[0]

            # Plateformes
            for plateforme_nom in game.get("plateformes", []):
                cur.execute(
                    """
                    INSERT INTO plateforme (nom)
                    VALUES (%s)
                    ON CONFLICT (nom)
                    DO UPDATE SET
                        nom = EXCLUDED.nom
                    RETURNING id;
                    """,
                    (plateforme_nom,)
                )
                plateforme_id = cur.fetchone()[0]

                # Relation jeu <-> plateforme
                cur.execute(
                    """
                    INSERT INTO jeuvideo_plateforme (
                        jeuvideo_id,
                        plateforme_id
                    )
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING;
                    """,
                    (
                        jeuvideo_id,
                        plateforme_id
                    )
                )

            # Genres
            for genre_nom in game.get("genres", []):

                cur.execute(
                    """
                    INSERT INTO genre (nom)
                    VALUES (%s)
                    ON CONFLICT (nom)
                    DO UPDATE SET
                        nom = EXCLUDED.nom
                    RETURNING id;
                    """,
                    (genre_nom,)
                )

                genre_id = cur.fetchone()[0]

                # Relation jeu <-> genre
                cur.execute(
                    """
                    INSERT INTO jeuvideo_genre (
                        jeuvideo_id,
                        genre_id
                    )
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING;
                    """,
                    (
                        jeuvideo_id,
                        genre_id
                    )
                )


    # Validation de la transaction
    conn.commit()
    print("Import terminé avec succès.")

except Exception as e:
    # Annulation en cas d'erreur
    conn.rollback()

    print("Erreur pendant l'import.")
    print(e)

    raise

finally:
    # Fermeture connexion
    conn.close()

    print("Connexion PostgreSQL fermée.")