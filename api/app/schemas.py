from pydantic import BaseModel, Field
from typing import Optional


# plateforme de jeu vidéo
class Plateforme(BaseModel):
    id: int
    nom: str


# genre de jeu vidéo
class Genre(BaseModel):
    id: int
    nom: str


# jeux vidéo
class JeuVideo(BaseModel):
    id: int
    url: str
    titre: str
    editeur: Optional[str] = None
    description: Optional[str] = None
    score_metacritic: Optional[float] = None
    score_utilisateurs: Optional[float] = None
    plateformes: list[Plateforme] = Field(default_factory=list)
    genres: list[Genre] = Field(default_factory=list)


# spécimens d'arbre
class Tree(BaseModel):
    id: int
    species_scientific_name: Optional[str] = None
    species_common_name: Optional[str] = None
    form: Optional[str] = None
    growth_rate: Optional[str] = None
    fall_color: Optional[str] = None
    environmental_tolerances: Optional[str] = None
    location_tolerances: Optional[str] = None
    notes_suggested_cultivars: Optional[str] = None
    tree_size: Optional[str] = None
    comments: Optional[str] = None


# salaires
class Salary(BaseModel):
    id: int
    geo: str
    sex: str
    freq: str
    time_period: int
    dera_measure: str
    pcs_ese: str
    obs_status: str
    conf_status: str
    obs_value_niveau: float




# Création d'un utilisateur
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


