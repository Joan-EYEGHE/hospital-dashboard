"""
figures.py
----------
Génération des 6 graphiques Plotly du dashboard hospitalier.
Chaque fonction reçoit un DataFrame (déjà filtré) et retourne une figure Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Palette & thème ──────────────────────────────────────────────────────────

COULEURS_DEPT = {
    "Cardiologie":  "#E63946",
    "Oncologie":    "#457B9D",
    "Neurologie":   "#2A9D8F",
    "Orthopédie":   "#E9C46A",
    "Pneumologie":  "#F4A261",
    "Gériatrie":    "#A8DADC",
    "Dermatologie": "#6D6875",
}

COULEURS_TRAITEMENT = [
    "#E63946", "#457B9D", "#2A9D8F",
    "#E9C46A", "#F4A261", "#6D6875"
]

COULEURS_TRANCHES = [
    "#264653", "#2A9D8F", "#E9C46A",
    "#F4A261", "#E63946", "#6D6875"
]

ORDRE_TRANCHES = ["0-20", "20-30", "30-40", "40-50", "50-60", "+60"]
ORDRE_MOIS = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun",
              "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]

LAYOUT_BASE = dict(
    font_family="'Segoe UI', sans-serif",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=20, t=50, b=40),
    hoverlabel=dict(bgcolor="white", font_size=13),
)


def _apply_base(fig) -> go.Figure:
    """Applique le thème de base à une figure."""
    fig.update_layout(**LAYOUT_BASE)
    fig.update_xaxes(showgrid=False, linecolor="#e0e0e0")
    fig.update_yaxes(gridcolor="#f0f0f0", linecolor="#e0e0e0")
    return fig


# ── Graphique 1 : Distribution des âges par tranche ──────────────────────────

def fig_tranches_age(df: pd.DataFrame) -> go.Figure:
    """Bar chart — nombre de patients par tranche d'âge."""
    if df.empty:
        return _empty_fig("Aucune donnée")

    counts = (
        df["TrancheAge"]
        .astype(str)
        .value_counts()
        .reindex(ORDRE_TRANCHES, fill_value=0)
        .reset_index()
    )
    counts.columns = ["TrancheAge", "NbPatients"]

    fig = px.bar(
        counts,
        x="TrancheAge",
        y="NbPatients",
        title="Distribution des âges par tranche",
        color="TrancheAge",
        color_discrete_sequence=COULEURS_TRANCHES,
        text="NbPatients",
        labels={"TrancheAge": "Tranche d'âge", "NbPatients": "Nb patients"},
    )
    fig.update_traces(textposition="outside", showlegend=False)
    fig.update_layout(title_font_size=15)
    return _apply_base(fig)


# ── Graphique 2 : Coût moyen par département ─────────────────────────────────

def fig_cout_departement(df: pd.DataFrame) -> go.Figure:
    """Bar chart horizontal — coût moyen par département."""
    if df.empty:
        return _empty_fig("Aucune donnée")

    cout_dept = (
        df.groupby("Departement")["Cout"]
        .mean()
        .round(0)
        .reset_index()
        .sort_values("Cout", ascending=True)
    )

    fig = px.bar(
        cout_dept,
        x="Cout",
        y="Departement",
        orientation="h",
        title="Coût moyen par département (FCFA)",
        color="Departement",
        color_discrete_map=COULEURS_DEPT,
        text=cout_dept["Cout"].apply(lambda x: f"{int(x):,}"),
        labels={"Cout": "Coût moyen (FCFA)", "Departement": ""},
    )
    fig.update_traces(textposition="outside", showlegend=False)
    fig.update_layout(title_font_size=15)
    return _apply_base(fig)


# ── Graphique 3 : Durée de séjour par maladie ───────────────────────────────

def fig_duree_maladie(df: pd.DataFrame) -> go.Figure:
    """Box plot — distribution de la durée de séjour par maladie."""
    if df.empty:
        return _empty_fig("Aucune donnée")

    fig = px.box(
        df,
        x="Maladie",
        y="DureeSejour",
        title="Durée de séjour par maladie (jours)",
        color="Maladie",
        points="outliers",
        labels={"DureeSejour": "Durée (jours)", "Maladie": ""},
    )
    fig.update_traces(showlegend=False)
    fig.update_layout(title_font_size=15)
    return _apply_base(fig)


# ── Graphique 4 : Répartition des traitements (pie) ─────────────────────────

def fig_repartition_traitements(df: pd.DataFrame) -> go.Figure:
    """Donut chart — répartition des traitements."""
    if df.empty:
        return _empty_fig("Aucune donnée")

    counts = df["Traitement"].value_counts().reset_index()
    counts.columns = ["Traitement", "NbPatients"]

    fig = px.pie(
        counts,
        names="Traitement",
        values="NbPatients",
        title="Répartition des traitements",
        hole=0.45,
        color_discrete_sequence=COULEURS_TRAITEMENT,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>%{value} patients (%{percent})<extra></extra>",
    )
    fig.update_layout(title_font_size=15, showlegend=True)
    return _apply_base(fig)


# ── Graphique 5 : Évolution des admissions par mois ─────────────────────────

def fig_admissions_par_mois(df: pd.DataFrame) -> go.Figure:
    """Line chart — nombre d'admissions par mois."""
    if df.empty:
        return _empty_fig("Aucune donnée")

    admissions = (
        df.groupby(["MoisAdmission", "MoisLabel"])
        .size()
        .reset_index(name="NbAdmissions")
        .sort_values("MoisAdmission")
    )

    fig = px.line(
        admissions,
        x="MoisLabel",
        y="NbAdmissions",
        title="Évolution des admissions par mois",
        markers=True,
        labels={"MoisLabel": "Mois", "NbAdmissions": "Nb admissions"},
        category_orders={"MoisLabel": ORDRE_MOIS},
    )
    fig.update_traces(
        line=dict(color="#E63946", width=2.5),
        marker=dict(size=8, color="#E63946"),
    )
    fig.update_layout(title_font_size=15)
    return _apply_base(fig)


# ── Graphique 6 : Scatter Coût vs Durée de séjour ───────────────────────────

def fig_scatter_cout_duree(df: pd.DataFrame) -> go.Figure:
    """Scatter plot — Coût vs Durée de séjour, coloré par département."""
    if df.empty:
        return _empty_fig("Aucune donnée")

    fig = px.scatter(
        df,
        x="DureeSejour",
        y="Cout",
        color="Departement",
        color_discrete_map=COULEURS_DEPT,
        hover_data=["Age", "Maladie", "Traitement"],
        title="Coût vs Durée de séjour",
        labels={"DureeSejour": "Durée séjour (jours)", "Cout": "Coût (FCFA)"},
        opacity=0.7,
    )
    m, b = np.polyfit(df["DureeSejour"], df["Cout"], 1)
    x_line = sorted(df["DureeSejour"].unique())
    fig.add_trace(go.Scatter(
        x=x_line, y=[m * xi + b for xi in x_line],
        mode="lines",
        line=dict(color="#333333", width=1.5, dash="dot"),
        name="Tendance", showlegend=False,
    ))
    fig.update_layout(title_font_size=15)
    return _apply_base(fig)


# ── Utilitaire ───────────────────────────────────────────────────────────────

def _empty_fig(message: str = "Aucune donnée disponible") -> go.Figure:
    """Retourne une figure vide avec un message centré."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color="#999"),
    )
    fig.update_layout(
        **LAYOUT_BASE,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig
