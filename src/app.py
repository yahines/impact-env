#import streamlit as st
#st.set_page_config(page_title="Streamlit App", page_icon=":guardsman:", layout="wide")
#st.title("Streamlit App")
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# --- Chargement des données ---
#@st.cache_data
#def load_data():
    #df = pd.read_csv('../data/AGB_CIQUAL_food_products.csv')  # Fichier fusionné contenant nutrition + environnement
    #return df

# --- Chargement des données ---
def load_data():
    df = pd.read_csv("data/AGB_CIQUAL_food_products.csv")  # Fusion nutrition + environnement
    return df

df = load_data()

# --- Titre ---
st.title("🍽️ Sélectionnez vos aliments et découvrez leur empreinte environnementale")

# --- Interface de sélection ---
aliments = df["Nom du Produit en Français"].dropna().unique()
selection = st.multiselect("Choisissez vos aliments :", aliments)

# --- Affichage des résultats ---
if selection:
    df_selection = df[df["Nom du Produit en Français"].isin(selection)]

    # --- Nutrition ---
    st.subheader("Apport nutritionnel pour 100 g (par aliment)")
    st.dataframe(df_selection[[
        "Nom du Produit en Français", "Energie (kcal/100 g)", "Protéines (g/100 g)",
        "Glucides (g/100 g)", "Lipides (g/100 g)", "Fibres alimentaires (g/100 g)"
    ]].set_index("Nom du Produit en Français"))

    # --- Environnement ---
    st.subheader("Impact environnemental (par kg de produit)")
    st.dataframe(df_selection[[
        "Nom du Produit en Français", "Score unique EF", "Changement climatique - émissions fossiles",
        "Utilisation du sol", "Eutrophisation terrestre", "Épuisement des ressources eau"
    ]].set_index("Nom du Produit en Français"))

    # --- Agrégation ---
    st.subheader("Synthèse du menu (somme des apports et impacts)")
    total_nutrition = df_selection[[
        "Energie (kcal/100 g)", "Protéines (g/100 g)", "Glucides (g/100 g)",
        "Lipides (g/100 g)", "Fibres alimentaires (g/100 g)"
    ]].sum()

    total_impact = df_selection[[
        "Score unique EF", "Changement climatique - émissions fossiles",
        "Utilisation du sol", "Eutrophisation terrestre", "Épuisement des ressources eau"
    ]].sum()

    st.write("**Total nutritionnel (pour 100 g de chaque aliment)**")
    st.json(total_nutrition.to_dict())

    st.write("**Total impact environnemental (par kg)**")
    st.json(total_impact.to_dict())

    # --- Visualisations ---
    st.subheader("Visualisation : Apports nutritionnels par aliment")
    fig_nutri = px.bar(df_selection, x="Nom du Produit en Français", y=[
        "Energie (kcal/100 g)", "Protéines (g/100 g)", "Glucides (g/100 g)",
        "Lipides (g/100 g)", "Fibres alimentaires (g/100 g)"
    ], barmode="group")
    st.plotly_chart(fig_nutri)

    st.subheader("Visualisation : Impact environnemental par aliment")
    fig_impact = px.bar(df_selection, x="Nom du Produit en Français", y=[
        "Score unique EF", "Changement climatique - émissions fossiles",
        "Utilisation du sol", "Eutrophisation terrestre", "Épuisement des ressources eau"
    ], barmode="group")
    st.plotly_chart(fig_impact)

    # --- Score global + évaluation ---
    st.subheader("Score combiné nutrition + environnement (note simplifiée)")

    df_selection["Score nutrition"] = df_selection[[
        "Protéines (g/100 g)", "Fibres alimentaires (g/100 g)"
    ]].sum(axis=1) - df_selection[[
        "Glucides (g/100 g)", "Lipides (g/100 g)"
    ]].sum(axis=1)

    df_selection["Score environnement"] = -df_selection["Score unique EF"]
    df_selection["Note globale"] = df_selection["Score nutrition"] + df_selection["Score environnement"]

    # Qualification du score
    def qualifier_score(score):
        if score > 5:
            return "Bon"
        elif score > 0:
            return "Moyen"
        elif score > -20:
            return "Mauvais"
        else:
            return "Critique"

    df_selection["Classement"] = df_selection["Note globale"].apply(qualifier_score)

    st.dataframe(
        df_selection[[
            "Nom du Produit en Français", "Note globale", "Classement"
        ]].sort_values(by="Note globale", ascending=False)
    )

else:
    st.info("Veuillez choisir au moins un aliment pour afficher les résultats.")
