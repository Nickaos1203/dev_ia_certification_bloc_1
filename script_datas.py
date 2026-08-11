import psycopg2
import json
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
import os

# Chargement des variables secrètes
load_dotenv()

# tests des import dotenv
print("database =" + os.getenv("DB_NAME"))
print("user =" + os.getenv("DB_USER"))
print("password =" + os.getenv("DB_PASSWORD"))


# Connexion avec la base de données'toque_et_chef'
conn = psycopg2.connect(
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    host='localhost',
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

# Création du curseur
cur = conn.cursor()

# Requête SQL pour créer une table dans postgreSQL
sql = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    age INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Exécution
cur.execute(sql)

# Validation de la transaction
conn.commit()

print("Table 'users' créée avec succès.")

# Fermeture
cur.close()
conn.close()