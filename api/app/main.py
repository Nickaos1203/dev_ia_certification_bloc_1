from fastapi import FastAPI, Depends, HTTPException, status

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Annotated, Optional
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas import JeuVideo, Genre, Plateforme, UserCreate, UserResponse, Token, JeuVideoCreate, JeuVideoUpdate
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user



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

# Accueil
@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API !!!"}


@app.get("/jeux", response_model=list[JeuVideo])
async def read_all_videogames():

    conn = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # =========================
    # Jeux vidéo
    # =========================

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

    # =========================
    # Plateformes
    # =========================

    cursor.execute("""
        SELECT
            jp.jeuvideo_id AS jeu_id,
            p.id AS plateforme_id,
            p.nom AS plateforme_nom
        FROM jeuvideo_plateforme jp
        INNER JOIN plateforme p
            ON jp.plateforme_id = p.id
        ORDER BY jp.jeuvideo_id, p.nom
    """)

    plateformes = cursor.fetchall()

    # =========================
    # Genres
    # =========================

    cursor.execute("""
        SELECT
            jg.jeuvideo_id AS jeu_id,
            g.id AS genre_id,
            g.nom AS genre_nom
        FROM jeuvideo_genre jg
        INNER JOIN genre g
            ON jg.genre_id = g.id
        ORDER BY jg.jeuvideo_id, g.nom
    """)

    genres = cursor.fetchall()

    cursor.close()
    conn.close()

    # =========================
    # Association plateformes
    # =========================

    plateformes_par_jeu = {}

    for plateforme in plateformes:

        jeu_id = plateforme["jeu_id"]

        if jeu_id not in plateformes_par_jeu:
            plateformes_par_jeu[jeu_id] = []

        plateformes_par_jeu[jeu_id].append(
            Plateforme(
                id=plateforme["plateforme_id"],
                nom=plateforme["plateforme_nom"]
            )
        )

    # =========================
    # Association genres
    # =========================

    genres_par_jeu = {}

    for genre in genres:

        jeu_id = genre["jeu_id"]

        if jeu_id not in genres_par_jeu:
            genres_par_jeu[jeu_id] = []

        genres_par_jeu[jeu_id].append(
            Genre(
                id=genre["genre_id"],
                nom=genre["genre_nom"]
            )
        )

    # =========================
    # Construction des résultats
    # =========================

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
                plateformes=plateformes_par_jeu.get(jeu_id, []),
                genres=genres_par_jeu.get(jeu_id, [])
            )
        )

    return result


@app.get("/jeux/{id}", response_model=JeuVideo)
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



#---------------------
# authentification
#---------------------
@app.post("/register",response_model=UserResponse)
async def register(user: UserCreate):
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

    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE username = %s
           OR email = %s
        """,
        (user.username, user.email)
    )

    existing_user = cursor.fetchone()

    if existing_user:

        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=400,
            detail="Username ou email déjà utilisé"
        )

    password_hash = get_password_hash(
        user.password
    )

    cursor.execute(
        """
        INSERT INTO users (
            username,
            email,
            password_hash
        )
        VALUES (%s, %s, %s)
        RETURNING
            id,
            username,
            email,
            is_active
        """,
        (
            user.username,
            user.email,
            password_hash
        )
    )

    new_user = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    return new_user


@app.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

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

    cursor.execute(
        """
        SELECT
            id,
            username,
            email,
            password_hash,
            is_active
        FROM users
        WHERE username = %s
        """,
        (form_data.username,)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Username ou mot de passe incorrect",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    if not verify_password(
        form_data.password,
        user["password_hash"]
    ):

        raise HTTPException(
            status_code=401,
            detail="Username ou mot de passe incorrect",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    if not user["is_active"]:

        raise HTTPException(
            status_code=400,
            detail="Utilisateur désactivé"
        )

    access_token = create_access_token(
        user["username"]
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.post("/logout")
async def logout(
    current_user: str = Depends(get_current_user)):
    return {
        "message": f"Utilisateur {current_user} déconnecté"
    }

@app.get("/users/me")
async def read_users_me(current_user: str = Depends(get_current_user)):
    return {
        "username": current_user
    }


@app.post("/jeux/create",response_model=JeuVideo,status_code=201)
async def create_videogame(
    jeu: JeuVideoCreate,
    current_user: str = Depends(get_current_user)
):

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

    # Création du jeu
    cursor.execute(
        """
        INSERT INTO jeuvideo (
            url,
            titre,
            editeur,
            description,
            score_metacritic,
            score_utilisateurs
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            jeu.url,
            jeu.titre,
            jeu.editeur,
            jeu.description,
            jeu.score_metacritic,
            jeu.score_utilisateurs
        )
    )

    nouveau_jeu = cursor.fetchone()

    jeu_id = nouveau_jeu["id"]

    # Plateformes
    for plateforme_id in jeu.plateformes:

        cursor.execute(
            """
            INSERT INTO jeuvideo_plateforme (
                jeuvideo_id,
                plateforme_id
            )
            VALUES (%s, %s)
            """,
            (jeu_id, plateforme_id)
        )

    # Genres
    for genre_id in jeu.genres:

        cursor.execute(
            """
            INSERT INTO jeuvideo_genre (
                jeuvideo_id,
                genre_id
            )
            VALUES (%s, %s)
            """,
            (jeu_id, genre_id)
        )

    conn.commit()

    cursor.close()
    conn.close()

    return {
        **nouveau_jeu,
        "plateformes": [],
        "genres": []
    }


