import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# --- Chargement des données ---
merged_df = pd.read_csv("data/AGB_CIQUAL_food_products_category_type.csv")

# --- Titre ---
st.title("🍽️ Sélectionnez vos aliments et découvrez leur empreinte environnementale",)

# --- Interface de sélection ---
# TODO DONE case à cocher avec les 8 elem
st.subheader("Sélectionnez les éléments de votre menu :")
selected_menus = {}
menus = merged_df["Catégorie"].dropna().unique()
selected_menus = st.segmented_control("éléments menu", menus.tolist(), selection_mode="multi")
# st.markdown(f"Éléments sélectionnés : {selected_menus}.")

# TODO cancatener partie colonne/jauge

# TODO DONE input pour liste de groupes confondus 
if selected_menus:
    st.subheader("Sélectionnez un ou plusieurs groupes d'aliments :")
    groupes = merged_df[merged_df["Catégorie"].isin(selected_menus)]["Groupe d'aliment"].dropna().unique()
    selected_groupes = st.segmented_control("Groupes d'aliments", groupes.tolist(), selection_mode="multi")
    # st.markdown(f"Groupes sélectionnés : {selected_groupes}.")

# TODO input pour liste de types confondus 
    if selected_groupes:
        st.subheader("Sélectionnez un ou plusieurs types d'aliments :")
        types = merged_df[
            (merged_df["Catégorie"].isin(selected_menus)) &
            (merged_df["Groupe d'aliment"].isin(selected_groupes))
        ]["Type d'aliment"].dropna().unique()
        selected_types = st.segmented_control("Types d'aliments", types.tolist(), selection_mode="multi")
        # st.markdown(f"Types sélectionnés : {selected_types}.")

# TODO selectionner dans liste des type de cuisson
        if selected_types:
            st.subheader("Sélectionnez un ou plusieurs modes de préparation :")
            preparations = merged_df[
                (merged_df["Catégorie"].isin(selected_menus)) &
                (merged_df["Groupe d'aliment"].isin(selected_groupes)) &
                (merged_df["Type d'aliment"].isin(selected_types))
            ]["Préparation"].dropna().unique()
            selected_preparations = st.segmented_control("Modes de préparation", preparations.tolist(), selection_mode="multi")
            # st.markdown(f"Modes de cuisson sélectionnés : {selected_preparations}.")

# TODO propose liste des produits filtre avec le score unique EF dans le dataframe daffichage final dans loredre decroissant
# TODO on affiche tt les produit selectionnes avec le score unique EF classe et somme des apports nutritionnels
            if selected_preparations:
                st.subheader("Sélectionnez un produit dans les types sélectionnés :")
                product_search = st.text_input("Search for the product you like")
                product_search_filter = (
                    merged_df['Nom du Produit en Français'].str.lower().str.contains(product_search.lower()) &
                    merged_df["Catégorie"].isin(selected_menus) &
                    merged_df["Groupe d'aliment"].isin(selected_groupes) &
                    merged_df["Type d'aliment"].isin(selected_types) &
                    merged_df["Préparation"].isin(selected_preparations)
                )
                product_search_result = merged_df[["Nom du Produit en Français", "Score unique EF"]][product_search_filter].set_index("Nom du Produit en Français")
                product_selection = st.dataframe(product_search_result, selection_mode='multi-row', on_select='rerun')

                # Save selected products in a dataframe
                if product_selection['selection']['rows']:
                    selected_products_df = product_search_result.iloc[product_selection['selection']['rows']]
                    st.title('You selected')
                    st.dataframe(selected_products_df)

                    # display wit groups
                    # selected_rows = product_selection['selection']['rows']
                    # selected_products = product_search_result.iloc[selected_rows].index.tolist()
                    # display_df = merged_df[
                    #     merged_df["Nom du Produit en Français"].isin(selected_products)
                    # ][["Nom du Produit en Français", "Groupe d'aliment", "Score unique EF"]]
                    # st.dataframe(display_df)

                # selected_products = st.multiselect(
                #     "Sélectionnez un ou plusieurs produits :",
                #     options=product_search_result.index.tolist()
                # )

                # if selected_products:
                #     final_df = merged_df[
                #         merged_df["Nom du Produit en Français"].isin(selected_products)
                #     ].sort_values("Score unique EF", ascending=False)
                #     st.title('Produits sélectionnés')
                #     st.dataframe(final_df[["Nom du Produit en Français", "Score unique EF"]])
else:
    st.info("Sélectionnez au moins un élément de menu pour afficher les groupes d'aliments.")