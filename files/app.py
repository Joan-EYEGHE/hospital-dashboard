"""
app.py
------
Point d'entrée du dashboard hospitalier (Dash).
Layout + callbacks. La logique métier est dans modules/.
"""

import base64

import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd

from modules.preprocessing import preprocess, apply_filters, get_kpis, get_filter_options
from modules.figures import (
    fig_tranches_age,
    fig_cout_departement,
    fig_duree_maladie,
    fig_repartition_traitements,
    fig_admissions_par_mois,
    fig_scatter_cout_duree,
)
from modules.rapport import generate_rapport_html
from modules.ml import train_and_evaluate  # créé ci-après

# ── Initialisation ───────────────────────────────────────────────────────────

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Dashboard Hospitalier",
)
server = app.server  # pour Gunicorn / Render

# Chargement unique au démarrage
DF_GLOBAL = preprocess()
OPTIONS = get_filter_options(DF_GLOBAL)

# Résultats ML calculés une fois (sur données complètes)
ML_RESULTS = train_and_evaluate(DF_GLOBAL)

# ── Composants réutilisables ─────────────────────────────────────────────────

def kpi_card(titre, valeur, icone, couleur):
    return dbc.Card(
        dbc.CardBody([
            html.Div(icone, className="kpi-icon"),
            html.Div(valeur, className="kpi-value"),
            html.Div(titre, className="kpi-label"),
        ]),
        className="kpi-card",
        style={"borderLeft": f"4px solid {couleur}"},
    )


def dropdown_filter(label, id_, options, placeholder):
    return html.Div([
        html.Label(label, className="filter-label"),
        dcc.Dropdown(
            id=id_,
            options=[{"label": o, "value": o} for o in options],
            multi=True,
            placeholder=placeholder,
            clearable=True,
        ),
    ], className="filter-item")


# ── Layout ───────────────────────────────────────────────────────────────────

app.layout = html.Div([

    # Header
    html.Div([
        html.Div([
            html.H1("🏥 Dashboard Hospitalier", className="dashboard-title"),
            html.P("Analyse des données patients · Prédiction des séjours longs",
                   className="dashboard-subtitle"),
        ]),
        html.Div([
            html.Button(
                "📥 Télécharger le rapport",
                id="btn-rapport",
                className="btn-rapport",
                n_clicks=0,
            ),
            dcc.Download(id="download-rapport"),
        ]),
    ], className="header"),

    # KPIs
    html.Div(id="kpi-section", className="kpi-section"),

    # Filtres
    html.Div([
        html.H3("🔍 Filtres", className="section-title"),
        html.Div([
            dropdown_filter(
                "Département", "filter-dept",
                OPTIONS["departements"], "Tous les départements"
            ),
            dropdown_filter(
                "Sexe", "filter-sexe",
                OPTIONS["sexes"], "Tous"
            ),
            dropdown_filter(
                "Tranche d'âge", "filter-age",
                OPTIONS["tranches_age"], "Toutes les tranches"
            ),
        ], className="filters-grid"),
    ], className="card filters-card"),

    # Graphiques
    html.Div([
        html.H3("📊 Visualisations", className="section-title"),
        html.Div([
            dbc.Row([
                dbc.Col(dcc.Graph(id="graph-tranches-age"), md=6),
                dbc.Col(dcc.Graph(id="graph-cout-dept"), md=6),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col(dcc.Graph(id="graph-duree-maladie"), md=6),
                dbc.Col(dcc.Graph(id="graph-traitements"), md=6),
            ], className="mb-4"),
            dbc.Row([
                dbc.Col(dcc.Graph(id="graph-admissions"), md=6),
                dbc.Col(dcc.Graph(id="graph-scatter"), md=6),
            ]),
        ]),
    ], className="card"),

    # Section ML
    html.Div([
        html.H3("🤖 Machine Learning — Prédiction de séjour long", className="section-title"),
        html.P(
            "Variable cible : SejourLong (DureeSejour > médiane → 1). "
            "Évaluation par Cross-Validation 5 folds.",
            className="ml-description"
        ),
        html.Div(id="ml-results-section"),
    ], className="card ml-card"),

], className="main-container")


# ── Callbacks ────────────────────────────────────────────────────────────────

def get_filtered(depts, sexes, ages):
    return apply_filters(
        DF_GLOBAL,
        departements=depts or None,
        sexes=sexes or None,
        tranches_age=ages or None,
    )


