import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# TODO personnalisation pages app 
# 
# st.set_page_config(page_title="Streamlit App", 
#                    page_icon=":guardsman:", 
#                    layout="wide")
# st.title("Streamlit App")

# --- Chargement des données ---
def load_data():
    df = pd.read_csv("data/AGB_CIQUAL_with_menu_category.csv")  # Fusion nutrition + environnement
# TODO 
    dfTypes = pd.read_csv("data/AGB_CIQUAL_food_products 2newcolonns - type_csv.csv")  # Differentes catégorisations d'aliments
    return df, dfTypes
#   return df

# TODO merge datasets
df, dfTypes = load_data()
merged_df = pd.merge(df, dfTypes, 
                    left_on="Sous-groupe d'aliment", 
                    right_on="Sous Groupe Aliment",
                    how='inner')
print(merged_df.shape)
# merged_df.to_csv("data/merged_AGB_CIQUAL.csv", index=False)
# --- Titre ---
st.title("🍽️ Sélectionnez vos aliments et découvrez leur empreinte environnementale")

# --- Interface de sélection ---

# choix 2
# TODO DONE case à cocher avec les 8 elem
# a recuperer du datasets merged
# menus = ["En-cas", "Plat fait maison", "Plat préparé", "Produit céréalier", "Dessert", "Boisson", "Fruit, Légume", "lait"]

menus = merged_df["Appli Web case à cocher"].dropna().unique()
st.subheader("Sélectionnez les éléments de votre menu :")
menu_selection = {}
for menu in menus:
    menu_selection[menu] = st.checkbox(menu)

# TODO cancatener partie colonne/jauge

# Pour afficher les éléments cochés :
selected_menus = [k for k, v in menu_selection.items() if v]
#st.write("Éléments sélectionnés :", selected_menus)
with st.expander("Voir les éléments sélectionnés", expanded=True):
    st.markdown("**Éléments sélectionnés :**")
    if selected_menus:
        st.write(", ".join(selected_menus))
    else:
        st.write("Aucun élément sélectionné.")


# TODO DONE selectionner liste de groupe 
# Pour chaque élément coché, afficher une selectbox avec la liste des groupes d'aliments associés

