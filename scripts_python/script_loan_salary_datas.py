import json
import os
import psycopg2
from dotenv import load_dotenv


# Configuration
JSON_FILE = "salaries.json"


# Chargement des variables d'environnement
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


# Chargement du JSON
with open(JSON_FILE, "r", encoding="utf-8") as file:
    salaries = json.load(file)

print(f"{len(salaries)} lignes de la table 'salaries' à importer.")



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
        for salary in salaries:
            cur.execute(
                """
                INSERT INTO salaries (
                        geo,
                        sex,
                        freq,
                        time_period,
                        dera_measure,
                        pcs_ese,
                        obs_status,
                        conf_status,
                        obs_value_niveau)
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s);
                """,
                (
                    salary.get("GEO"),
                    salary.get("SEX"),
                    salary.get("FREQ"),
                    salary.get("TIME_PERIOD"),
                    salary.get("DERA_MEASURE"),
                    salary.get("PCS_ESE"),
                    salary.get("OBS_STATUS"),
                    salary.get("CONF_STATUS"),
                    salary.get("OBS_VALUE_NIVEAU")
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
    # Fermeture de la connexion
    conn.close()
    print("Connexion PostgreSQL fermée.")