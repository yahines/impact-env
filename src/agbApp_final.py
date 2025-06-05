import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- Chargement des données ---
merged_df = pd.read_csv("data/AGB_CIQUAL_food_products_category_type.csv")

# --- Titre ---
st.title("🍽️ Sélectionnez vos aliments et découvrez leurs impacts environnementaux 🌿")
# st.set_page_config(page_title="🍽️ Sélectionnez vos aliments et découvrez leur empreinte environnementale 🌿", layout="wide")

# --- Agrégation des scores EF ---
agg_df_gen = merged_df.groupby("Groupe d'aliment")["Score unique EF"].agg(['min', 'median', 'max']).reset_index()
# Pour chaque ligne, une barre horizontale avec les 3 valeurs

# with st.expander("Scores EF pour groupe d'aliment", expanded=True):
#     for index, row in agg_df_gen.iterrows():
#         cat = row["Groupe d'aliment"]
#         min_val, med_val, max_val = row['min'], row['median'], row['max']

#         fig = go.Figure()
#         fig.add_trace(go.Bar(
#             x=[min_val, med_val, max_val],
#             y=[cat, cat, cat],
#             orientation='h',
#             marker_color=["rgb(235, 91, 37)", "rgb(116, 147, 83)", "rgb(237, 177, 11)"],
#             name="Min / Médiane / Max",
#             customdata=[["Min"], ["Médiane"], ["Max"]],
#             hovertemplate='%{customdata[0]}: %{x}<extra></extra>',
#             showlegend=False,
#             text=[f"{min_val:.2f}", f"{med_val:.2f}", f"{max_val:.2f}"],  # Affiche les valeurs
#             textposition="inside"
#         ))

#         fig.update_layout(
#             height=50,
#             margin={"l": 5, "r": 5, "t": 5, "b": 5},
#             xaxis={"showgrid": False, "showticklabels": False },
#             # yaxis={"showticklabels": True, "tickfont": {"size": 10}, "automargin": True},
#             yaxis={
#                 "showticklabels": True,
#                 "tickfont": {"size": 16},  # Increased font size for y labels
#                 "automargin": True
#             },
#         )
#         st.plotly_chart(fig, use_container_width=False)

# --- Interface de sélection ---
# TODO DONE case à cocher avec les 8 elem
st.subheader("\n\n Sélectionnez les éléments de votre menu :")
selected_menus = {}
menus = merged_df["Catégorie"].dropna().unique()
selected_menus = st.segmented_control("éléments menu", 
                                      menus.tolist(), 
                                      selection_mode="multi", 
                                      label_visibility="hidden")
# st.markdown(f"Éléments sélectionnés : {selected_menus}.")

# TODO DONE input pour liste de groupes confondus 
if selected_menus:
    st.subheader("Sélectionnez un ou plusieurs groupes d'aliments :")
    groupes = merged_df[merged_df["Catégorie"].isin(selected_menus)]["Groupe d'aliment"].dropna().unique()
    selected_groupes = st.segmented_control("Groupes d'aliments", 
                                            groupes.tolist(), 
                                            selection_mode="multi", 
                                            label_visibility="hidden")
    # st.markdown(f"Groupes sélectionnés : {selected_groupes}.")

# TODO input pour liste de types confondus 
    if selected_groupes:
        st.subheader("Sélectionnez un ou plusieurs types d'aliments :")
        types = merged_df[
            (merged_df["Catégorie"].isin(selected_menus)) &
            (merged_df["Groupe d'aliment"].isin(selected_groupes))
        ]["Type d'aliment"].dropna().unique()
        selected_types = st.segmented_control("Types d'aliments", 
                                              types.tolist(), 
                                              selection_mode="multi", 
                                              label_visibility="hidden")
        # st.markdown(f"Types sélectionnés : {selected_types}.")

# TODO selectionner dans liste des type de cuisson
        if selected_types:
            st.subheader("Sélectionnez un ou plusieurs modes de préparation :")
            preparations = merged_df[
                (merged_df["Catégorie"].isin(selected_menus)) &
                (merged_df["Groupe d'aliment"].isin(selected_groupes)) &
                (merged_df["Type d'aliment"].isin(selected_types))
            ]["Préparation"].dropna().unique()
            selected_preparations = st.segmented_control("Modes de préparation", 
                                                         preparations.tolist(), 
                                                         selection_mode="multi", 
                                                         label_visibility="hidden")
            # st.markdown(f"Modes de cuisson sélectionnés : {selected_preparations}.")

# TODO propose liste des produits filtre avec le score unique EF dans le dataframe daffichage final dans loredre decroissant
# TODO on affiche tt les produit selectionnes avec le score unique EF classe et somme des apports nutritionnels
            if selected_preparations:
                st.subheader("Sélectionnez un produit que vous désirez dans la liste des produits alimentaires :")
                #product_search = st.text_input("Search for the product you like", label_visibility="hidden")
                product_search_filter = (
                #     merged_df['Nom du Produit en Français'].str.lower().str.contains(product_search.lower()) &
                    merged_df["Catégorie"].isin(selected_menus) &
                    merged_df["Groupe d'aliment"].isin(selected_groupes) &
                    merged_df["Type d'aliment"].isin(selected_types) &
                    merged_df["Préparation"].isin(selected_preparations)
                )
                product_search_result = merged_df[["Nom du Produit en Français", "Score unique EF"]][product_search_filter].set_index("Nom du Produit en Français")
                # sort with Score unique EF in descending order
                product_search_result = product_search_result.sort_values("Score unique EF", ascending=False)
                product_selection = st.dataframe(product_search_result, selection_mode='multi-row', on_select='rerun')

                # Save selected products in a dataframe
                # all_selected_products_df = pd.DataFrame()
                # print(all_selected_products_df.shape)
                if product_selection['selection']['rows']:
                    selected_products_df = product_search_result.iloc[product_selection['selection']['rows']]
                    # all_selected_products_df = pd.concat([all_selected_products_df, selected_products_df], ignore_index=True).set_index("Nom du Produit en Français")
                    st.subheader('Vous avez mis dans votre assiette :')
                    st.dataframe(selected_products_df)
                    # Display the sum of the "Score unique EF" for the selected products
                    # st.markdown(f"**Somme du Score unique EF des produits sélectionnés :** {selected_products_df['Score unique EF'].sum():.2f}")
                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: center; align-items: center;">
                            <div style="background-color: #f0f2f6; padding: 1.5em 2em; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                                <span style="font-weight: bold; font-size: 1.2em;">
                                    Somme du Score EF de votre assiette : {selected_products_df['Score unique EF'].sum():.2f}
                                </span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True)
                # st.title('You selected')
                # st.dataframe(all_selected_products_df)
else:
    st.info("Sélectionnez au moins un élément de menu pour afficher les groupes d'aliments.")