if selected_menus:
    for menu in selected_menus:
        with st.expander("Voir les éléments sélectionnés", expanded=True):
            # Filtrer les groupes d'aliments correspondant à ce menu
            groupes = merged_df.loc[merged_df["Appli Web case à cocher"] == menu, "Groupe d'aliment"].dropna().unique()
            if len(groupes) > 0:
                groupe_choisi = st.selectbox(
                    f"Sélectionnez un groupe d'aliment pour {menu} :", groupes, key=f"groupe_{menu}"
                )
                # Afficher la liste des sous-groupes d'aliments pour le groupe choisi
                sous_groupes = merged_df[
                    (merged_df["Appli Web case à cocher"] == menu) &
                    (merged_df["Groupe d'aliment"] == groupe_choisi)
                ]["Sous-groupe d'aliment"].dropna().unique()
                if len(sous_groupes) > 0:
                    sous_groupe_choisi = st.selectbox(
                        f"Sélectionnez un sous-groupe d'aliment pour {menu} - {groupe_choisi} :", 
                        sous_groupes, 
                        key=f"sous_groupe_{menu}_{groupe_choisi}"
                    )
                    # Sélectionner le Type d'aliment pour chaque Sous-groupe d'aliment
                    types_aliment = merged_df[
                        (merged_df["Appli Web case à cocher"] == menu) &
                        (merged_df["Groupe d'aliment"] == groupe_choisi) &
                        (merged_df["Sous-groupe d'aliment"] == sous_groupe_choisi)
                    ]["Type d'aliment"].dropna().unique()
                    if len(types_aliment) > 0:
                        type_aliment_choisi = st.selectbox(
                            f"Sélectionnez un type d'aliment pour {menu} - {groupe_choisi} - {sous_groupe_choisi} :",
                            types_aliment,
                            key=f"type_{menu}_{groupe_choisi}_{sous_groupe_choisi}"
                        )
                        # Sélectionner le Sous type d'aliment pour chaque type_aliment_choisi
                        sous_types_aliment = merged_df[
                            (merged_df["Appli Web case à cocher"] == menu) &
                            (merged_df["Groupe d'aliment"] == groupe_choisi) &
                            (merged_df["Sous-groupe d'aliment"] == sous_groupe_choisi) &
                            (merged_df["Type d'aliment"] == type_aliment_choisi)
                        ]["Sous type d'aliment"].dropna().unique()
                        if len(sous_types_aliment) > 0:
                            sous_type_aliment_choisi = st.selectbox(
                                f"Sélectionnez un sous type d'aliment pour {menu} - {groupe_choisi} - {sous_groupe_choisi} - {type_aliment_choisi} :",
                                sous_types_aliment,
                                key=f"sous_type_{menu}_{groupe_choisi}_{sous_groupe_choisi}_{type_aliment_choisi}"
                            )
                            # Sélectionner le produit pour chaque sous_type_aliment_choisi
                            produits_sous_type = merged_df[
                                (merged_df["Appli Web case à cocher"] == menu) &
                                (merged_df["Groupe d'aliment"] == groupe_choisi) &
                                (merged_df["Sous-groupe d'aliment"] == sous_groupe_choisi) &
                                (merged_df["Type d'aliment"] == type_aliment_choisi) &
                                (merged_df["Sous type d'aliment"] == sous_type_aliment_choisi)
                            ]["Nom du Produit en Français"].dropna().unique()
                            if len(produits_sous_type) >= 0:
                                # Récupérer les scores EF pour chaque produit
                                produits_scores = merged_df[
                                    merged_df["Nom du Produit en Français"].isin(produits_sous_type)
                                ][["Nom du Produit en Français", "Score unique EF"]].drop_duplicates()
                                # Trier par Score unique EF décroissant
                                produits_scores = produits_scores.sort_values("Score unique EF", ascending=False)
                                produits_sorted = produits_scores["Nom du Produit en Français"].tolist()
                                # Afficher le score dans la selectbox
                                produit_labels = [
                                    f"{prod} (Score EF: {score:.2f})"
                                    for prod, score in zip(
                                        produits_scores["Nom du Produit en Français"],
                                        produits_scores["Score unique EF"]
                                    )
                                ]
                                produit_choisi_sous_type = st.selectbox(
                                    f"Sélectionnez un produit pour {menu} - {groupe_choisi} - {sous_groupe_choisi} - {type_aliment_choisi} - {sous_type_aliment_choisi} :",
                                    options=produit_labels,
                                    key=f"produit_{menu}_{groupe_choisi}_{sous_groupe_choisi}_{type_aliment_choisi}_{sous_type_aliment_choisi}"
                                )
                            else:
                                produit_choisi_sous_type = None
                        else:
                            sous_type_aliment_choisi = None
                    else:
                        type_aliment_choisi = None
                else:
                    sous_groupe_choisi = None

                
                # Optionnel : afficher les produits de ce groupe
#                 produits = merged_df[
#                     (merged_df["Appli Web case à cocher"] == menu) &
#                     (merged_df["Groupe d'aliment"] == groupe_choisi)
#                 ]["Nom du Produit en Français"].dropna().unique()
#                 if len(produits) > 0:
#                     produit_choisi = st.selectbox(
#                         f"Sélectionnez un produit pour {menu} - {groupe_choisi} :", produits, key=f"produit_{menu}"
#                     ) 
else:
    st.info("Sélectionnez au moins un élément de menu pour afficher les groupes d'aliments.")

# TODO selectionner liste de sous groupe
# TODO selectionner typpe et sous types et pas sou grp si fruit si viande

# adapter la colonn e de filtrage en fonction de la case à cocher 
# par exp si boisson je passe a filtrage ss grp ensuite type

# TODO selectionner liste des type de cuisson
# TODO propose liste des produits filtre si possible avec le score unique EFdans la select box dans loredre decroissant
# TODO on affiche tt les produit selectionnes avec le score unique EF classe et somme des apports nutritionnels
# TODO avoir pour laffichage avec le sort