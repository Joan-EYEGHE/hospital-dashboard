"""
app.py — Dashboard Hospitalier
Compatible Dash 4.x / Plotly 6.x / dash-bootstrap-components 2.x
"""

import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc

from modules.preprocessing import preprocess, apply_filters, get_kpis, get_filter_options
from modules.figures import (
    fig_tranches_age, fig_cout_departement, fig_duree_maladie,
    fig_repartition_traitements, fig_admissions_par_mois, fig_scatter_cout_duree,
)
from modules.rapport import generate_rapport_html
from modules.ml import train_and_evaluate

# ── Init ────────────────────────────────────────────────────────────────────

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,300&family=DM+Serif+Display&display=swap",
    ],
    suppress_callback_exceptions=True,
    title="Dashboard Hospitalier",
)
server = app.server

DF_GLOBAL  = preprocess()
OPTIONS    = get_filter_options(DF_GLOBAL)
_ml_raw    = train_and_evaluate(DF_GLOBAL)
ML_SCORES  = _ml_raw.get("all_scores", {k: v for k, v in _ml_raw.items() if k != "feature_importance_fig"})
FI_FIG     = _ml_raw.get("feature_importance_fig")

# ── Helpers ─────────────────────────────────────────────────────────────────

def kpi_card(icone, valeur, label, color):
    return html.Div([
        html.Div(icone, className="kpi-icon"),
        html.Div(valeur, className="kpi-value"),
        html.Div(label, className="kpi-label"),
    ], className="kpi-card", style={"borderLeftColor": color})


def make_dropdown(label, id_, options, placeholder):
    return html.Div([
        html.Label(label, className="filter-label"),
        dcc.Dropdown(
            id=id_,
            options=[{"label": o, "value": o} for o in options],
            multi=True, placeholder=placeholder, clearable=True,
            style={"fontSize": "0.88rem"},
        ),
    ])


def graph_card(title, graph_id):
    return html.Div([
        html.P(title, className="graph-title"),
        dcc.Graph(id=graph_id, config={"displayModeBar": False}),
    ], className="graph-card")


# ── Layout ───────────────────────────────────────────────────────────────────

app.layout = html.Div([

    # Sidebar
    html.Div([
        html.Div([
            html.Span("🏥", style={"fontSize": "1.8rem"}),
            html.Div("Dashboard Hospitalier", className="sidebar-title"),
            html.Div("M2 CDSD · ISM Dakar", className="sidebar-footer-text"),
        ], className="sidebar-brand"),

        html.Hr(className="sidebar-hr"),
        html.Div("FILTRES", className="sidebar-section-label"),

        html.Div([
            make_dropdown("Département", "filter-dept", OPTIONS["departements"], "Tous les départements"),
            make_dropdown("Sexe", "filter-sexe", OPTIONS["sexes"], "Tous"),
            make_dropdown("Tranche d'âge", "filter-age", OPTIONS["tranches_age"], "Toutes les tranches"),
        ], style={"display": "flex", "flexDirection": "column", "gap": "18px"}),

        html.Hr(className="sidebar-hr"),

        html.Button(
            "📥  Télécharger le rapport",
            id="btn-rapport", className="btn-download", n_clicks=0,
        ),
        dcc.Download(id="download-rapport"),

    ], className="sidebar"),

    # Contenu principal
    html.Div([

        # En-tête page
        html.Div([
            html.Div([
                html.H1("Analyse des données patients", className="page-title"),
                html.P("Optimisation des coûts · Anticipation des séjours longs", className="page-subtitle"),
            ]),
            html.Div(id="filter-badge", className="filter-badge"),
        ], className="page-header"),

        # KPIs
        html.Div(id="kpi-row", className="kpi-row"),

        # Graphiques — 3 lignes de 2
        html.Div([
            graph_card("Distribution des âges par tranche", "graph-tranches-age"),
            graph_card("Coût moyen par département (FCFA)", "graph-cout-dept"),
        ], className="graphs-row"),

        html.Div([
            graph_card("Durée de séjour par maladie", "graph-duree-maladie"),
            graph_card("Répartition des traitements", "graph-traitements"),
        ], className="graphs-row"),

        html.Div([
            graph_card("Évolution des admissions par mois", "graph-admissions"),
            graph_card("Coût vs Durée de séjour", "graph-scatter"),
        ], className="graphs-row"),

        # Section ML
        html.Div([
            html.H2("🤖 Machine Learning — Prédiction de séjour long", className="section-heading"),
            html.P(
                "Variable cible : SejourLong (DureeSejour > médiane 8 j → 1). "
                "Évaluation par Cross-Validation stratifiée 5 folds.",
                className="section-desc",
            ),
            html.Div(id="ml-section"),
        ], className="ml-wrapper"),

    ], className="main-content"),

], className="app-shell")


# ── Callback global (graphiques + KPIs) ─────────────────────────────────────

