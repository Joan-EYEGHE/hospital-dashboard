"""
ml.py — Module Machine Learning
Prédiction SejourLong — 3 niveaux, 5 modèles + VotingClassifier
Compatible scikit-learn 1.8.x
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier, ExtraTreesClassifier,
    HistGradientBoostingClassifier, VotingClassifier,
)
import plotly.express as px
import plotly.graph_objects as go

# ── Constantes ───────────────────────────────────────────────────────────────

FEATURES_BASE   = ['Age', 'Departement_enc', 'Sexe_enc', 'Maladie_enc', 'Traitement_enc', 'Saison_enc']
FEATURES_ENRICH = FEATURES_BASE + ['EstSenior', 'EstPediatrique', 'Mois', 'Trimestre', 'Mal_Trait']

CV = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
SCORING = ['f1', 'accuracy', 'precision', 'recall']


# ── Feature Engineering ──────────────────────────────────────────────────────

def build_ml_features(df: pd.DataFrame) -> pd.DataFrame:
    """Encode les catégorielles + crée les features enrichies. Retourne df augmenté."""
    df = df.copy()
    for col in ['Departement', 'Sexe', 'Maladie', 'Traitement', 'Saison']:
        le = LabelEncoder()
        df[col + '_enc'] = le.fit_transform(df[col].astype(str))

    df['EstSenior']      = (df['Age'] >= 60).astype(int)
    df['EstPediatrique'] = (df['Age'] < 20).astype(int)
    df['Mois']           = df['MoisAdmission']
    df['Trimestre']      = ((df['MoisAdmission'] - 1) // 3 + 1)
    df['Mal_Trait']      = df['Maladie_enc'] * 10 + df['Traitement_enc']
    return df


def _make_models():
    """Retourne les 5 modèles de base + VotingClassifier."""
    lr  = Pipeline([('sc', StandardScaler()), ('m', LogisticRegression(max_iter=1000, random_state=42))])
    dt  = Pipeline([('m', DecisionTreeClassifier(random_state=42))])
    rf  = Pipeline([('m', RandomForestClassifier(n_estimators=100, random_state=42))])
    et  = Pipeline([('m', ExtraTreesClassifier(n_estimators=100, random_state=42))])
    hgb = Pipeline([('m', HistGradientBoostingClassifier(random_state=42))])

    lr2  = Pipeline([('sc', StandardScaler()), ('m', LogisticRegression(max_iter=1000, random_state=42))])
    et2  = Pipeline([('m', ExtraTreesClassifier(n_estimators=100, random_state=42))])
    hgb2 = Pipeline([('m', HistGradientBoostingClassifier(random_state=42))])
    voting = VotingClassifier([('lr', lr2), ('et', et2), ('hgb', hgb2)], voting='soft')

    return {
        'Logistic Regression':  lr,
        'Decision Tree':        dt,
        'Random Forest':        rf,
        'Extra Trees':          et,
        'HistGradientBoosting': hgb,
        'Voting (LR+ET+HGB)':   voting,
    }


def _cv_row(pipe, X, y) -> dict:
    res = cross_validate(pipe, X, y, cv=CV, scoring=SCORING, n_jobs=-1)
    return {
        'f1_mean':   float(res['test_f1'].mean()),
        'f1_std':    float(res['test_f1'].std()),
        'accuracy':  float(res['test_accuracy'].mean()),
        'precision': float(res['test_precision'].mean()),
        'recall':    float(res['test_recall'].mean()),
    }


# ── Figure feature importance ────────────────────────────────────────────────

def _fi_figure(df_ml: pd.DataFrame, y: pd.Series) -> go.Figure:
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(df_ml[FEATURES_ENRICH], y)

    labels = {
        'Age': 'Âge', 'Departement_enc': 'Département', 'Sexe_enc': 'Sexe',
        'Maladie_enc': 'Maladie', 'Traitement_enc': 'Traitement', 'Saison_enc': 'Saison',
        'EstSenior': 'Est Senior (≥60)', 'EstPediatrique': 'Est Pédiatrique (<20)',
        'Mois': 'Mois admission', 'Trimestre': 'Trimestre', 'Mal_Trait': 'Maladie×Traitement',
    }
    fi = (
        pd.DataFrame({'Feature': FEATURES_ENRICH, 'Importance': rf.feature_importances_})
        .assign(Feature=lambda d: d['Feature'].map(labels).fillna(d['Feature']))
        .sort_values('Importance', ascending=True)
    )
    fig = px.bar(
        fi, x='Importance', y='Feature', orientation='h',
        title='Importance des variables (Random Forest)',
        color='Importance',
        color_continuous_scale=['#a8dadc', '#457b9d', '#1d3557'],
        labels={'Importance': 'Importance relative', 'Feature': ''},
    )
    fig.update_layout(
        font_family="'Segoe UI', Calibri, sans-serif",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=20, t=50, b=40), coloraxis_showscale=False,
        title_font_size=14,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor='#f0f0f0')
    return fig


# ── Pipeline principal ───────────────────────────────────────────────────────

def train_and_evaluate(df: pd.DataFrame) -> dict:
    """
    Entraîne 5 modèles + VotingClassifier sur 3 niveaux.

    Returns
    -------
    dict {
        'niveau1': { modèle: scores },
        'niveau2': { modèle: scores },
        'niveau3': { modèle: scores },   ← VotingClassifier uniquement
        'best_model': str,
        'best_scores': dict,
        'progression': { 'base': f1, 'enrichi': f1, 'optimise': f1 },
        'feature_importance_fig': go.Figure,
    }
    """
    df_ml = build_ml_features(df)
    y     = df_ml['SejourLong']
    X_base   = df_ml[FEATURES_BASE]
    X_enrich = df_ml[FEATURES_ENRICH]

    # ── Niveau 1 — Base ──
    niveau1 = {}
    for name, pipe in _make_models().items():
        if name == 'Voting (LR+ET+HGB)':
            continue
        niveau1[name] = _cv_row(pipe, X_base, y)

    # ── Niveau 2 — Enrichi ──
    niveau2 = {}
    for name, pipe in _make_models().items():
        if name == 'Voting (LR+ET+HGB)':
            continue
        niveau2[name] = _cv_row(pipe, X_enrich, y)

    # ── Niveau 3 — Optimisé (VotingClassifier) ──
    lr2  = Pipeline([('sc', StandardScaler()), ('m', LogisticRegression(max_iter=1000, random_state=42))])
    et2  = Pipeline([('m', ExtraTreesClassifier(n_estimators=100, random_state=42))])
    hgb2 = Pipeline([('m', HistGradientBoostingClassifier(random_state=42))])
    voting = VotingClassifier([('lr', lr2), ('et', et2), ('hgb', hgb2)], voting='soft')
    niveau3 = {'Voting (LR+ET+HGB)': _cv_row(voting, X_enrich, y)}

    # Meilleur modèle niveau 2
    best_name  = max(niveau2, key=lambda m: niveau2[m]['f1_mean'])
    best_scores = niveau2[best_name]

    # Progression F1
    f1_base    = max(s['f1_mean'] for s in niveau1.values())
    f1_enrich  = max(s['f1_mean'] for s in niveau2.values())
    f1_optimise = niveau3['Voting (LR+ET+HGB)']['f1_mean']

    # Tous les modèles niveau 2 pour l'affichage dashboard
    all_scores = {**niveau2, **niveau3}

    return {
        'niveau1':    niveau1,
        'niveau2':    niveau2,
        'niveau3':    niveau3,
        'all_scores': all_scores,
        'best_model': best_name,
        'best_scores': best_scores,
        'progression': {
            'base':     round(f1_base, 3),
            'enrichi':  round(f1_enrich, 3),
            'optimise': round(f1_optimise, 3),
        },
        'feature_importance_fig': _fi_figure(df_ml, y),
    }
