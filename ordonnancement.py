from collections import deque
import networkx as nx
import matplotlib.pyplot as plt

# ---------------------------------------
# Validation
# ---------------------------------------

def valider_donnees(df, noms_taches):

    # Vérification durées
    for tache in noms_taches:

        valeur = str(df.loc["Durée", tache]).strip()

        try:
            d = int(valeur)

            if d <= 0:
                return False, f"Durée invalide pour {tache}"

        except:
            return False, f"Durée invalide pour {tache}"

    # Vérification antécédents
    for tache in noms_taches:

        ants = str(df.loc["T.antérieurs", tache]).strip()

        if ants == "-":
            continue

        liste = list(ants.replace(" ", ""))

        for a in liste:

            a = a.strip()

            if a not in noms_taches:
                return False, f"Tâche inconnue : {a}"

            if a == tache:
                return False, f"{tache} ne peut pas dépendre d'elle-même"

    return True, "OK"


# ---------------------------------------
# Construction graphe
# ---------------------------------------

def construire_graphe(df, noms_taches):

    graphe = {}

    for tache in noms_taches:

        duree = int(df.loc["Durée", tache])

        ants = str(df.loc["T.antérieurs", tache]).strip()

        if ants == "-":
            antecedents = []
        else:
            antecedents = list(ants.replace(" ", ""))

        graphe[tache] = {
            "duree": duree,
            "antecedents": antecedents
        }

    return graphe


# ---------------------------------------
# Successeurs
# ---------------------------------------

def calcul_successeurs(graphe):

    successeurs = {}

    for t in graphe:
        successeurs[t] = []

    for tache, infos in graphe.items():

        for ant in infos["antecedents"]:
            successeurs[ant].append(tache)

    return successeurs


# ---------------------------------------
# Dates au plus tôt
# ---------------------------------------

def calcul_dates_plus_tot(graphe):

    indegree = {}
    dates = {}

    for t in graphe:
        indegree[t] = len(graphe[t]["antecedents"])
        dates[t] = 0

    queue = deque()

    for t in graphe:
        if indegree[t] == 0:
            queue.append(t)

    ordre = []

    while queue:

        courant = queue.popleft()

        ordre.append(courant)

        for succ, infos in graphe.items():

            if courant in infos["antecedents"]:

                debut_possible = (
                    dates[courant]
                    + graphe[courant]["duree"]
                )

                dates[succ] = max(
                    dates[succ],
                    debut_possible
                )

                indegree[succ] -= 1

                if indegree[succ] == 0:
                    queue.append(succ)

    # Détection cycle
    if len(ordre) != len(graphe):
        raise Exception(
            "Cycle détecté dans les dépendances"
        )

    return dates, ordre
def calcul_fin_projet(graphe, successeurs, dates):

    fins = []

    for tache in graphe:

        # aucune tâche après
        if len(successeurs[tache]) == 0:

            fin = (
                dates[tache]
                + graphe[tache]["duree"]
            )

            fins.append(fin)

    return max(fins)

def calcul_chemin_critique(graphe, dates, date_fin):

    chemin = []

    # Recherche tâche finale critique
    fin_tache = None

    for tache in graphe:

        fin = (
            dates[tache]
            + graphe[tache]["duree"]
        )

        if fin == date_fin:
            fin_tache = tache

    courant = fin_tache

    while courant:

        chemin.insert(0, courant)

        antecedents = graphe[courant]["antecedents"]

        precedent = None

        for ant in antecedents:

            fin_ant = (
                dates[ant]
                + graphe[ant]["duree"]
            )

            if fin_ant == dates[courant]:

                precedent = ant
                break

        courant = precedent

    return chemin