@callback(
    Output("kpi-row", "children"),
    Output("graph-tranches-age", "figure"),
    Output("graph-cout-dept", "figure"),
    Output("graph-duree-maladie", "figure"),
    Output("graph-traitements", "figure"),
    Output("graph-admissions", "figure"),
    Output("graph-scatter", "figure"),
    Output("filter-badge", "children"),
    Input("filter-dept", "value"),
    Input("filter-sexe", "value"),
    Input("filter-age", "value"),
)
def update_all(depts, sexes, ages):
    df = apply_filters(
        DF_GLOBAL,
        departements=depts or None,
        sexes=sexes or None,
        tranches_age=ages or None,
    )
    k = get_kpis(df)

    kpis = html.Div([
        kpi_card("👤", f"{k['nb_patients']:,}", "Patients", "#E63946"),
        kpi_card("💰", f"{k['cout_moyen']:,.0f}", "Coût moyen (FCFA)", "#457B9D"),
        kpi_card("🗓️", f"{k['duree_moyenne']} j", "Durée moyenne séjour", "#2A9D8F"),
        kpi_card("⚠️", f"{df['SejourLong'].mean()*100:.0f}%", "Taux séjours longs", "#E9C46A"),
    ], style={"display": "contents"})

    badge = (
        f"🔍 Filtres actifs · {len(df)} patients"
        if any([depts, sexes, ages])
        else "📋 500 patients · aucun filtre"
    )

    return (
        kpis,
        fig_tranches_age(df),
        fig_cout_departement(df),
        fig_duree_maladie(df),
        fig_repartition_traitements(df),
        fig_admissions_par_mois(df),
        fig_scatter_cout_duree(df),
        badge,
    )


# ── Callback ML (statique, affiché une seule fois) ──────────────────────────

@callback(
    Output("ml-section", "children"),
    Input("filter-dept", "value"),
)
def update_ml(_):
    winner = max(ML_SCORES, key=lambda m: ML_SCORES[m]["f1_mean"])

    rows = []
    for model, s in ML_SCORES.items():
        is_w = model == winner
        bar_pct = f"{min(s['f1_mean'] / 0.6 * 100, 100):.0f}%"
        rows.append(html.Tr([
            html.Td([
                html.Span("🏆 ", style={"marginRight": "4px"}) if is_w else None,
                html.Strong(model) if is_w else model,
            ]),
            html.Td([
                html.Div(f"{s['f1_mean']:.3f} ± {s['f1_std']:.3f}", className="f1-value"),
                html.Div(className="f1-bar-bg", children=[
                    html.Div(
                        className="f1-bar-fill" + (" f1-bar-winner" if is_w else ""),
                        style={"width": bar_pct},
                    ),
                ]),
            ]),
            html.Td(f"{s['accuracy']:.3f}"),
            html.Td(f"{s['precision']:.3f}"),
            html.Td(f"{s['recall']:.3f}"),
        ], style={"background": "#f0faf9" if is_w else "transparent"}))

    fi_section = html.Div([
        html.P("Importance des variables (Random Forest)", className="graph-title"),
        dcc.Graph(figure=FI_FIG, config={"displayModeBar": False}),
    ], className="graph-card") if FI_FIG else None

    return html.Div([
        html.Div([
            html.Div(
                f"🏆  Meilleur modèle : {winner}  ·  F1 = {ML_SCORES[winner]['f1_mean']:.3f}",
                className="winner-banner"
            ),
            html.Table([
                html.Thead(html.Tr([
                    html.Th(h) for h in
                    ["Modèle", "F1-score (CV)", "Accuracy", "Précision", "Rappel"]
                ])),
                html.Tbody(rows),
            ], className="ml-table"),
        ], className="ml-table-wrapper"),
        fi_section,
    ], className="ml-grid")


# ── Callback téléchargement ─────────────────────────────────────────────────

@callback(
    Output("download-rapport", "data"),
    Input("btn-rapport", "n_clicks"),
    State("filter-dept", "value"),
    State("filter-sexe", "value"),
    State("filter-age", "value"),
    prevent_initial_call=True,
)
def download_rapport(n, depts, sexes, ages):
    df = apply_filters(
        DF_GLOBAL,
        departements=depts or None,
        sexes=sexes or None,
        tranches_age=ages or None,
    )
    kpis = get_kpis(df)
    figs = {
        "tranches_age":  fig_tranches_age(df),
        "cout_dept":     fig_cout_departement(df),
        "duree_maladie": fig_duree_maladie(df),
        "traitements":   fig_repartition_traitements(df),
        "admissions":    fig_admissions_par_mois(df),
        "scatter":       fig_scatter_cout_duree(df),
    }
    return dict(
        content=generate_rapport_html(
            df, kpis, figs, _ml_raw,
            {"departements": depts, "sexes": sexes, "tranches_age": ages},
        ),
        filename="rapport_hospitalier.html",
    )


if __name__ == "__main__":
    app.run(debug=True)
