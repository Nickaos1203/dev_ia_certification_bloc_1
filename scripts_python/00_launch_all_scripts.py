# a faire !!!
import os

# Création des tables
os.system("python script_creation_tables.py")


# Chargement des données dans les tables
os.system("python script_clean_videogames_datas.py")
os.system("python script_loan_videogames_datas.py")
os.system("python script_loan_trees_datas.py")
os.system("python script_loan_salary_datas.py")

