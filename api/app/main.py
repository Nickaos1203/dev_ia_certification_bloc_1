from fastapi import FastAPI, Depends, HTTPException, status

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Annotated, Optional
from dotenv import load_dotenv

from fastapi.security import OAuth2PasswordRequestForm

from schemas import JeuVideo, Genre, Plateforme, Tree, Salary, UserCreate, UserResponse, Token
from auth import get_password_hash, verify_password, create_access_token, get_current_user, authenticate_user, connexion


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
async def home():
    """
    Affiche le message de bienvenue.

    Returns:
        message: Message de bienvenue.
    """
    return {"message": "Bienvenue sur l'API !!!"}


@app.get("/jeux", response_model=list[JeuVideo])
async def read_all_videogames(current_user: str = Depends(get_current_user)):
    """
    Retourne la liste de tous les jeux vidéo disponibles.

    Returns:
        list[JeuVideo]: Liste des jeux vidéo enregistrés dans la base de données.
    """
    conn = connexion()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT id, url, titre, editeur, description, score_metacritic, score_utilisateurs
        FROM jeuvideo
        ORDER BY id
    """)

    jeux = cursor.fetchall()

    # Plateformes
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

    # Genres
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


    # Association plateformes
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

    # Association genres
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

    # Construction des résultats
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
async def read_videogame_by_id(id:int, current_user: str = Depends(get_current_user)):
    """
    Retourne les informations d'un jeu vidéo à partir de son identifiant.

    Args:
        id (int): Identifiant du jeu vidéo à rechercher.

    Returns:
        JeuVideo: Données du jeu vidéo correspondant à l'identifiant fourni.
    """
    conn = connexion()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Informations du jeu
    cursor.execute("""
        SELECT id, url, titre, editeur, description, score_metacritic, score_utilisateurs
        FROM jeuvideo
        WHERE id = %s
    """, (id,))

    jeu = cursor.fetchone()

    if jeu is None:
        cursor.close()
        conn.close()
        return None


    # Plateformes du jeu
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

    # Genres du jeu
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


    # Construction du résultat
    jeu["plateformes"] = plateformes
    jeu["genres"] = genres
    return jeu


@app.get("/salaries", response_model=list[Salary])
async def salaries_list(current_user: str = Depends(get_current_user)):
    """
    Récupère la liste des données salariales.

    Returns:
        list[Salary]: Liste des données salariales issues de la table salary.
    """
    conn = connexion()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
    SELECT id, geo, sex, freq, time_period, dera_measure, pcs_ese, obs_status, conf_status, obs_value_niveau
    FROM salary
    """)

    salaries = cursor.fetchall()
    cursor.close()
    conn.close()

    return salaries


# salaire par id
@app.get("/salaries/{id}", response_model=Salary)
async def salary_by_id(id: int, current_user: str = Depends(get_current_user)):
    """
    Retourne les données salariales correspondant à un identifiant.

    Args:
        id (int): Identifiant de la donnée salariale à rechercher.

    Returns:
        Salary: Donnée salariale correspondant à l'identifiant fourni.
    """
    conn = connexion()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
    SELECT id, geo, sex, freq, time_period, dera_measure, pcs_ese, obs_status, conf_status, obs_value_niveau
    FROM salary
    WHERE id = %s
    """, (id,))

    salary = cursor.fetchone()
    cursor.close()
    conn.close()

    return salary


@app.get("/trees", response_model=list[Tree])
async def trees_list(current_user: str = Depends(get_current_user)):
    """
    Retourne la liste de toutes les espèces d'arbres disponibles.

    Returns:
        list[Tree]: Liste des espèces d'arbres enregistrées dans la base de données.
    """
    conn = connexion()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        """
        SELECT id, species_scientific_name, species_common_name, form, growth_rate, fall_color, environmental_tolerances, location_tolerances, notes_suggested_cultivars, tree_size, comments
        FROM tree_specie
        """)

    trees = cursor.fetchall()
    cursor.close()
    conn.close()

    return trees



@app.get("/trees/{id}", response_model=Tree)
async def trees_list(id: int, current_user: str = Depends(get_current_user)):
    """
    Retourne les informations d'une espèce d'arbre à partir de son identifiant.

    Args:
        id (int): Identifiant de l'espèce d'arbre recherchée.

    Returns:
        Tree: Données de l'espèce d'arbre correspondant à l'identifiant fourni.
    """
    conn = connexion()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        """
        SELECT id, species_scientific_name, species_common_name, form, growth_rate, fall_color, environmental_tolerances, location_tolerances, notes_suggested_cultivars, tree_size, comments
        FROM tree_specie
        WHERE id = %s
        """,(id,))

    tree = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return tree


@app.post("/register",response_model=UserResponse)
async def register(user: UserCreate):
    """
    Crée un nouvel utilisateur dans la base de données.

    Vérifie que le nom d'utilisateur et l'adresse e-mail ne sont pas
    déjà utilisés, puis hash le mot de passe avant d'enregistrer
    le nouvel utilisateur.

    Args:
        user (UserCreate): Données du nouvel utilisateur.

    Returns:
        User: Informations du nouvel utilisateur créé.
    """
    conn = connexion()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE username = %s
           OR email = %s
        """, (user.username, user.email)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Username ou email déjà utilisé")

    password_hash = get_password_hash(
        user.password
    )

    cursor.execute(
        """
        INSERT INTO users (username, email, password_hash)
        VALUES (%s, %s, %s)
        RETURNING id, username, email, is_active
        """,(user.username, user.email, password_hash)
    )

    new_user = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    return new_user


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authentifie un utilisateur et génère un token JWT.

    Vérifie les identifiants fournis et retourne un token d'accès
    en cas d'authentification réussie.

    Args:
        form_data (OAuth2PasswordRequestForm): Identifiant et mot de passe
            de l'utilisateur.

    Returns:
        dict: Token d'accès JWT et type de token.
    """
    return await authenticate_user(form_data)


@app.post("/logout")
async def logout(current_user: str = Depends(get_current_user)):
    """
    Déconnecte l'utilisateur actuellement authentifié.

    Args:
        current_user (str): Nom de l'utilisateur authentifié.

    Returns:
        dict: Message confirmant la déconnexion de l'utilisateur.
    """
    return {
        "message": f"Utilisateur {current_user} déconnecté"
    }


@app.get("/users/me")
async def read_users_me(current_user: str = Depends(get_current_user)):
    """
    Retourne les informations de l'utilisateur actuellement authentifié.

    Args:
        current_user (str): Nom de l'utilisateur authentifié.

    Returns:
        dict: Informations de l'utilisateur connecté.
    """
    return {
        "username": current_user
    }