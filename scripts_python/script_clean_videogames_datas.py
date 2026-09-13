import pandas as pd


# CHARGEMENT DU FICHIER JSON
df = pd.read_json("videogames_dataset.json")



# Suppression des espaces en début et fin de chaîne
colonnes_texte = ["url", "titre", "editeur", "genre", "description"]

for colonne in colonnes_texte:
    df[colonne] = df[colonne].apply(
        lambda x: x.strip() if isinstance(x, str) else None
    )


# Gestion des valeurs nulles : Conversion des valeurs absentes en None
df = df.where(pd.notna(df), None)


# Sur la liste des plateformes, suppression :
# - des valeurs nulles
# - des chaînes vides
# - des espaces inutiles
# - des doublons
df["plateformes"] = df["plateformes"].apply(
    lambda liste: list(dict.fromkeys(
        [
            plateforme.strip()
            for plateforme in liste
            if isinstance(plateforme, str)
            and plateforme.strip() != ""
        ]
    ))
    if isinstance(liste, list)
    else []
)


# Contrôle des champs obligatoires : L'URL et le titre doivent être présents
df = df[df["url"].notna() & df["titre"].notna()]


# L'URL doit commencer par http:// ou https://
df["url_valide"] = (df["url"].str.match(r"^https?://[^\s]+$", na=False))


# Suppression des URL invalides
df = df[df["url_valide"]]


# Suppression de la colonne temporaire
df.drop(columns=["url_valide"], inplace=True)


# conversion des scores en type float
df["score_metacritic"] = pd.to_numeric(
    df["score_metacritic"],
    errors="coerce"
)

df["score_utilisateurs"] = pd.to_numeric(
    df["score_utilisateurs"],
    errors="coerce"
)


# Validation des cores :
# - Metacritic : entre 0 et 100
# - Utilisateurs : entre 0 et 10
df = df[
    (df["score_metacritic"].isna() | df["score_metacritic"].between(0, 100))
    &
    (df["score_utilisateurs"].isna() | df["score_utilisateurs"].between(0, 10))]


# Gestion des doublons : Les URL servent à identifier les doublons
df = df.drop_duplicates(subset="url", keep="first")


# Normalisation : Transformation du genre en liste
df["genre"] = df["genre"].apply(
    lambda genre: [genre]
    if isinstance(genre, str) and genre.strip() != ""
    else []
)


# réinitialisation des index
df.reset_index(drop=True, inplace=True)


# affichage des résultats
print(df.head())


# génération du fichier json nettoyé
df.to_json(
    "videogames_dataset_clean.json",
    orient="records",
    force_ascii=False,
    indent=4
)