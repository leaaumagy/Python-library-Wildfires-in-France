import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from ipywidgets import interact, widgets
from IPython.display import display
import scipy.stats as stats
import os 
import argparse


def incendi_data(filename):

    # Importation de la base
    incendi = pd.read_csv(filename, delimiter=';', skiprows=2)

    # Renommer les variables
    variables = {
        'Année': 'Annee',
        'Numéro': 'Numero',
        'Type de feu': 'Type_de_feu',
        'Département': 'Departement',
        'Code INSEE': 'Code_INSEE',
        'Lieu-dit': 'Lieu_dit',
        'Code du carreau DFCI': 'Code_carreau_DFCI',
        'Origine de l\'alerte': 'Origine_alerte',
        'Surface parcourue (m2)': 'Surface_parcourue_m2'
    }

    incendi = incendi.rename(columns = variables)

    # Utiliser Numero comme Index
    incendi.set_index("Numero", inplace=True)

    # Nettoyage des variables "Commune" et "Lieu_dit", on remplce les villes et adresse NA par "inconnu"
    incendi['Commune'].fillna('Inconnu', inplace=True)
    incendi['Lieu_dit'].fillna('Inconnu', inplace=True)
    incendi["Commune"] = incendi["Commune"].str.title() # majuscule
    incendi["Lieu_dit"] = incendi["Lieu_dit"].str.title() # majuscule

    # Nettoyer la variable "alerte" qui contient la date et l'heure de l'alerte
    incendi[['Date_alerte', 'Heure_alerte']] = incendi['Alerte'].str.split(' ', expand=True) # on sépare la date et l'heure dans deux variables
    incendi.drop(columns=['Alerte'], inplace = True) # on supprime la variable "Alerte"

    # Convertir les colonnes "Date" et "Heure" en type datetime
    incendi['Date_alerte'] = pd.to_datetime(incendi['Date_alerte'])
    incendi['Date_alerte'] = incendi['Date_alerte'].dt.strftime('%Y-%m-%d')
    incendi['Heure_alerte'] = pd.to_datetime(incendi['Heure_alerte'], format='%H:%M:%S').dt.time

    # Nettoyage de la variable "Origine_alerte", il n'existe pas de valeur 0 mais des NA, donc on remplace NA par 0
    incendi["Origine_alerte"].fillna(0, inplace=True)
    # Convertir la varialbe "Origine_altere" en nombre entier
    incendi["Origine_alerte"] = incendi["Origine_alerte"].astype(int)
    
    # création d'une variable où on convertie la colonne "surface_parcourue_m2" en ha
    incendi['Surface_parcourue_ha'] = incendi['Surface_parcourue_m2'] / 10000

    return incendi

# Compter le nombre d'incendie selon un filter sur les années et sur les départements
def count_fires(incendi, years, departments = None):

    # S'il n'y a pas de département dans la liste alors on les affiche tous
    if departments is None or not departments:
        departments = incendi['Departement'].unique()
        
    # Filtre les données en fonction des années et, si fournis, des départements
    condition = incendi['Annee'].isin(years) & incendi['Departement'].isin(departments)
    filtered_incendi = incendi[condition]
    
    number_fire = filtered_incendi.groupby(['Annee', 'Departement']).size().unstack()
    return number_fire

# Compter la surface brulée parcourue selon un filter sur les années et sur les départements
def sum_burnt_area(incendi, years, departments=None):

    # S'il n'y a pas de département dans la liste alors on les affiche tous
    if departments is None or not departments:
        departments = incendi['Departement'].unique()
        
    # Filtre les données en fonction des années et, si fournis, des départements
    condition = incendi['Annee'].isin(years) & incendi['Departement'].isin(departments)
    filtered_incendi = incendi[condition]

    total_burnt_area = filtered_incendi.groupby(['Annee', 'Departement'])['Surface_parcourue_ha'].sum().round(2).unstack()
    return total_burnt_area

# Statistiques sur la surface brulée parcourue selon un filter sur les années et sur les départements
def stats_burnt_area(incendi, years, departments=None):
    
    # S'il n'y a pas de département dans la liste alors on les affiche tous
    if departments is None or not departments:
        departments = incendi['Departement'].unique()
        
    # Filtre les données en fonction des années et, si fournis, des départements
    condition = incendi['Annee'].isin(years) & incendi['Departement'].isin(departments)
    filtered_incendi = incendi[condition]

    stats = filtered_incendi.groupby(['Annee', 'Departement'])['Surface_parcourue_ha'].describe().round(3).unstack()
    return stats

