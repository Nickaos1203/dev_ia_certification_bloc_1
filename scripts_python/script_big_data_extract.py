from google.cloud import bigquery
import pandas as pd


# ==========================================================
# 1. CONNEXION À BIGQUERY
# ==========================================================

client = bigquery.Client()


# ==========================================================
# 2. EXTRACTION DE LA TABLE tree_species
# ==========================================================

query = """
SELECT
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
FROM `bigquery-public-data.new_york.tree_species`
"""

df = client.query(query).to_dataframe()

print(f"Nombre de lignes extraites : {len(df)}")


# ==========================================================
# 3. NETTOYAGE DES DONNÉES
# ==========================================================

# Colonnes contenant des données textuelles
string_columns = [
    "species_scientific_name",
    "species_common_name",
    "form",
    "growth_rate",
    "fall_color",
    "environmental_tolerances",
    "location_tolerances",
    "notes_suggested_cultivars",
    "tree_size",
    "comments"
]


# ----------------------------------------------------------
# 3.1 Suppression des espaces inutiles
# ----------------------------------------------------------

for column in string_columns:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
    )


# ----------------------------------------------------------
# 3.2 Remplacement des chaînes vides par des valeurs nulles
# ----------------------------------------------------------

for column in string_columns:
    df[column] = df[column].replace(
        r"^\s*$",
        pd.NA,
        regex=True
    )


# ----------------------------------------------------------
# 3.3 Suppression des doublons
# ----------------------------------------------------------

df = df.drop_duplicates()


# ----------------------------------------------------------
# 3.4 Suppression des lignes sans nom scientifique
# ----------------------------------------------------------

df = df.dropna(
    subset=["species_scientific_name"]
)


# ==========================================================
# 4. INFORMATIONS APRÈS NETTOYAGE
# ==========================================================

print(f"Nombre de lignes après nettoyage : {len(df)}")

print("\nDonnées nettoyées :")
print(df)


# ==========================================================
# 5. EXPORT AU FORMAT JSON
# ==========================================================

df.to_json(
    "tree_species.json",
    orient="records",
    force_ascii=False,
    indent=4
)

print("\nFichier tree_species.json créé avec succès.")