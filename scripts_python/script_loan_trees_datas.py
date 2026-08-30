import json
import os
import psycopg2
from dotenv import load_dotenv


# ==========================================================
# Configuration
# ==========================================================

JSON_FILE = "tree_species.json"


# ==========================================================
# Chargement des variables d'environnement
# ==========================================================

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


# ==========================================================
# Chargement du JSON
# ==========================================================

with open(JSON_FILE, "r", encoding="utf-8") as file:
    tree_species = json.load(file)

print(f"{len(tree_species)} espèces à importer.")


# ==========================================================
# Connexion PostgreSQL
# ==========================================================

conn = psycopg2.connect(
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)


# ==========================================================
# Import
# ==========================================================

try:

    with conn.cursor() as cur:

        for tree in tree_species:

            cur.execute(
                """
                INSERT INTO tree_species (
                    species_scientific_name,
                    species_common_name,
                    form,
                    growth_rate,
                    fall_color,
                    environmental_tolerances,
                    location_tolerances,
                    notes_suggested_cultivars,
                    tree_size,
                    comments
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                );
                """,
                (
                    tree.get("species_scientific_name"),
                    tree.get("species_common_name"),
                    tree.get("form"),
                    tree.get("growth_rate"),
                    tree.get("fall_color"),
                    tree.get("environmental_tolerances"),
                    tree.get("location_tolerances"),
                    tree.get("notes_suggested_cultivars"),
                    tree.get("tree_size"),
                    tree.get("comments")
                )
            )


    # ======================================================
    # Validation de la transaction
    # ======================================================

    conn.commit()

    print("Import terminé avec succès.")


except Exception as e:

    # ======================================================
    # Annulation en cas d'erreur
    # ======================================================

    conn.rollback()

    print("Erreur pendant l'import.")
    print(e)

    raise


finally:

    # ======================================================
    # Fermeture de la connexion
    # ======================================================

    conn.close()

    print("Connexion PostgreSQL fermée.")