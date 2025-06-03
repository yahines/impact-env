import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Simulation de tes données pour une catégorie
df = pd.read_csv("data/AGB_CIQUAL_food_products.csv")  # Doit contenir 'Catégorie', 'Score unique EF'

# --- Interface de sélection ---
# aliments = df["Nom du Produit en Français"].dropna().unique()
# aliments_entree = df[df["Groupe d'aliment"] == "Entrée"]["Nom du Produit en Français"].dropna().unique()
# print(aliments.len())

# entree = st.selectbox("Choisissez vos aliments :", aliments_entree)  
# plat = st.selectbox("Choisissez vos aliments :", aliments)
# fromage = st.selectbox("Choisissez vos aliments :", aliments)
# desset = st.selectbox("Choisissez vos aliments :", aliments)
# boisson = st.selectbox("Choisissez vos aliments :", aliments)


# Agrégation des scores EF
agg_df = df.groupby("Groupe d'aliment")["Score unique EF"].agg(['min', 'median', 'max']).reset_index()

st.title("🌿 Impact environnemental des catégories alimentaires")
st.write("Affichage min / médiane / max du Score Unique EF par catégorie")

# Pour chaque ligne, une barre horizontale avec les 3 valeurs
for index, row in agg_df.iterrows():
    cat = row["Groupe d'aliment"]
    min_val, med_val, max_val = row['min'], row['median'], row['max']

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[min_val, med_val, max_val],
        y=[cat, cat, cat],
        orientation='h',
        marker_color=["#A8DADC", "#457B9D", "#1D3557"],
        name="Min / Médiane / Max",
        customdata=[["Min"], ["Médiane"], ["Max"]],
        hovertemplate='%{customdata[0]}: %{x}<extra></extra>',
        showlegend=False
    ))



    fig.update_layout(
        height=70,
        margin={"l": 50, "r": 10, "t": 10, "b": 10},
        xaxis={"title": 'Score Unique EF', "showgrid": False},
        yaxis={"showticklabels": True},
    )
    st.plotly_chart(fig, use_container_width=True)


#import streamlit as st
#st.set_page_config(page_title="Streamlit App", page_icon=":guardsman:", layout="wide")
#st.title("Streamlit App")
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# appli multipages 
# st.set_page_config(page_title="Streamlit App", 
#                    page_icon=":guardsman:", 
#                    layout="wide")
# st.title("Streamlit App")

# --- Chargement des données ---
def load_data():
    df = pd.read_csv("data/AGB_CIQUAL_food_products.csv")  # Fusion nutrition + environnement
    return df

df = load_data()

# --- Titre ---
st.title("🍽️ Sélectionnez vos aliments et découvrez leur empreinte environnementale")



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

