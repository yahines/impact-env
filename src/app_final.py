
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Charger les données
df = pd.read_csv("data/AGB_CIQUAL_with_menu_category.csv")

# Nettoyer les colonnes utilisées
nutr_cols = [
    "Energie (kcal/100 g)", "Protéines (g/100 g)", 
    "Glucides (g/100 g)", "Lipides (g/100 g)"
]
df = df.dropna(subset=["Nom du Produit en Français", "Score unique EF"] + nutr_cols)

# Interface Streamlit
st.title("🌱 Analyse Environnementale et Nutritionnelle")

produits = df["Nom du Produit en Français"].unique()
choix = st.selectbox("Choisissez un produit :", sorted(produits))

# Produit sélectionné
prod_init = df[df["Nom du Produit en Français"] == choix].iloc[0]
categorie_menu = prod_init["Catégorie menu"]

# Alternative recommandée dans la même catégorie menu
df_categorie = df[df["Catégorie menu"] == categorie_menu]
df_alternatives = df_categorie[df_categorie["Nom du Produit en Français"] != choix]
prod_alt = df_alternatives.sort_values("Score unique EF").iloc[0]

# Jauge Score EF
st.subheader("🎯 Réduction d'impact")

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=prod_alt["Score unique EF"],
    delta={'reference': prod_init["Score unique EF"], 'relative': True, 'valueformat': '.2%'},
    title={'text': "Score unique EF (Alternative)"},
    gauge={
        'axis': {'range': [0, max(df["Score unique EF"].max(), 0.5)]},
        'bar': {'color': "green"},
    }
))
st.plotly_chart(fig_gauge)

# Comparaison nutritionnelle
st.subheader("📊 Apports nutritionnels comparés")

trace1 = go.Bar(name='Produit initial', x=nutr_cols, y=[prod_init[col] for col in nutr_cols])
trace2 = go.Bar(name='Alternative proposée', x=nutr_cols, y=[prod_alt[col] for col in nutr_cols])

fig_nutri = go.Figure(data=[trace1, trace2])
fig_nutri.update_layout(barmode='group', title="Comparaison nutritionnelle (pour 100g)")

st.plotly_chart(fig_nutri)

# Résumé sous forme de tableau
st.subheader("📋 Détails comparatifs")

resume = pd.DataFrame({
    "Type": ["Produit initial", "Alternative proposée"],
    "Nom": [prod_init["Nom du Produit en Français"], prod_alt["Nom du Produit en Français"]],
    "Score unique EF": [prod_init["Score unique EF"], prod_alt["Score unique EF"]],
    "Energie (kcal/100 g)": [prod_init["Energie (kcal/100 g)"], prod_alt["Energie (kcal/100 g)"]],
    "Protéines (g/100 g)": [prod_init["Protéines (g/100 g)"], prod_alt["Protéines (g/100 g)"]],
    "Glucides (g/100 g)": [prod_init["Glucides (g/100 g)"], prod_alt["Glucides (g/100 g)"]],
    "Lipides (g/100 g)": [prod_init["Lipides (g/100 g)"], prod_alt["Lipides (g/100 g)"]]
})

st.dataframe(resume.set_index("Type"))
