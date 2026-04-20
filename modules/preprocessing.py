"""
preprocessing.py
----------------
Chargement et feature engineering du dataset hospitalier.
Toutes les transformations de données passent par ce module.
"""

import pandas as pd
import numpy as np


# ── Constantes ──────────────────────────────────────────────────────────────

DATA_PATH = "data/hospital_data.csv"

TRANCHES_AGE = [0, 20, 30, 40, 50, 60, 120]
LABELS_TRANCHES = ["0-20", "20-30", "30-40", "40-50", "50-60", "+60"]

SAISONS = {
    1: "Hiver", 2: "Hiver",
    3: "Printemps", 4: "Printemps", 5: "Printemps",
    6: "Été", 7: "Été", 8: "Été",
    9: "Automne", 10: "Automne", 11: "Automne",
    12: "Hiver"
}

NOMS_MOIS = {
    1: "Jan", 2: "Fév", 3: "Mar", 4: "Avr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Aoû",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Déc"
}


# ── Chargement ───────────────────────────────────────────────────────────────

def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    """
    Charge le CSV et parse les colonnes de dates.

    Returns
    -------
    pd.DataFrame : données brutes avec DateAdmission et DateSortie en datetime.
    """
    df = pd.read_csv(path, sep=";")
    df["DateAdmission"] = pd.to_datetime(df["DateAdmission"], format="%d/%m/%Y")
    df["DateSortie"] = pd.to_datetime(df["DateSortie"], format="%d/%m/%Y")
    return df


# ── Feature Engineering ──────────────────────────────────────────────────────

def add_tranche_age(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute la colonne TrancheAge (catégorie d'âge)."""
    df = df.copy()
    df["TrancheAge"] = pd.cut(
        df["Age"],
        bins=TRANCHES_AGE,
        labels=LABELS_TRANCHES,
        right=False
    )
    return df


def add_mois_admission(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute MoisAdmission (entier 1-12) et MoisLabel (abréviation FR)."""
    df = df.copy()
    df["MoisAdmission"] = df["DateAdmission"].dt.month
    df["MoisLabel"] = df["MoisAdmission"].map(NOMS_MOIS)
    return df


def add_cout_par_jour(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute CoutParJour = Cout / DureeSejour. Évite la division par zéro."""
    df = df.copy()
    df["CoutParJour"] = df.apply(
        lambda row: round(row["Cout"] / row["DureeSejour"], 2)
        if row["DureeSejour"] > 0 else 0,
        axis=1
    )
    return df


def add_sejour_long(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute SejourLong (variable cible ML binaire).
    SejourLong = 1 si DureeSejour > médiane, 0 sinon.
    """
    df = df.copy()
    mediane = df["DureeSejour"].median()
    df["SejourLong"] = (df["DureeSejour"] > mediane).astype(int)
    df.attrs["mediane_sejour"] = mediane  # stockée pour affichage dans le rapport
    return df


def add_saison(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute Saison à partir de MoisAdmission."""
    if "MoisAdmission" not in df.columns:
        df = add_mois_admission(df)
    df = df.copy()
    df["Saison"] = df["MoisAdmission"].map(SAISONS)
    return df


# ── Pipeline complet ─────────────────────────────────────────────────────────

def preprocess(path: str = DATA_PATH) -> pd.DataFrame:
    """
    Pipeline complet : chargement + toutes les transformations.

    Returns
    -------
    pd.DataFrame enrichi avec toutes les colonnes dérivées.
    """
    df = load_data(path)
    df = add_tranche_age(df)
    df = add_mois_admission(df)
    df = add_cout_par_jour(df)
    df = add_sejour_long(df)
    df = add_saison(df)
    return df


def apply_filters(
    df: pd.DataFrame,
    departements: list = None,
    sexes: list = None,
    tranches_age: list = None
) -> pd.DataFrame:
    """
    Filtre le DataFrame selon les sélections du dashboard.

    Parameters
    ----------
    df : DataFrame préprocessé
    departements : liste de départements sélectionnés (None = tous)
    sexes : liste de sexes sélectionnés (None = tous)
    tranches_age : liste de tranches d'âge sélectionnées (None = toutes)

    Returns
    -------
    pd.DataFrame filtré
    """
    filtered = df.copy()

    if departements:
        filtered = filtered[filtered["Departement"].isin(departements)]
    if sexes:
        filtered = filtered[filtered["Sexe"].isin(sexes)]
    if tranches_age:
        filtered = filtered[filtered["TrancheAge"].isin(tranches_age)]

    return filtered


def get_kpis(df: pd.DataFrame) -> dict:
    """
    Calcule les 3 KPIs principaux à partir du DataFrame filtré.

    Returns
    -------
    dict avec clés : nb_patients, cout_moyen, duree_moyenne
    """
    return {
        "nb_patients": len(df),
        "cout_moyen": round(df["Cout"].mean(), 2) if len(df) > 0 else 0,
        "duree_moyenne": round(df["DureeSejour"].mean(), 1) if len(df) > 0 else 0,
    }


# ── Options pour les filtres Dash ────────────────────────────────────────────

def get_filter_options(df: pd.DataFrame) -> dict:
    """
    Retourne les options de dropdown pour les filtres du dashboard.

    Returns
    -------
    dict avec clés : departements, sexes, tranches_age
    """
    return {
        "departements": sorted(df["Departement"].unique().tolist()),
        "sexes": sorted(df["Sexe"].unique().tolist()),
        "tranches_age": LABELS_TRANCHES,
    }


# ── Script de vérification ───────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Test preprocessing.py ===")
    try:
        df = preprocess()
        print(f"✅ Dataset chargé : {len(df)} patients, {len(df.columns)} colonnes")
        print(f"\nColonnes : {list(df.columns)}")
        print(f"\nAperçu :\n{df.head(3).to_string()}")
        print(f"\nKPIs globaux : {get_kpis(df)}")
        print(f"Médiane DureeSejour : {df.attrs.get('mediane_sejour', 'N/A')}")
        print(f"\nDistribution SejourLong :\n{df['SejourLong'].value_counts()}")
    except FileNotFoundError:
        print("⚠️  Fichier CSV non trouvé — place hospital_data.csv dans data/")