@callback(
    Output("kpi-section", "children"),
    [Input("filter-dept", "value"),
     Input("filter-sexe", "value"),
     Input("filter-age", "value")],
)
def update_kpis(depts, sexes, ages):
    df = get_filtered(depts, sexes, ages)
    k = get_kpis(df)
    return html.Div([
        kpi_card("Patients", str(k["nb_patients"]), "👤", "#E63946"),
        kpi_card("Coût moyen", f"{k['cout_moyen']:,.0f} FCFA", "💰", "#457B9D"),
        kpi_card("Durée moyenne", f"{k['duree_moyenne']} jours", "🗓️", "#2A9D8F"),
    ], className="kpis-row")


@callback(
    [Output("graph-tranches-age", "figure"),
     Output("graph-cout-dept", "figure"),
     Output("graph-duree-maladie", "figure"),
     Output("graph-traitements", "figure"),
     Output("graph-admissions", "figure"),
     Output("graph-scatter", "figure")],
    [Input("filter-dept", "value"),
     Input("filter-sexe", "value"),
     Input("filter-age", "value")],
)
def update_graphs(depts, sexes, ages):
    df = get_filtered(depts, sexes, ages)
    return (
        fig_tranches_age(df),
        fig_cout_departement(df),
        fig_duree_maladie(df),
        fig_repartition_traitements(df),
        fig_admissions_par_mois(df),
        fig_scatter_cout_duree(df),
    )


@callback(
    Output("ml-results-section", "children"),
    Input("filter-dept", "value"),  # déclenché à l'init pour afficher d'emblée
)
def display_ml_results(_):
    """Affiche les résultats ML sous forme de tableau + badge gagnant."""
    rows = []
    for model, scores in ML_RESULTS.items():
        rows.append(html.Tr([
            html.Td(model, style={"fontWeight": "600"}),
            html.Td(f"{scores['f1_mean']:.3f}"),
            html.Td(f"± {scores['f1_std']:.3f}"),
            html.Td(f"{scores['accuracy']:.3f}"),
            html.Td(f"{scores['precision']:.3f}"),
            html.Td(f"{scores['recall']:.3f}"),
        ]))

    winner = max(ML_RESULTS, key=lambda m: ML_RESULTS[m]["f1_mean"])

    return html.Div([
        html.Div([
            html.Span("🏆 Meilleur modèle : ", className="winner-label"),
            html.Span(winner, className="winner-name"),
            html.Span(
                f" F1 = {ML_RESULTS[winner]['f1_mean']:.3f}",
                className="winner-score"
            ),
        ], className="winner-banner"),

        html.Table([
            html.Thead(html.Tr([
                html.Th("Modèle"),
                html.Th("F1-score (CV)"),
                html.Th("Écart-type"),
                html.Th("Accuracy"),
                html.Th("Précision"),
                html.Th("Rappel"),
            ])),
            html.Tbody(rows),
        ], className="ml-table"),

        html.Div([
            html.H4("Importance des variables (Random Forest)", className="feat-title"),
            dcc.Graph(id="graph-feature-importance",
                      figure=ML_RESULTS.get("feature_importance_fig",
                                            {"data": [], "layout": {}})),
        ], className="feature-importance"),
    ])


@callback(
    Output("download-rapport", "data"),
    Input("btn-rapport", "n_clicks"),
    [State("filter-dept", "value"),
     State("filter-sexe", "value"),
     State("filter-age", "value")],
    prevent_initial_call=True,
)
def download_rapport(n_clicks, depts, sexes, ages):
    df = get_filtered(depts, sexes, ages)
    kpis = get_kpis(df)
    filtres = {"departements": depts, "sexes": sexes, "tranches_age": ages}

    figs = {
        "tranches_age": fig_tranches_age(df),
        "cout_dept":    fig_cout_departement(df),
        "duree_maladie": fig_duree_maladie(df),
        "traitements":  fig_repartition_traitements(df),
        "admissions":   fig_admissions_par_mois(df),
        "scatter":      fig_scatter_cout_duree(df),
    }

    html_content = generate_rapport_html(df, kpis, figs, ML_RESULTS, filtres)
    return dict(content=html_content, filename="rapport_hospitalier.html")


# ── Lancement ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