def afficher_chemin_critique_simple(
        chemin,
        graphe
):

    fig, ax = plt.subplots(
        figsize=(22, 5)
    )

    # -----------------------------
    # Fond moderne
    # -----------------------------

    fig.patch.set_facecolor("#f8fafc")
    ax.set_facecolor("#f8fafc")

    ax.axis("off")

    # -----------------------------
    # Construction chemin
    # -----------------------------

    chemin_complet = (
        ["DEBUT"]
        + chemin
        + ["FIN"]
    )

    # Espacement horizontal
    espace = 3

    x_positions = [
        i * espace
        for i in range(len(chemin_complet))
    ]

    y = 0

    # -----------------------------
    # Flèches modernes
    # -----------------------------

    for i in range(len(chemin_complet) - 1):

        x1 = x_positions[i]
        x2 = x_positions[i + 1]

        # Glow arrière
        ax.plot(
            [x1 + 0.52, x2 - 0.52],
            [y, y],
            color="#e2e8f0",
            linewidth=14,
            alpha=0.55,
            solid_capstyle="round",
            zorder=0
        )

        # Pointe flèche moderne
        # Flèche moderne propre
        ax.annotate(
            "",
            xy=(x2 - 0.50, y),
            xytext=(x1 + 0.52, y),
            arrowprops=dict(
                arrowstyle="->",
                color="#ef4444",
                lw=3.5,
                shrinkA=0,
                shrinkB=0,
                mutation_scale=18,
                capstyle="round",
                joinstyle="round"
            ),
            zorder=2
        )

    # -----------------------------
    # Noeuds
    # -----------------------------

    for i, noeud in enumerate(chemin_complet):

        x = x_positions[i]

        # --------------------------------
        # DEBUT / FIN
        # --------------------------------

        if noeud in ["DEBUT", "FIN"]:

            # Ombre
            ombre = plt.Circle(
                (x, y - 0.04),
                0.60,
                color="#86efac",
                alpha=0.35,
                zorder=2
            )

            ax.add_patch(ombre)

            # Cercle principal
            cercle = plt.Circle(
                (x, y),
                0.52,
                facecolor="#16a34a",
                edgecolor="white",
                linewidth=4,
                zorder=3
            )

            ax.add_patch(cercle)

            # Texte
            ax.text(
                x,
                y,
                noeud,
                ha="center",
                va="center",
                fontsize=11,
                color="white",
                fontweight="bold",
                zorder=4
            )

        # --------------------------------
        # Tâches
        # --------------------------------

        else:

            # Ombre
            ombre = plt.Circle(
                (x, y - 0.04),
                0.54,
                color="#bae6fd",
                alpha=0.45,
                zorder=2
            )

            ax.add_patch(ombre)

            # Cercle principal
            cercle = plt.Circle(
                (x, y),
                0.48,
                facecolor="#0ea5e9",
                edgecolor="white",
                linewidth=4,
                zorder=3
            )

            ax.add_patch(cercle)

            # Texte tâche
            ax.text(
                x,
                y,
                noeud,
                ha="center",
                va="center",
                fontsize=14,
                color="white",
                fontweight="bold",
                zorder=4
            )

    # -----------------------------
    # Durées modernes
    # -----------------------------

    for i in range(len(chemin_complet) - 1):

        x1 = x_positions[i]
        x2 = x_positions[i + 1]

        depart = chemin_complet[i]

        # Durée
        if depart == "DEBUT":

            duree = 0

        else:

            duree = graphe[depart]["duree"]

        milieu = (x1 + x2) / 2

        # Ombre badge
        ax.text(
            milieu,
            y + 0.42,
            str(duree),
            ha="center",
            va="center",
            fontsize=14,
            fontweight="bold",
            color="white",
            bbox=dict(
                boxstyle="round,pad=0.50",
                fc="#fecaca",
                ec="none"
            ),
            alpha=0.35,
            zorder=4
        )

        # Badge principal
        ax.text(
            milieu,
            y + 0.45,
            str(duree),
            ha="center",
            va="center",
            fontsize=14,
            fontweight="bold",
            color="#991b1b",
            bbox=dict(
                boxstyle="round,pad=0.50",
                fc="white",
                ec="#ef4444",
                lw=2.5
            ),
            zorder=5
        )

    # -----------------------------
    # Titre
    # -----------------------------

    ax.set_title(
        "Chemin Critique du Projet",
        fontsize=20,
        fontweight="bold",
        color="#0f172a",
        pad=25
    )

    # -----------------------------
    # Limites affichage
    # -----------------------------

    ax.set_xlim(
        -1.5,
        x_positions[-1] + 1.5
    )

    ax.set_ylim(
        -1.5,
        1.5
    )

    plt.tight_layout()

    return fig