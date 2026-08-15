from pydantic import BaseModel
from typing import List, Annotated, Optional

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
    plateformes: list[str] = []
    genres: list[str] = []