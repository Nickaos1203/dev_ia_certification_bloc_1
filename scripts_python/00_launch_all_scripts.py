# script d'automatisation des étapes de collecte et de nettoyage des données, de création des tables et de chargement des données  
import os


# Lancement du scraping de "metacritic.com" et nettoyage
os.system(
    "cd /d ../web_scraping && "
    "scrapy crawl videogames_spider -O ../scripts_python/videogames_dataset.json"
)
os.system("python script_clean_videogames_datas.py")


# Collecte des données de l'API
os.system("python script_api_extract_datas.py")


# Collecte des données sur BigQUery
os.system("python script_big_data_extract_datas.py")


# Création des tables
os.system("python script_creation_tables.py")


# Chargement des données dans PostgreSQL
os.system("python script_loan_videogames_datas.py")
os.system("python script_loan_trees_datas.py")
os.system("python script_loan_salary_datas.py")