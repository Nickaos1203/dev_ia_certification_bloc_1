# Projet "dev_ia_certification_bloc_1"

# I. Présentation du projet



# II. Architecture générale

```text
dev_ia_certification_bloc_1/
│
├── api/
│   ├── app/
│       ├── __init__.py
│       ├── auth.py
│       ├── main.py
│       ├── schemas.py
│       └── test.py
│
├── scripts_python/
│   ├── 00_launch_all_scripts.py
│   ├── salaries.json
│   ├── script_api_extract_datas.py
│   ├── script_big_data_extract_datas.py
│   ├── script_clean_videogames_datas.py
│   ├── script_creation_tables.py
│   ├── script_load_salaries_datas.py
│   ├── script_load_trees_datas.py
│   ├── script_load_videogames_datas.py
│   ├── tree_species.json
│   ├── videogames_dataset_clean.json
│   └── videogames_dataset.json
│
├── web_scraping/
│   │
│   ├── web_scraping/
│   │   ├── spiders/
│   │   │   ├── __init__.py
│   │   │   └── videogames_spider.py
│   │   │
│   │   ├── __init__.py
│   │   ├── items.py
│   │   ├── middlewares.py
│   │   ├── pipelines.py
│   │   └── settings.py
│   │
│   └── scrapy.cfg
│
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

# III. Rôle des principaux répertoires et fichiers

| Répertoire / fichier | Rôle |
|---|---|
| `api/` | Contient l'API REST développée avec **FastAPI** |
| `api/app/main.py` | Point d'entrée de l'API et définition des endpoints |
| `api/app/auth.py` | Gestion de l'authentification et de la sécurité |
| `api/app/schemas.py` | Définition des schémas de données avec Pydantic |
| `api/requirements.txt` | Dépendances spécifiques à l'API |
| `scripts_python/` | Scripts Python permettant l'extraction, le nettoyage, le chargement des données, ainsi que la création des tables|
| `script_clean_videogames_datas.py` | Nettoyage et validation des données de jeux vidéo |
| `script_api_extract_datas.py` | Extraction de données via une API |
| `script_big_data_extract_datas.py` | Extraction de données (table tree_species) à partir d'une base de données publique BigQuery (GCP) |
| `script_creation_tables.py` | Création des tables de la base de données |
| `script_load_*.py` | Chargement des différents jeux de données en base |
| `web_scraping/` | Projet de collecte de données avec **Scrapy** |
| `web_scraping/spiders/` | Contient les spiders Scrapy |
| `videogames_spider.py` | Spider dédié à la collecte des données de jeux vidéo via "metacritic.com"|
| `items.py` | Définition des structures de données Scrapy |
| `pipelines.py` | Traitement des données récupérées par Scrapy |
| `middlewares.py` | Middlewares Scrapy |
| `settings.py` | Configuration du projet Scrapy |
| `.env` | Variables d'environnement et secrets |
| `README.md` | Documentation du projet |
| `requirements.txt` | Dépendances Python du projet |



# IV. Lancement du projet

## 1. Prérequis

Avant d'installer le projet, vérifier que les éléments suivants sont installés :

- Python 3.10 ou supérieur
- Git
- pip

Vérifier les versions installées :

```bash
python --version
git --version
pip --version
```

## 2. Installation du projet

- Cloner le repository :
```bash
git clone https://github.com/Nickaos1203/dev_ia_certification_bloc_1.git
```

- Se placer dans le projet :
```bash
cd dev_ia_certification_bloc_1
```

- Créer l'environnement virtuel :
```bash
python -m venv .venv
```

- Activer l'environnement sous Windows :
```bash
.venv\Scripts\activate
```

- Mettre pip à jour :
```bash
python -m pip install --upgrade pip
```

- Installer les dépendances :
```bash
pip install -r requirements.txt
```

## 3. Configuration des variables secrètes

- Créer le fichier .env :
```bash
touch .env
```

- Ajouter dans le fichier .env les variables de connexion à PostgreSQL :
```
DB_NAME=<nom_de_la_base>
DB_USER=<nom_utilisateur>
DB_PASSWORD=<mot_de_passe>
DB_HOST=localhost
DB_PORT=5432
```

## 4. Création des tables et ETL

- Se placer dans le dossier scripts_python :
```bash
cd scripts_python
```

- Lancer le script 00_launch_all_scripts.py :
```bash
python 00_launch_all_scripts.py
```



# Concernant l'extraction de données par scraping

- placez-vous dans le dossier web_scraping (le 1er dossier)

```bash
cd web_scraping
```
- lancez l'extraction de données avec la commande suivante. Un fichier json comprenant les données collectées sera créé dans le dossier scripts_python : `dev_ia_certification_bloc_1/scripts_python/videogames_dataset.json`
```bash
scrapy crawl videogames_spider -O ../scripts_python/videogames_dataset.json
```

- lancez le script python de nettoyage des données. Un fichier json avec les données nettoyées sera générée dans le dossier scripts_python : `dev_ia_certification_bloc_1/scripts_python/videogames_dataset_clean.json`