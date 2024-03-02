import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from ipywidgets import interact, widgets
from IPython.display import display
import scipy.stats as stats

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

    # filtre
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
    
    # Extraction de chaque département
    departments = incendi['Departement'].unique()

    plt.figure(figsize = (8, 5))
    
    # Iteration pour avoir une ligne par départements sur le graphique
    for department in departments:
        department_data = incendi[incendi['Departement'] == department]
        # Somme de la surface parcourue en ha de l'incendi pour chaque département par an
        grouped_data = department_data.groupby('Annee')['Surface_parcourue_ha'].sum()
        plt.plot(grouped_data.index, grouped_data.values, label=department)

    plt.title('Evolution of total burnt area by department')
    plt.xlabel('Year')
    plt.ylabel('Burnt Area (ha)')
    plt.legend(title='Department', bbox_to_anchor=(1, 1), loc='upper left')
    plt.savefig(f"{save_path}/Evolution_surface_brulee_par_departement.png", bbox_inches="tight")


# graphique pour montrer la part des surface parcourue en ha parmi l'ensemble des départements par an
def plot_pie_chart_filter(incendi, save_path):
    unique_years = incendi['Annee'].unique()

    # création d'un menu déroulant pour sélectionner l'année
    year_dropdown = widgets.Dropdown(
        options=unique_years,
        description='Select Year:'
    )

    # connecter le menu déroulant au graphique
    interact(update_pie_chart, year=year_dropdown, incendi=widgets.fixed(incendi), unique_years=widgets.fixed(unique_years), save_path=widgets.fixed(save_path))

# fonction qui affiche le graphique selon l'année sélectionné dans le menu déroulant
def update_pie_chart(year, incendi, unique_years, save_path):
    year_data = incendi[incendi['Annee'] == year]
    total_burnt_area_per_department = year_data.groupby('Departement')['Surface_parcourue_ha'].sum()

    plt.figure(figsize=(7, 7))
    plt.pie(total_burnt_area_per_department, labels=total_burnt_area_per_department.index, autopct='%1.1f%%')
    plt.title(f'Total Burnt Area by Department for the Year {year}')
    plt.show()
    
    # Enregistrer tous les graphiques par année
    for year in unique_years:
        plt.savefig(f"{save_path}/Surface_brulee_par_departement_en_{year}.png", bbox_inches="tight")


# Test de la significativité d'une variable catégorielle sur une variable continue avec le Test ANOVA
def test_anova(incendi, category_variable, continuous_variable):
    
    categories = incendi[category_variable].unique()
    anova_data = {category: incendi[continuous_variable][incendi[category_variable] == category] for category in categories}
    anova_result = stats.f_oneway(*[anova_data[category] for category in categories])

    # Affichage
    print(f"\nTest ANOVA de la variable '{category_variable}' sur la variable '{continuous_variable}'.")
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