@app.patch("/jeux/update/{id}",response_model=JeuVideo)
async def update_videogame(id: int, jeu: JeuVideoUpdate, current_user: str = Depends(get_current_user)):

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

    cursor.execute(
        """
        SELECT *
        FROM jeuvideo
        WHERE id = %s
        """,
        (id,)
    )

    existing_game = cursor.fetchone()

    if existing_game is None:

        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Jeu vidéo introuvable"
        )

    # Mise à jour des informations principales
    cursor.execute(
        """
        UPDATE jeuvideo
        SET
            url = COALESCE(%s, url),
            titre = COALESCE(%s, titre),
            editeur = COALESCE(%s, editeur),
            description = COALESCE(%s, description),
            score_metacritic = COALESCE(
                %s,
                score_metacritic
            ),
            score_utilisateurs = COALESCE(
                %s,
                score_utilisateurs
            )
        WHERE id = %s
        RETURNING *
        """,
        (
            jeu.url,
            jeu.titre,
            jeu.editeur,
            jeu.description,
            jeu.score_metacritic,
            jeu.score_utilisateurs,
            id
        )
    )

    updated_game = cursor.fetchone()

    # Plateformes
    if jeu.plateformes is not None:

        cursor.execute(
            """
            DELETE FROM jeuvideo_plateforme
            WHERE jeuvideo_id = %s
            """,
            (id,)
        )

        for plateforme_id in jeu.plateformes:

            cursor.execute(
                """
                INSERT INTO jeuvideo_plateforme (
                    jeuvideo_id,
                    plateforme_id
                )
                VALUES (%s, %s)
                """,
                (id, plateforme_id)
            )

    # Genres
    if jeu.genres is not None:

        cursor.execute(
            """
            DELETE FROM jeuvideo_genre
            WHERE jeuvideo_id = %s
            """,
            (id,)
        )

        for genre_id in jeu.genres:

            cursor.execute(
                """
                INSERT INTO jeuvideo_genre (
                    jeuvideo_id,
                    genre_id
                )
                VALUES (%s, %s)
                """,
                (id, genre_id)
            )

    conn.commit()

    cursor.close()
    conn.close()

    return {
        **updated_game,
        "plateformes": [],
        "genres": []
    }


@app.delete("/jeux/delete/{id}")
async def delete_videogame(
    id: int,
    current_user: str = Depends(get_current_user)
):

    conn = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM jeuvideo
        WHERE id = %s
        RETURNING id
        """,
        (id,)
    )

    deleted_game = cursor.fetchone()

    if deleted_game is None:

        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="Jeu vidéo introuvable"
        )

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "Jeu vidéo supprimé",
        "id": deleted_game[0]
    }

