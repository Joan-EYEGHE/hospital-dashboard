"""
ml.py
-----
Module Machine Learning — Prédiction de SejourLong.
Modèles : Régression Logistique + Random Forest.
Évaluation : Cross-Validation 5 folds, F1-score.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_validate, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
import plotly.express as px
import plotly.graph_objects as go


# ── Feature engineering ML ──────────────────────────────────────────────────

def build_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Construit la matrice X et le vecteur cible y pour l'entraînement.

    Features retenues :
    - Age (numérique)
    - DureeSejour (exclu de la cible — inclus pour cohérence si besoin futur)
    - Cout, CoutParJour
    - Departement, Sexe, Maladie, Traitement, Saison (encodés)

    Returns
    -------
    X : pd.DataFrame
    y : pd.Series (SejourLong)
    """
    features_num = ["Age", "Cout", "CoutParJour"]
    features_cat = ["Departement", "Sexe", "Maladie", "Traitement", "Saison"]

    df_ml = df.copy()

    # Encodage des catégorielles
    encoders = {}
    for col in features_cat:
        le = LabelEncoder()
        df_ml[col + "_enc"] = le.fit_transform(df_ml[col].astype(str))
        encoders[col] = le

    features_enc = [c + "_enc" for c in features_cat]
    X = df_ml[features_num + features_enc].copy()
    y = df_ml["SejourLong"]

    return X, y


def _cv_scores(model, X, y, cv) -> dict:
    """Lance une cross-validation et retourne les métriques agrégées."""
    scoring = ["f1", "accuracy", "precision", "recall"]
    results = cross_validate(model, X, y, cv=cv, scoring=scoring, n_jobs=-1)
    return {
        "f1_mean":    float(np.mean(results["test_f1"])),
        "f1_std":     float(np.std(results["test_f1"])),
        "accuracy":   float(np.mean(results["test_accuracy"])),
        "precision":  float(np.mean(results["test_precision"])),
        "recall":     float(np.mean(results["test_recall"])),
    }


def _feature_importance_fig(rf_model, feature_names: list) -> go.Figure:
    """Retourne le graphique d'importance des features du Random Forest."""
    importances = rf_model.named_steps["rf"].feature_importances_
    fi = (
        pd.DataFrame({"Feature": feature_names, "Importance": importances})
        .sort_values("Importance", ascending=True)
        .tail(10)  # top 10
    )

    fig = px.bar(
        fi,
        x="Importance",
        y="Feature",
        orientation="h",
        title="Importance des variables (Random Forest)",
        color="Importance",
        color_continuous_scale=["#A8DADC", "#457B9D", "#1D3557"],
        labels={"Importance": "Importance", "Feature": ""},
    )
    fig.update_layout(
        font_family="'Segoe UI', sans-serif",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=50, b=40),
        coloraxis_showscale=False,
        title_font_size=15,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#f0f0f0")
    return fig


# ── Pipeline principal ───────────────────────────────────────────────────────

def train_and_evaluate(df: pd.DataFrame) -> dict:
    """
    Entraîne et évalue Régression Logistique + Random Forest sur df.

    Returns
    -------
    dict {
        "Régression Logistique": { f1_mean, f1_std, accuracy, precision, recall },
        "Random Forest":         { f1_mean, f1_std, accuracy, precision, recall },
        "feature_importance_fig": go.Figure,
    }
    """
    X, y = build_features(df)
    feature_names = list(X.columns)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # — Régression Logistique —
    pipe_lr = Pipeline([
        ("scaler", StandardScaler()),
        ("lr", LogisticRegression(max_iter=1000, random_state=42)),
    ])
    scores_lr = _cv_scores(pipe_lr, X, y, cv)

    # — Random Forest —
    pipe_rf = Pipeline([
        ("rf", RandomForestClassifier(n_estimators=100, random_state=42)),
    ])
    scores_rf = _cv_scores(pipe_rf, X, y, cv)

    # Entraîner le RF sur tout le dataset pour l'importance des features
    pipe_rf.fit(X, y)
    fi_fig = _feature_importance_fig(pipe_rf, feature_names)

    return {
        "Régression Logistique": scores_lr,
        "Random Forest": scores_rf,
        "feature_importance_fig": fi_fig,
    }
