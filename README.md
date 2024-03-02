# Projet PrometheusLib

Ce projet contient une bibliothèque Python pour l'analyse des incendies en France.

## Instructions d'exécution

1. **Cloner le dépôt :**
   `git clone https://github.com/leaaumagy/projet_fire.git
   cd projet_fire`

2. **Créer un environnement virtuel :**
   `python3 -m venv venv
   source venv/bin/activate  # Sur Windows, utilisez .\venv\Scripts\activate`

3. **Installer les packages :**
   `pip install -r requirements.txt`

4. **Exécuter le script principal : :**
   `python3 Projet_argparse.py --input_base "./liste_incendies_du_12_08_2022.csv" --input_year "2019,2020,2021,2022" --input_department "" --input_savepath "./Graphics" --input_category_variable "Origine_alerte" "Departement" --input_continuous_variable "Surface_parcourue_ha"`

Cet exemple de script permettra de visualiser les incendis sur l'ensembles des départements de la base de données pour l'année 2019, 2020, 2021 et 2022. 
Si `--input_year` est vide alors cela excécutera l'algorithme sur l'ensemble de la période. 
Si vous souhaitez avoir une analyse sur seulement un départemenet il suffit de renseigner `--input_department "13"`, par exemple.
