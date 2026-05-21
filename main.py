import streamlit as st
import pandas as pd
import string

from ordonnancement import (
    valider_donnees,
    construire_graphe,
    calcul_dates_plus_tot,
    calcul_successeurs,
    calcul_fin_projet,
    calcul_chemin_critique,
    afficher_chemin_critique_simple
)

st.set_page_config(
    page_title="Ordonnancement TABLO",
    layout="wide"
)

st.title("Ordonnancement des tâches - Méthode TABLO")

# -------------------------
# Nombre de tâches
# -------------------------

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    nb_taches = st.number_input(
        "Nombre de tâches",
        min_value=1,
        max_value=26,
        value=5
    )

noms_taches = list(string.ascii_uppercase[:nb_taches])

# -------------------------
# Tableau de saisie
# -------------------------

data = {
    tache: ["1", "-"] for tache in noms_taches
}

df = pd.DataFrame(
    data,
    index=["Durée", "T.antérieurs"]
)

st.subheader("Saisie des données")

df_edit = st.data_editor(
    df,
    use_container_width=True
)

# -------------------------
# Bouton calcul
# -------------------------

if st.button("Calculer"):

    valide, message = valider_donnees(df_edit, noms_taches)

    if not valide:
        st.error(message)

    else:

        # -------------------------
        # Construction données
        # -------------------------

        graphe = construire_graphe(df_edit, noms_taches)

        # -------------------------
        # Successeurs
        # -------------------------

        successeurs = calcul_successeurs(graphe)

        # -------------------------
        # Dates au plus tôt
        # -------------------------

        dates, ordre_taches = calcul_dates_plus_tot(graphe)
        date_fin = calcul_fin_projet(
            graphe,
            successeurs,
            dates
        )

        # -------------------------
        # Tableau résultat
        # -------------------------
        # Tri TABLO :
        # date plus tôt puis alphabet

        ordre_taches = sorted(
            ordre_taches,
            key=lambda t: (
                dates[t],
                t
            )
        )
        
        resultat = []

        for tache in ordre_taches:

            resultat.append({
                "Tâche": tache,
                "Durée": graphe[tache]["duree"],
                "Antécédents": ", ".join(graphe[tache]["antecedents"]) if graphe[tache]["antecedents"] else "-",
                "Successeurs": ", ".join(successeurs[tache]) if successeurs[tache] else "-",
                "Date plus tôt": dates[tache]
            })

        # Ajouter ligne FIN

        resultat.append({
            "Tâche": "FIN",
            "Durée": "-",
            "Antécédents": "-",
            "Successeurs": "-",
            "Date plus tôt": date_fin
        })

        df_resultat = pd.DataFrame(resultat)

        st.success("Calcul terminé")

        st.subheader("Résultats")

        st.dataframe(
            df_resultat,
            use_container_width=True
        )
        chemin_critique = calcul_chemin_critique(
            graphe,
            dates,
            date_fin
        )

        # -------------------------
        # Graphe PERT
        # -------------------------

        # -------------------------
        # Affichage chemin critique
        # -------------------------

        st.subheader("Chemin critique")

        st.success(
            " → ".join(
                ["DEBUT"]
                + chemin_critique
                + ["FIN"]
            )
        )

        # -------------------------
        # Graphe chemin critique
        # -------------------------

        st.subheader(
            "Graphe du chemin critique"
        )

        fig = afficher_chemin_critique_simple(
            chemin_critique,
            graphe
        )

        st.pyplot(fig)