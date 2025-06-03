
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Chargement des données
df = pd.read_csv("data/AGB_CIQUAL_with_menu_category.csv")

st.title("🍽️ Simulateur de menu alimentaire durable et équilibré")

# --- Sélection utilisateur ---
cat_menu = st.selectbox("Choisissez une catégorie de menu :", sorted(df["Catégorie menu"].dropna().unique()))
mode_prep = st.selectbox("Mode de préparation :", sorted(df["Préparation"].dropna().unique()))
df_filtre = df[(df["Catégorie menu"] == cat_menu) & (df["Préparation"] == mode_prep)]

# --- Vue globale EF ---
st.subheader("📊 Impact environnemental global (Score Unique EF)")
agg = df_filtre.groupby("Type d'aliment")["Score unique EF"].agg(["min", "median", "max"]).reset_index()

if agg.shape[0] > 1:
    for _, row in agg.iterrows():
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[row["min"], row["median"] - row["min"], row["max"] - row["median"]],
            y=[row["Type d'aliment"]],
            orientation='h',
            marker=dict(color=["#A8DADC", "#457B9D", "#1D3557"]),
            hoverinfo="x+y"
        ))
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)
else:
    st.warning("Pas assez de produits pour afficher min/médiane/max.")

# --- Détails par type d'aliment ---
st.subheader("🔎 Explorer les produits disponibles")
if not df_filtre.empty:
    type_aliments = df_filtre["Type d'aliment"].dropna().unique()
    if len(type_aliments) > 0:
        selected_type = st.selectbox("Choisissez un type d’aliment :", sorted(type_aliments))
        produits = df_filtre[df_filtre["Type d'aliment"] == selected_type].copy()

        # Calcul score nutrition simplifié
        produits["Score nutrition"] = (
            produits[["Protéines (g/100 g)", "Fibres alimentaires (g/100 g)"]].sum(axis=1)
            - produits[["Glucides (g/100 g)", "Lipides (g/100 g)"]].sum(axis=1)
        )
        produits["Note globale"] = produits["Score nutrition"] - produits["Score unique EF"]

        st.dataframe(produits[[
            "Nom du Produit en Français", "Préparation", "Score unique EF",
            "Score nutrition", "Note globale"
        ]].sort_values("Note globale", ascending=False))
    else:
        st.info("Aucun type d'aliment disponible pour ces filtres.")
else:
    st.warning("Aucun produit trouvé pour cette catégorie + mode de préparation.")
