import os
import psycopg2
from dotenv import load_dotenv


# Chargement des variables d'environnement
load_dotenv()

print("Database :", os.getenv("DB_NAME"))
print("User :", os.getenv("DB_USER"))
print("Password chargé :", bool(os.getenv("DB_PASSWORD")))


# Connexion PostgreSQL
conn = psycopg2.connect(
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    host=os.getenv("DB_HOST", "localhost"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT", "5432")
)


# Création des tables
sql = """

CREATE TABLE IF NOT EXISTS jeuvideo (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    titre VARCHAR(255) NOT NULL,
    editeur VARCHAR(255),
    description TEXT,
    score_metacritic NUMERIC(4,1),
    score_utilisateurs NUMERIC(4,1)
);


CREATE TABLE IF NOT EXISTS plateforme (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL
);


CREATE TABLE IF NOT EXISTS genre (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL
);


CREATE TABLE IF NOT EXISTS jeuvideo_plateforme (
    jeuvideo_id INTEGER NOT NULL,
    plateforme_id INTEGER NOT NULL,

    PRIMARY KEY (jeuvideo_id, plateforme_id),

    FOREIGN KEY (jeuvideo_id)
        REFERENCES jeuvideo(id)
        ON DELETE CASCADE,

    FOREIGN KEY (plateforme_id)
        REFERENCES plateforme(id)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS jeuvideo_genre (
    jeuvideo_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,

    PRIMARY KEY (jeuvideo_id, genre_id),

    FOREIGN KEY (jeuvideo_id)
        REFERENCES jeuvideo(id)
        ON DELETE CASCADE,

    FOREIGN KEY (genre_id)
        REFERENCES genre(id)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS users (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

"""


# Exécution
try:

    with conn.cursor() as cur:
        cur.execute(sql)

    conn.commit()
    print("Les tables ont été créées avec succès.")

except Exception as e:

    conn.rollback()
    print("Erreur lors de la création des tables :")
    print(e)

finally:

    conn.close()
    print("Connexion PostgreSQL fermée.")