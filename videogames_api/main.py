from fastapi import FastAPI
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Annotated, Optional
from dotenv import load_dotenv

from schemas import JeuVideo, Genre, Plateforme


# Chargement des variables d'environnement
load_dotenv()


# Variables PostgreSQL
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


# Création de l'API
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/jeux")
async def read_all_videogames():
    conn = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    # -------------------------
    # Récupération des jeux
    # -------------------------

    cursor.execute("""
        SELECT
            id,
            url,
            titre,
            editeur,
            description,
            score_metacritic,
            score_utilisateurs
        FROM jeuvideo
        ORDER BY id
    """)

    jeux = cursor.fetchall()


    # -------------------------
    # Récupération des plateformes
    # -------------------------

    cursor.execute("""
        SELECT
            jp.jeuvideo_id,
            p.id,
            p.nom
        FROM jeuvideo_plateforme jp
        INNER JOIN plateforme p
            ON jp.plateforme_id = p.id
        ORDER BY jp.jeuvideo_id, p.nom
    """)

    plateformes = cursor.fetchall()


    # -------------------------
    # Récupération des genres
    # -------------------------

    cursor.execute("""
        SELECT
            jg.jeuvideo_id,
            g.id,
            g.nom
        FROM jeuvideo_genre jg
        INNER JOIN genre g
            ON jg.genre_id = g.id
        ORDER BY jg.jeuvideo_id, g.nom
    """)

    genres = cursor.fetchall()


    cursor.close()
    conn.close()


    # -------------------------
    # Association plateformes
    # -------------------------

    plateformes_par_jeu = {}

    for plateforme in plateformes:

        jeu_id = plateforme["jeuvideo_id"]

        if jeu_id not in plateformes_par_jeu:
            plateformes_par_jeu[jeu_id] = []

        plateformes_par_jeu[jeu_id].append(
            Plateforme(
                id=plateforme["id"],
                nom=plateforme["nom"]
            )
        )


    # -------------------------
    # Association genres
    # -------------------------

    genres_par_jeu = {}

    for genre in genres:

        jeu_id = genre["jeuvideo_id"]

        if jeu_id not in genres_par_jeu:
            genres_par_jeu[jeu_id] = []

        genres_par_jeu[jeu_id].append(
            Genre(
                id=genre["id"],
                nom=genre["nom"]
            )
        )


    # -------------------------
    # Construction des jeux
    # -------------------------

    result = []

    for jeu in jeux:

        jeu_id = jeu["id"]

        result.append(
            JeuVideo(
                id=jeu["id"],
                url=jeu["url"],
                titre=jeu["titre"],
                editeur=jeu["editeur"],
                description=jeu["description"],
                score_metacritic=jeu["score_metacritic"],
                score_utilisateurs=jeu["score_utilisateurs"],
                plateformes=plateformes_par_jeu.get(
                    jeu_id,
                    []
                ),
                genres=genres_par_jeu.get(
                    jeu_id,
                    []
                )
            )
        )

    return result


@app.get("/jeux/{id}")
async def read_videogame_by_id(id:int):
    conn = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    cursor = conn.cursor(
        cursor_factory=RealDictCursor
    )

    # -------------------------
    # 1. Informations du jeu
    # -------------------------

    cursor.execute("""
        SELECT
            id,
            url,
            titre,
            editeur,
            description,
            score_metacritic,
            score_utilisateurs
        FROM jeuvideo
        WHERE id = %s
    """, (id,))

    jeu = cursor.fetchone()

    if jeu is None:
        cursor.close()
        conn.close()
        return None


    # -------------------------
    # 2. Plateformes du jeu
    # -------------------------

    cursor.execute("""
        SELECT
            p.id,
            p.nom
        FROM plateforme p
        INNER JOIN jeuvideo_plateforme jp
            ON p.id = jp.plateforme_id
        WHERE jp.jeuvideo_id = %s
        ORDER BY p.nom
    """, (id,))

    plateformes = cursor.fetchall()


    # -------------------------
    # 3. Genres du jeu
    # -------------------------

    cursor.execute("""
        SELECT
            g.id,
            g.nom
        FROM genre g
        INNER JOIN jeuvideo_genre jg
            ON g.id = jg.genre_id
        WHERE jg.jeuvideo_id = %s
        ORDER BY g.nom
    """, (id,))

    genres = cursor.fetchall()


    cursor.close()
    conn.close()


    # -------------------------
    # 4. Construction du résultat
    # -------------------------

    jeu["plateformes"] = plateformes
    jeu["genres"] = genres

    return jeu