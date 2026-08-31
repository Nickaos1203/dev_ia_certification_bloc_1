from pydantic import BaseModel, Field
from typing import Optional


class Plateforme(BaseModel):
    id: int
    nom: str


class Genre(BaseModel):
    id: int
    nom: str


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


# =========================
# Authentification
# =========================

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


# =========================
# Jeux vidéo
# =========================

class JeuVideoCreate(BaseModel):
    url: str
    titre: str
    editeur: Optional[str] = None
    description: Optional[str] = None
    score_metacritic: Optional[float] = None
    score_utilisateurs: Optional[float] = None
    plateformes: list[int] = Field(default_factory=list)
    genres: list[int] = Field(default_factory=list)


class JeuVideoUpdate(BaseModel):
    url: Optional[str] = None
    titre: Optional[str] = None
    editeur: Optional[str] = None
    description: Optional[str] = None
    score_metacritic: Optional[float] = None
    score_utilisateurs: Optional[float] = None
    plateformes: Optional[list[int]] = None
    genres: Optional[list[int]] = None