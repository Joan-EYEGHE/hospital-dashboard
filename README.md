# 🏥 Hospital Dashboard — Analyse & Prédiction de Séjours Hospitaliers

> Dashboard interactif de visualisation et de Machine Learning pour l'analyse des données hospitalières.  
> Projet M2 CDSD — Data Visualisation & Machine Learning | ISM Dakar

---

## 📌 Objectifs métier

1. **Optimisation des coûts** — Identifier quels départements, maladies et profils patients génèrent les coûts les plus élevés.
2. **Anticipation des séjours longs** — Prédire dès l'admission si un patient est susceptible de rester longtemps à l'hôpital.

---

## 🗂️ Structure du projet

```
hospital-dashboard/
├── app.py                  # Point d'entrée Dash — layout + callbacks
├── data/
│   └── hospital_data.csv   # Dataset 500 patients (séparateur ;)
├── modules/
│   ├── __init__.py
│   ├── preprocessing.py    # Nettoyage + feature engineering
│   ├── figures.py          # Graphiques Plotly
│   └── rapport.py          # Génération du rapport HTML téléchargeable
├── assets/
│   └── style.css           # Styles globaux du dashboard
├── requirements.txt
└── README.md
```

---

## 📊 Fonctionnalités du dashboard

### KPIs
- Nombre total de patients
- Coût moyen de séjour
- Durée moyenne de séjour

### Filtres interactifs
- Département
- Sexe
- Tranche d'âge

### Visualisations (6 graphiques)
| # | Graphique | Objectif |
|---|-----------|----------|
| 1 | Distribution des âges par tranche | Profil démographique |
| 2 | Coût moyen par département | Identification des coûts |
| 3 | Durée de séjour par maladie | Charge opérationnelle |
| 4 | Répartition des traitements (pie) | Mix thérapeutique |
| 5 | Évolution des admissions par mois | Saisonnalité |
| 6 | Scatter Coût vs Durée de séjour | Corrélation coût/durée |

### Machine Learning
- **Modèles :** Régression Logistique + Random Forest
- **Variable cible :** `SejourLong` (séjour > médiane → 1, sinon 0)
- **Évaluation :** Cross-Validation (F1-score)
- **Interprétabilité :** Importance des features affichée

### Export
- Bouton de téléchargement d'un **rapport HTML** complet (KPIs + graphiques + résultats ML)

---

## ⚙️ Installation locale

```bash
# 1. Cloner le dépôt
git clone https://github.com/<ton-username>/hospital-dashboard.git
cd hospital-dashboard

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer le dashboard
python app.py
```

Ouvrir dans le navigateur : [http://127.0.0.1:8050](http://127.0.0.1:8050)

---

## 📦 Dataset

- **Fichier :** `data/hospital_data.csv`
- **Séparateur :** `;`
- **500 patients**, aucune valeur manquante
- **Colonnes :** `PatientID`, `Age`, `Sexe`, `Departement`, `Maladie`, `DureeSejour`, `Cout`, `DateAdmission`, `DateSortie`, `Traitement`

**Variables dérivées créées en preprocessing :**
- `TrancheAge` : 0-20 / 20-30 / 30-40 / 40-50 / 50-60 / +60
- `MoisAdmission` : mois extrait de `DateAdmission`
- `CoutParJour` : `Cout / DureeSejour`
- `SejourLong` : `DureeSejour > médiane` → 1 / 0 (variable cible ML)
- `Saison` : Printemps / Été / Automne / Hiver

---

## 🚀 Déploiement

Application déployée sur **Render** :  
🔗 **[https://hospital-dashboard.onrender.com](https://hospital-dashboard.onrender.com)** *(lien à mettre à jour après déploiement)*

---

## 🛠️ Stack technique

| Outil | Usage |
|-------|-------|
| Python 3.10+ | Langage principal |
| Dash + Plotly | Dashboard interactif |
| Pandas | Manipulation de données |
| Scikit-learn | Modèles ML |
| Gunicorn | Serveur WSGI (Render) |

---

## 👩‍💻 Auteur

**Joan** — M2 CDSD, ISM Dakar  
Projet académique — Data Visualisation & Machine Learning
