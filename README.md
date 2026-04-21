# Hospital Dashboard — Analyse & Prédiction de Séjours Hospitaliers

> Dashboard interactif de visualisation et de Machine Learning pour l'analyse des données hospitalières.  
> Projet M2 CDSD — Data Visualisation & Machine Learning | ISM Dakar

---

## Objectifs métier

1. **Optimisation des coûts** — Identifier quels départements, maladies et profils patients génèrent les coûts les plus élevés.
2. **Anticipation des séjours longs** — Prédire dès l'admission si un patient est susceptible de rester longtemps à l'hôpital.

---

## Structure du projet

```
hospital-dashboard/
├── app.py                  # Point d'entrée Dash — layout + callbacks
├── data/
│   └── hospital_data.csv   # Dataset 500 patients (séparateur ;)
├── modules/
│   ├── __init__.py
│   ├── preprocessing.py    # Chargement + feature engineering
│   ├── figures.py          # 6 graphiques Plotly
│   ├── ml.py               # Pipeline ML 3 niveaux (6 modèles)
│   └── rapport.py          # Génération du rapport HTML téléchargeable
├── assets/
│   └── style.css           # Styles globaux du dashboard
├── requirements.txt
└── README.md
```

---

## Fonctionnalités du dashboard

### KPIs (4 indicateurs)
- Nombre total de patients
- Coût moyen de séjour (FCFA)
- Durée moyenne de séjour (jours)
- Taux de séjours longs (%)

### Filtres interactifs
- Département
- Sexe
- Tranche d'âge

### Visualisations (6 graphiques)
| # | Graphique | Objectif |
|---|-----------|----------|
| 1 | Distribution des âges par tranche | Profil démographique |
| 2 | Coût moyen par département (FCFA) | Identification des coûts |
| 3 | Durée de séjour par maladie | Charge opérationnelle |
| 4 | Répartition des traitements (pie) | Mix thérapeutique |
| 5 | Évolution des admissions par mois | Saisonnalité |
| 6 | Scatter Coût vs Durée de séjour | Corrélation coût/durée |

### Machine Learning — Pipeline 3 niveaux

**Variable cible :** `SejourLong` (DureeSejour > médiane 8 j → 1, sinon 0)

| Niveau | Features | Modèles |
|--------|----------|---------|
| 1 — Base | 6 features brutes | Logistic Regression, Decision Tree, Random Forest, Extra Trees, HistGradientBoosting |
| 2 — Enrichi | 11 features + termes d'interaction | Mêmes 5 modèles |
| 3 — Optimisé | 11 features enrichies | VotingClassifier (LR + ExtraTrees + HGB, soft voting) |

**Évaluation :** Cross-Validation stratifiée 5 folds — F1-score, Accuracy, Précision, Rappel  
**Interprétabilité :** Importance des features (Random Forest) affichée dans le dashboard

### Export
- Bouton de téléchargement d'un **rapport HTML** complet (KPIs + graphiques + résultats ML)  
- Le rapport est autonome (Bootstrap CDN + Plotly inline) — s'ouvre sans serveur actif

---

## Installation locale

```bash
# 1. Cloner le dépôt
git clone https://github.com/<ton-username>/hospital-dashboard.git
cd hospital-dashboard

# 2. Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer le dashboard
python app.py
```

Ouvrir dans le navigateur : [http://127.0.0.1:8050](http://127.0.0.1:8050)

---

## Dataset

- **Fichier :** `data/hospital_data.csv`
- **Séparateur :** `;`
- **500 patients**, aucune valeur manquante
- **Colonnes brutes :** `PatientID`, `Age`, `Sexe`, `Departement`, `Maladie`, `DureeSejour`, `Cout`, `DateAdmission`, `DateSortie`, `Traitement`

**Variables dérivées créées par `preprocessing.py` :**
| Colonne | Description |
|---------|-------------|
| `TrancheAge` | Catégorie d'âge : 0-20 / 20-30 / 30-40 / 40-50 / 50-60 / +60 |
| `MoisAdmission` | Mois d'admission (entier 1–12) |
| `MoisLabel` | Abréviation FR du mois (Jan, Fév, …) |
| `CoutParJour` | `Cout / DureeSejour` |
| `SejourLong` | Cible ML binaire — `DureeSejour > médiane` → 1 / 0 |
| `Saison` | Printemps / Été / Automne / Hiver |

---

## Déploiement

Application déployée sur **Render** (WSGI via Gunicorn) :  
L'objet `server` exporté depuis `app.py` est le point d'entrée WSGI.

```bash
gunicorn app:server --bind 0.0.0.0:8080
```

---

## Stack technique

| Outil | Version | Usage |
|-------|---------|-------|
| Python | 3.10+ | Langage principal |
| Dash | 4.1.0 | Framework dashboard |
| Plotly | 6.7.0 | Graphiques interactifs |
| dash-bootstrap-components | 2.0.4 | UI / Bootstrap 5.3.2 |
| Pandas | 3.0.2 | Manipulation de données |
| NumPy | 2.4.4 | Calculs numériques |
| scikit-learn | 1.8.0 | Modèles ML |
| SciPy | 1.15.3 | Dépendance scikit-learn |
| Gunicorn | 22.0.0 | Serveur WSGI (Render) |

---

## Auteur

**Joan** — M2 CDSD, ISM Dakar  
Projet académique — Data Visualisation & Machine Learning