def plot_burnt_area(incendi, save_path):

    # Create the directory if it doesn't exist
    os.makedirs(save_path, exist_ok = True)
    
    # Extraction de chaque département
    departments = incendi['Departement'].unique()

    plt.figure(figsize = (8, 5))
    
    # Iteration pour avoir une ligne par départements sur le graphique
    for department in departments:
        department_data = incendi[incendi['Departement'] == department]
        # Somme de la surface parcourue en ha de l'incendi pour chaque département par an
        grouped_data = department_data.groupby('Annee')['Surface_parcourue_ha'].sum()
        plt.plot(grouped_data.index, grouped_data.values, label = department)

    plt.title('Evolution of total burnt area by department')
    plt.xlabel('Year')
    plt.ylabel('Burnt Area (ha)')
    plt.legend(title='Department', bbox_to_anchor=(1, 1), loc='upper left')

    # Enregistrer le graphique
    plt.savefig(f"{save_path}/Evolution_surface_brulee_par_departement.png", bbox_inches="tight")
    plt.close()

def pie_charts_per_year(incendi, save_path):
    unique_years = incendi['Annee'].unique()

    # S'assurer que le répertoire de sauvegarde existe
    os.makedirs(save_path, exist_ok=True)

    for year in unique_years:
        year_data = incendi[incendi['Annee'] == year]
        total_burnt_area_per_department = year_data.groupby('Departement')['Surface_parcourue_ha'].sum()
 
        plt.figure(figsize=(7, 7))
        plt.pie(total_burnt_area_per_department, labels=total_burnt_area_per_department.index, autopct='%1.1f%%')
        plt.title(f'Total Burnt Area by Department for the Year {year}')
        
        # Enregistrez le graphique dans le répertoire avec le nom spécifique
        chart_filename = os.path.join(save_path, f"Surface_brulee_par_departement_en_{year}.png")
        plt.savefig(chart_filename, bbox_inches="tight")
        plt.close()  

# Test de la significativité d'une variable catégorielle sur une variable continue avec le Test ANOVA
def test_anova(incendi, category_variable, continuous_variable):
    
    categories = incendi[category_variable].unique()
    anova_data = {category: incendi[continuous_variable][incendi[category_variable] == category] for category in categories}
    anova_result = stats.f_oneway(*[anova_data[category] for category in categories])

    # Affichage
    print("F-statistic:", anova_result.statistic.round(4))
    print("P-value:", anova_result.pvalue.round(4))

    # On récupère la p-value de la variable pour tester la significativité
    anova_test = anova_result.pvalue   
    
    # Test du seuil de significativité
    alpha = 0.05 #seuil de significativité
    if anova_test < alpha:
        print(f"La variable '{category_variable}' a un impact significatif sur la variable '{continuous_variable}' pour un seuil de significativité de {alpha}.")
    else:
        print(f"La variable '{category_variable}' n'a pas un impact significatif sur la variable '{continuous_variable}' pour un seuil significativité de {alpha}.")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_base", help="Entrez le chemin de la base de donnée")
    ap.add_argument("--input_year", help="Enter une ou plusieurs années séparées par des virgules")
    ap.add_argument("--input_department", help="Enter un ou plusieurs départements séparés par des virgules")
    ap.add_argument("--input_savepath", help="Entrer un chemin où enregistrer le graphique")
    ap.add_argument("--input_category_variable", nargs='+', help="Entrer le nom d'une variable catégorielle de la base de donnée")
    ap.add_argument("--input_continuous_variable", help="Entrer le nom d'une variable continue de la base de donnée")
    args = vars(ap.parse_args())

    # Convertir les arguments en listes
    input_year = args["input_year"].split(",") if args["input_year"] else None
    input_department = args["input_department"].split(",") if args["input_department"] else None

    # Convertir les années en entiers
    input_year = [int(year) for year in input_year] if input_year else None
    
    # base de donnée incendi_data nettoyée
    incendi_df = incendi_data(args["input_base"])

    # count_fires
    number_fire = count_fires(incendi_df, input_year, input_department)
    print("\nCount of fires:")
    print(number_fire)

    # sum_burnt_area
    sum_burnt_area_result = sum_burnt_area(incendi_df, input_year, input_department)
    print("\nTotal burnt area:")
    print(sum_burnt_area_result)

    # stats_burnt_area
    statistics_burnt_area = stats_burnt_area(incendi_df, input_year, input_department)
    print("\nBurnt Area Statistics:")
    print(statistics_burnt_area)

    # graphique de l'évolution des surface brûlée par département et par année
    save_path = args["input_savepath"]  # Corrected variable name
    plot_burnt_area(incendi_df, save_path)  # Pass correct variable
    print("Le graphique 'plot_burnt_area' a bien été sauvegardé")

    # Graphique pie chart selon l'année
    pie_charts_per_year(incendi_df, save_path)
    print("Les graphiques sur la part des surfaces brûlées par département depuis l'année 2000 ont bien été sauvegardés")

    # Test ANOVA
    for input_category_variable in args["input_category_variable"]:
        print(f"\nTest ANOVA de la variable '{input_category_variable}' sur la variable '{args['input_continuous_variable']}':")
        test_anova(incendi_df, input_category_variable, args["input_continuous_variable"])

if __name__ == "__main__":
    main()