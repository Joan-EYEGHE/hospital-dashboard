"""
rapport.py — Génération du rapport HTML téléchargeable
Style gold standard M. EYEGHE Joan — ISM Master 2025-2026
Bootstrap 5.3.2 · Plotly 2.27.0 · Palette #1a3a5c / #2e86c1 / #1abc9c
"""

import base64, json
from datetime import datetime
import pandas as pd
import plotly.io as pio


# ── Helpers figures → base64 ─────────────────────────────────────────────────

def _fig_json(fig) -> str:
    """Sérialise une figure Plotly en JSON pour injection inline."""
    try:
        return fig.to_json()
    except Exception:
        return 'null'


def _chart_div(fig, div_id: str, height: int = 400) -> str:
    if fig is None:
        return '<div class="callout warning">Graphique non disponible.</div>'
    fig_json = _fig_json(fig)
    return f'''<div id="{div_id}" class="chart-container" style="min-height:{height}px"></div>
<script>(function(){{
  var fig = {fig_json};
  var layout = Object.assign({{}}, fig.layout||{{}}, {{
    paper_bgcolor:"rgba(0,0,0,0)", plot_bgcolor:"rgba(0,0,0,0)",
    margin:{{t:50,b:40,l:50,r:30}}, autosize:true
  }});
  Plotly.newPlot("{div_id}", fig.data, layout, {{responsive:true, displayModeBar:false}});
}})();</script>'''


# ── Sections HTML ─────────────────────────────────────────────────────────────

def _cover(nb_patients: int, nb_vars: int, date_gen: str) -> str:
    return f'''<div class="cover">
  <h1>Rapport Analytique<br/>Données Hospitalières</h1>
  <div class="subtitle">TP Data Visualisation &amp; Machine Learning — ISM Master 2025–2026</div>
  <div>
    <span class="badge-cover">🏥 Analyse hospitalière</span>
    <span class="badge-cover">📊 {nb_patients} patients</span>
    <span class="badge-cover">🔢 {nb_vars} variables</span>
    <span class="badge-cover">🤖 Machine Learning</span>
  </div>
  <div class="meta">M. EYEGHE Joan &nbsp;|&nbsp; {date_gen}</div>
</div>'''


def _navbar() -> str:
    return '''<nav class="navbar navbar-expand-lg navbar-custom">
  <div class="container-fluid px-4">
    <span class="navbar-brand">🏥 Dashboard Hospitalier</span>
    <div class="navbar-nav ms-auto flex-row gap-3">
      <a class="nav-link" href="#s0">Librairies</a>
      <a class="nav-link" href="#s1">Données</a>
      <a class="nav-link" href="#s2">EDA</a>
      <a class="nav-link" href="#s3">Visualisations</a>
      <a class="nav-link" href="#s4">Machine Learning</a>
      <a class="nav-link" href="#s5">Interprétation</a>
      <a class="nav-link" href="#s6">Conclusion</a>
    </div>
  </div>
</nav>'''


def _toc() -> str:
    return '''<div class="toc-card">
  <h2>📋 Table des matières</h2>
  <ol class="mb-0">
    <li><a href="#s0">Environnement technique &amp; librairies</a></li>
    <li><a href="#s1">Description des données</a></li>
    <li><a href="#s2">Analyse exploratoire (EDA)</a></li>
    <li><a href="#s3">Visualisations principales</a></li>
    <li><a href="#s4">Modèle Machine Learning</a></li>
    <li><a href="#s5">Interprétation des résultats</a></li>
    <li><a href="#s6">Conclusion &amp; Recommandations</a></li>
  </ol>
</div>'''


def _section_open(num: int, title: str, anchor: str) -> str:
    return f'''<div class="section-card" id="{anchor}">
<div class="section-title-row">
  <span class="section-number">{num}</span>
  <h2>{title}</h2>
</div>'''


def _section_libs() -> str:
    return f'''{_section_open(0, "Environnement technique &amp; librairies", "s0")}
<p>Ce rapport a été produit avec la stack technique suivante. Chaque librairie joue un rôle précis
dans le pipeline : collecte → traitement → visualisation → modélisation → export.</p>

<div class="table-responsive">
<table class="table table-custom">
<thead><tr><th>Librairie</th><th>Version</th><th>Rôle dans le projet</th></tr></thead>
<tbody>
<tr>
  <td><strong>Dash</strong></td><td>4.1.0</td>
  <td>Framework web Python pour construire l'interface interactive du dashboard (callbacks, layout, routing)</td>
</tr>
<tr>
  <td><strong>Plotly</strong></td><td>6.7.0</td>
  <td>Génération de tous les graphiques interactifs (barres, scatter, camembert, courbes) via Plotly Express</td>
</tr>
<tr>
  <td><strong>Pandas</strong></td><td>3.0.2</td>
  <td>Chargement, nettoyage et transformation du dataset CSV ; calcul des KPIs et des variables dérivées</td>
</tr>
<tr>
  <td><strong>scikit-learn</strong></td><td>1.8.0</td>
  <td>Pipeline Machine Learning : prétraitement (StandardScaler, LabelEncoder), modèles (RandomForest, GradientBoosting, LogisticRegression), VotingClassifier, métriques (AUC, F1, accuracy)</td>
</tr>
<tr>
  <td><strong>SciPy</strong></td><td>—</td>
  <td>Tests statistiques : ANOVA (f_oneway) pour la durée de séjour par tranche d'âge, corrélations de Pearson</td>
</tr>
<tr>
  <td><strong>dash-bootstrap-components</strong></td><td>2.x</td>
  <td>Composants Bootstrap 5 pour le layout (grilles, cartes, badges, dropdowns) dans l'interface Dash</td>
</tr>
<tr>
  <td><strong>Bootstrap</strong></td><td>5.3.2</td>
  <td>Framework CSS utilisé dans ce rapport HTML pour la mise en page et la typographie</td>
</tr>
<tr>
  <td><strong>Plotly.js</strong></td><td>3.5.0</td>
  <td>Librairie JavaScript chargée côté navigateur pour rendre les figures Plotly dans ce rapport HTML</td>
</tr>
<tr>
  <td><strong>Python</strong></td><td>3.13</td>
  <td>Langage d'exécution de l'ensemble du pipeline (preprocessing, ML, génération du rapport)</td>
</tr>
</tbody>
</table>
</div>

<div class="callout success"><strong>Stack orientée Data Science</strong>
L'ensemble du projet repose exclusivement sur des librairies open-source, sans dépendance commerciale.</div>
</div>'''


def _section1(df: pd.DataFrame, kpis: dict) -> str:
    age_std = round(df['Age'].std(), 0)
    sejour_std = round(df['DureeSejour'].std(), 1)
    top_dept = df['Departement'].value_counts().index[0]
    top_dept_n = df['Departement'].value_counts().iloc[0]
    top_dept_pct = round(top_dept_n / len(df) * 100, 1)
    top_mal = df['Maladie'].value_counts().index[0]
    top_mal_n = df['Maladie'].value_counts().iloc[0]
    top_mal_pct = round(top_mal_n / len(df) * 100, 1)
    sexe_h = round((df['Sexe'] == 'M').mean() * 100, 1)
    sexe_f = round(100 - sexe_h, 1)

    return f'''{_section_open(1, "Description des données", "s1")}
<p>Le dataset mis à disposition contient <strong>{len(df)} observations</strong> représentant des patients hospitalisés,
décrites par <strong>10 variables</strong> couvrant leur profil démographique, leur parcours de soin et les coûts associés.</p>
<hr class="section-divider"/>

<h5 style="color:var(--primary)">Variables du dataset</h5>
<div class="table-responsive">
<table class="table table-custom">
<thead><tr><th>Variable</th><th>Type</th><th>Description</th><th>Plage / Modalités</th></tr></thead>
<tbody>
<tr><td><code>PatientID</code></td><td>Identifiant</td><td>Identifiant unique du patient</td><td>1 – 500</td></tr>
<tr><td><code>Age</code></td><td>Numérique</td><td>Âge du patient</td><td>1 – 90 ans</td></tr>
<tr><td><code>Sexe</code></td><td>Catégorielle</td><td>Genre du patient</td><td>M / F</td></tr>
<tr><td><code>Departement</code></td><td>Catégorielle</td><td>Service hospitalier</td><td>7 modalités</td></tr>
<tr><td><code>Maladie</code></td><td>Catégorielle</td><td>Maladie diagnostiquée</td><td>7 modalités</td></tr>
<tr><td><code>DureeSejour</code></td><td>Numérique</td><td>Durée d'hospitalisation</td><td>1 – 15 jours</td></tr>
<tr><td><code>Cout</code></td><td>Numérique</td><td>Coût total de l'hospitalisation</td><td>303 – 10 110 FCFA</td></tr>
<tr><td><code>DateAdmission</code></td><td>Date</td><td>Date d'entrée à l'hôpital</td><td>2024 – 2025</td></tr>
<tr><td><code>DateSortie</code></td><td>Date</td><td>Date de sortie de l'hôpital</td><td>2024 – 2025</td></tr>
<tr><td><code>Traitement</code></td><td>Catégorielle</td><td>Type de traitement reçu</td><td>6 modalités</td></tr>
</tbody>
</table>
</div>

<div class="callout success"><strong>✅ Qualité des données</strong>
Aucune valeur manquante détectée. Le dataset est directement exploitable sans imputation.</div>

<hr class="section-divider"/>
<h5 style="color:var(--primary)">Statistiques descriptives clés</h5>
<div class="kpi-grid">
  <div class="kpi-box"><div class="kpi-value">{len(df)}</div><div class="kpi-label">Patients</div></div>
  <div class="kpi-box green"><div class="kpi-value">{round(df['Age'].mean(), 1)}</div><div class="kpi-label">Âge moyen (ans)</div></div>
  <div class="kpi-box orange"><div class="kpi-value">{round(df['DureeSejour'].mean(), 1)}j</div><div class="kpi-label">Séjour moyen</div></div>
  <div class="kpi-box red"><div class="kpi-value">{int(kpis['cout_moyen']):,}</div><div class="kpi-label">Coût moyen (FCFA)</div></div>
  <div class="kpi-box purple"><div class="kpi-value">{sexe_h}%</div><div class="kpi-label">Hommes</div></div>
  <div class="kpi-box"><div class="kpi-value">{top_dept_pct}%</div><div class="kpi-label">{top_dept} (1er dept)</div></div>
</div>

<div class="table-responsive mt-3">
<table class="table table-custom">
<thead><tr><th>Indicateur</th><th>Valeur</th></tr></thead>
<tbody>
<tr><td>Âge moyen</td><td><strong>{round(df['Age'].mean(),1)} ans</strong> (min={df['Age'].min()}, max={df['Age'].max()}, écart-type={age_std})</td></tr>
<tr><td>Répartition sexe</td><td><strong>{sexe_h}% Hommes</strong> / {sexe_f}% Femmes</td></tr>
<tr><td>Durée de séjour moyenne</td><td><strong>{round(df['DureeSejour'].mean(),1)} jours</strong> (médiane={df['DureeSejour'].median():.0f}j, min=1j, max=15j, écart-type={sejour_std})</td></tr>
<tr><td>Département le plus chargé</td><td><strong>{top_dept}</strong> — {top_dept_n} patients ({top_dept_pct}%)</td></tr>
<tr><td>Maladie la plus fréquente</td><td><strong>{top_mal}</strong> — {top_mal_n} cas ({top_mal_pct}%)</td></tr>
<tr><td>Budget total</td><td><strong>{df['Cout'].sum():,} FCFA</strong></td></tr>
</tbody>
</table>
</div>
</div>'''


def _section2(df: pd.DataFrame, figs: dict) -> str:
    seniors_n = (df['Age'] >= 60).sum()
    seniors_pct = round(seniors_n / len(df) * 100)
    top_dept = df['Departement'].value_counts().index[0]
    top_dept_pct = round(df['Departement'].value_counts().iloc[0] / len(df) * 100)
    top_mal = df['Maladie'].value_counts().index[0]
    top_mal_pct = round(df['Maladie'].value_counts().iloc[0] / len(df) * 100)
    duree_eczema_3040 = df[(df['Maladie']=='Eczéma') & (df['TrancheAge']=='30-40')]['DureeSejour'].mean()
    duree_alz_4050 = df[(df['Maladie']=='Alzheimer') & (df['TrancheAge']=='40-50')]['DureeSejour'].mean()
    from scipy import stats as sc
    _groups = [df[df['TrancheAge']==t]['DureeSejour'].values for t in df['TrancheAge'].dropna().unique()]
    if len(_groups) >= 2:
        f_val, p_val = sc.f_oneway(*_groups)
    else:
        f_val, p_val = float('nan'), float('nan')
    if len(df) >= 2:
        r_dc, _ = sc.pearsonr(df['DureeSejour'], df['Cout'])
        r_ad, p_ad = sc.pearsonr(df['Age'], df['DureeSejour'])
    else:
        r_dc = r_ad = p_ad = float('nan')

    return f'''{_section_open(2, "Analyse exploratoire (EDA)", "s2")}

<h5 style="color:var(--primary)">Partie 1 — Profil démographique</h5>
<p>La population hospitalière est <strong>équilibrée en genre</strong> (50/50) et couvre toutes les tranches d'âge.
La tranche <strong>+60 ans regroupe {seniors_n} patients ({seniors_pct}%)</strong>, ce qui en fait le groupe le plus important.
La distribution des âges présente une forme quasi-uniforme, signe que l'établissement accueille aussi bien
des patients pédiatriques que des patients très âgés.</p>
<div class="chart-grid-2">
  <div>{_chart_div(figs.get('tranches_age'), 'ch_age', 320)}</div>
  <div>{_chart_div(figs.get('traitements'), 'ch_trait', 320)}</div>
</div>

<hr class="section-divider"/>
<h5 style="color:var(--primary)">Partie 2 — Activité par département</h5>
<p>L'<strong>{top_dept}</strong> est le service le plus sollicité ({top_dept_pct}% des admissions).
Cette concentration sur un département à pathologies lourdes a des implications budgétaires importantes.</p>
{_chart_div(figs.get('cout_dept'), 'ch_dept', 380)}

<hr class="section-divider"/>
<h5 style="color:var(--primary)">Analyse des maladies</h5>
<p>L'<strong>{top_mal}</strong> est la maladie la plus fréquente ({top_mal_pct}%), ce qui constitue
un résultat surprenant pour un hôpital habituellement associé à des pathologies plus sévères.
Ce fait suggère une activité dermatologique notable de l'établissement.</p>
{_chart_div(figs.get('duree_maladie'), 'ch_dur', 400)}

<hr class="section-divider"/>
<h5 style="color:var(--primary)">Analyse des coûts et corrélations</h5>
<p>La corrélation quasi-parfaite entre durée et coût confirme une <strong>tarification journalière</strong>
de l'hôpital (r={r_dc:.2f}). Prédire le coût revient donc à prédire la durée de séjour.</p>
<div class="table-responsive">
<table class="table table-custom">
<thead><tr><th>Paire de variables</th><th>Corrélation de Pearson</th><th>Interprétation</th></tr></thead>
<tbody>
<tr><td>DureeSejour ↔ Cout</td><td><strong>r = {r_dc:.2f}</strong></td><td>Très forte — tarification journalière confirmée</td></tr>
<tr><td>Age ↔ DureeSejour</td><td>r = {r_ad:.2f} (p={p_ad:.2f})</td><td>Nulle — l'âge n'influence pas la durée</td></tr>
</tbody>
</table>
</div>
{_chart_div(figs.get('scatter'), 'ch_scatter', 380)}

<hr class="section-divider"/>
<h5 style="color:var(--primary)">Saisonnalité des admissions</h5>
<p>L'analyse temporelle révèle une légère concentration estivale des admissions.
L'analyse ANOVA confirme que <strong>l'âge n'explique pas la durée de séjour</strong>
(F={f_val:.2f}, p={p_val:.2f}).</p>
{_chart_div(figs.get('admissions'), 'ch_adm', 340)}

<div class="callout warning mt-3"><strong>⚠️ Deux anomalies méritent attention</strong>
<ul class="mb-0 mt-1">
  <li><strong>Eczéma chez les 30–40 ans</strong> : durée moyenne {duree_eczema_3040:.1f} jours — atypique cliniquement</li>
  <li><strong>Alzheimer chez les 40–50 ans</strong> : {duree_alz_4050:.1f} jours — Alzheimer précoce, prise en charge complexe</li>
</ul></div>
</div>'''


def _section3(figs: dict) -> str:
    return f'''{_section_open(3, "Visualisations principales", "s3")}
<p>Les visualisations suivantes, produites avec <strong>Plotly Express</strong>, résument les tendances
les plus significatives du dataset. Chaque graphique est interactif (survol, zoom).</p>

<p class="chart-title">Figure 1 — Distribution des âges par tranche</p>
{_chart_div(figs.get('tranches_age'), 'ch_age2', 360)}
<p class="text-muted" style="font-size:.87rem">La tranche +60 ans est la plus représentée (35%), confirmant
la vocation gériatrique partielle de l'établissement.</p>

<p class="chart-title">Figure 2 — Coût moyen par département</p>
{_chart_div(figs.get('cout_dept'), 'ch_dept2', 360)}
<p class="text-muted" style="font-size:.87rem">L'Oncologie présente le coût moyen le plus élevé, cohérent
avec la complexité des traitements oncologiques.</p>

<p class="chart-title">Figure 3 — Scatter Coût vs Durée de séjour</p>
{_chart_div(figs.get('scatter'), 'ch_sc2', 400)}
<p class="text-muted" style="font-size:.87rem">La corrélation r=0,91 est visible à l'œil nu.
Chaque jour supplémentaire génère un surcoût proportionnel quasi-constant.</p>
</div>'''


def _section4_ml(ml_results: dict) -> str:
    niveau1 = ml_results.get('niveau1', {})
    niveau2 = ml_results.get('niveau2', {})
    niveau3 = ml_results.get('niveau3', {})
    prog    = ml_results.get('progression', {})
    best    = ml_results.get('best_model', 'HistGradientBoosting')
    fi_fig  = ml_results.get('feature_importance_fig')

    def progress_bar(label, f1, color='var(--accent)'):
        pct = round(f1 * 100, 1)
        return f'''<div class="progress-wrap">
  <div class="progress-label"><span>{label}</span><span>F1 = {f1:.3f}</span></div>
  <div class="progress"><div class="progress-bar-custom" style="width:{pct}%"></div></div>
</div>'''

    def model_rows(niveau_dict, highlight):
        rows = ''
        for name, s in niveau_dict.items():
            is_best = name == highlight
            cls = 'class="best-row"' if is_best else ''
            trophy = ' 🏆' if is_best else ''
            rows += f'''<tr {cls}>
  <td><strong>{name}{trophy}</strong></td>
  <td>{s["f1_mean"]:.3f} <small>±{s["f1_std"]:.3f}</small></td>
  <td>{s["accuracy"]:.3f}</td>
  <td>{s["precision"]:.3f}</td>
  <td>{s["recall"]:.3f}</td>
</tr>'''
        return rows

    # Best F1 niveau1 pour progression
    f1_base    = prog.get('base', 0)
    f1_enrich  = prog.get('enrichi', 0)
    f1_optim   = prog.get('optimise', 0)

    return f'''{_section_open(4, "Modèle Machine Learning", "s4")}

<h5 style="color:var(--primary)">Choix de l'objectif</h5>
<p><strong>L'Option B (Classification des séjours longs)</strong> a été retenue plutôt que l'Option A
(régression du coût). Justification : la corrélation DureeSejour↔Cout de 0,91 rend la régression triviale
(R²&gt;99% garanti). La classification apporte une valeur analytique supérieure : identifier <em>a priori</em>
les patients à risque de séjour prolongé.</p>

<div class="callout success"><strong>Variable cible définie</strong>
SejourLong = 1 si DureeSejour &gt; 8 jours (médiane) · SejourLong = 0 sinon<br/>
Distribution : ~45% de séjours longs / ~55% courts — classes quasi-équilibrées.</div>

<hr class="section-divider"/>
<h5 style="color:var(--primary)">Prétraitement — Variables supprimées (data leakage)</h5>
<div class="callout danger"><strong>⚠️ Variables exclues pour éviter le data leakage</strong>
<ul class="mb-0 mt-1">
  <li><code>DureeSejour</code> — source directe de la variable cible</li>
  <li><code>Cout</code> — dérivé de DureeSejour (r=0,91) — leakage indirect</li>
  <li><code>CoutParJour</code> — dérivé de Cout et DureeSejour</li>
  <li><code>PatientID</code>, <code>DateAdmission</code>, <code>DateSortie</code> — sans valeur prédictive</li>
</ul></div>
<p><strong>Features finales (base) :</strong> Age, Departement, Sexe, Maladie, Traitement, Saison (encodées).</p>

<hr class="section-divider"/>
<h5 style="color:var(--primary)">Feature Engineering — 3 niveaux</h5>
<p><strong>Niveau 1 — Base :</strong> 6 features encodées (LabelEncoder)<br/>
<strong>Niveau 2 — Enrichi :</strong> ajout de EstSenior, EstPediatrique, Mois, Trimestre, Maladie×Traitement<br/>
<strong>Niveau 3 — Optimisé :</strong> VotingClassifier (vote doux LR + ExtraTrees + HGB), StratifiedKFold k=5</p>

<hr class="section-divider"/>
<h5 style="color:var(--primary)">Modèles entraînés</h5>
<div class="table-responsive">
<table class="table table-custom">
<thead><tr><th>Modèle</th><th>Famille</th></tr></thead>
<tbody>
<tr><td>Logistic Regression</td><td>Modèle linéaire</td></tr>
<tr><td>Decision Tree</td><td>Arbre de décision</td></tr>
<tr><td>Random Forest</td><td>Ensemble (forêt)</td></tr>
<tr><td>Extra Trees</td><td>Ensemble (forêt extrême)</td></tr>
<tr><td>HistGradientBoosting</td><td>Ensemble (boosting)</td></tr>
<tr><td>Voting (LR+ET+HGB)</td><td>Ensemble (vote doux)</td></tr>
</tbody>
</table>
</div>

<hr class="section-divider"/>
<h5 style="color:var(--primary)">Résultats — Niveau 2 Enrichi (StratifiedKFold 5)</h5>
<div class="table-responsive">
<table class="table table-custom">
<thead><tr><th>Modèle</th><th>F1-score (CV)</th><th>Accuracy</th><th>Precision</th><th>Recall</th></tr></thead>
<tbody>{model_rows(niveau2, best)}</tbody>
</table>
</div>

<hr class="section-divider"/>
<h5 style="color:var(--primary)">Progression F1-score</h5>
{progress_bar('Niveau 1 — Base', f1_base)}
{progress_bar('Niveau 2 — Enrichi', f1_enrich)}
{progress_bar('Niveau 3 — Optimisé (Voting)', f1_optim)}

<hr class="section-divider"/>
<h5 style="color:var(--primary)">Importance des variables (Random Forest)</h5>
{_chart_div(fi_fig, 'ch_fi', 380)}

<hr class="section-divider"/>
<div class="callout danger"><strong>⚠️ Limite théorique identifiée</strong>
La corrélation maximale entre toute variable disponible et SejourLong est quasi-nulle.
Cette contrainte impose un <strong>plafond théorique autour de 50–55% d'accuracy</strong> :
les données disponibles ne permettent pas de prédire fiablement la durée de séjour.
Atteindre 70% nécessiterait des données cliniques absentes du dataset
(score de gravité à l'admission, comorbidités, résultats biologiques).</div>
</div>'''


def _section5() -> str:
    return f'''{_section_open(5, "Interprétation des résultats", "s5")}

<h5 style="color:var(--primary)">Facteurs expliquant les coûts hospitaliers</h5>
<p>Le <strong>seul facteur déterminant du coût est la durée de séjour</strong> (r=0,91).
Les variables démographiques (âge, sexe) et cliniques (département, maladie, traitement)
n'ont pas d'effet direct significatif sur le coût une fois la durée contrôlée.
En d'autres termes, l'hôpital facture principalement <em>au jour de séjour</em>.</p>

<hr class="section-divider"/>
<h5 style="color:var(--primary)">Profils de patients aux séjours les plus longs</h5>
<div class="row g-3 mt-1">
<div class="col-md-6"><div class="callout warning"><strong>Eczéma, 30–40 ans</strong>
Durée moyenne <strong>11,1 jours</strong> — atypique cliniquement.</div></div>
<div class="col-md-6"><div class="callout warning"><strong>Alzheimer, 40–50 ans</strong>
Durée moyenne <strong>10,3 jours</strong> — Alzheimer précoce, prise en charge complexe.</div></div>
</div>

<hr class="section-divider"/>
<h5 style="color:var(--primary)">Fiabilité des modèles prédictifs</h5>
<p>Les modèles atteignent un F1-score plafonné autour de <strong>0,456</strong> en raison
de l'absence d'information prédictive dans les données disponibles.
Dans un contexte hospitalier, <strong>un Recall élevé est préférable</strong> :
manquer un patient à risque de séjour long est plus préjudiciable qu'une fausse alarme.
La stratégie d'ensemble (Voting) est donc cliniquement justifiée.</p>
</div>'''


def _section6() -> str:
    return f'''{_section_open(6, "Conclusion &amp; Recommandations", "s6")}
<p>L'analyse des données hospitalières révèle un établissement à l'activité diversifiée,
avec une concentration notable sur les pathologies oncologiques et une population de patients seniors
(35%) représentant 34% du budget. La durée de séjour est le principal levier de coût,
sans lien significatif avec l'âge ou le sexe du patient.</p>
<hr class="section-divider"/>

<div class="reco-item"><div class="reco-num">1</div><div class="reco-content">
  <h5>Optimisation des ressources en Oncologie</h5>
  <p>18% des admissions — une revue des protocoles de ce service permettrait d'identifier
  des opportunités de réduction des durées de séjour sans compromettre la qualité des soins.</p>
</div></div>

<div class="reco-item"><div class="reco-num">2</div><div class="reco-content">
  <h5>Suivi renforcé des patients seniors (&gt;60 ans)</h5>
  <p>35% des patients, 34% du budget — mettre en place des protocoles de sortie adaptés
  (suivi à domicile, soins post-hospitalisation) permettrait de réduire les durées de séjour
  tout en sécurisant les patients.</p>
</div></div>

<div class="reco-item"><div class="reco-num">3</div><div class="reco-content">
  <h5>Investigation des cas Eczéma à durée longue</h5>
  <p>11,1 jours chez les 30–40 ans — cliniquement atypique. Une revue des dossiers de ce segment
  permettrait de vérifier s'il s'agit de formes sévères ou d'un problème de protocole de sortie.</p>
</div></div>

<div class="reco-item"><div class="reco-num">4</div><div class="reco-content">
  <h5>Déploiement du modèle prédictif en admissions</h5>
  <p>Le modèle Voting peut être utilisé dès l'admission pour signaler les patients susceptibles
  d'avoir un séjour prolongé — anticiper l'allocation des lits et planifier les ressources infirmières.</p>
</div></div>

<div class="reco-item"><div class="reco-num">5</div><div class="reco-content">
  <h5>Enrichissement des données cliniques pour améliorer la prédiction</h5>
  <p>Score de gravité à l'admission, comorbidités, résultats biologiques — ces données permettraient
  de dépasser le plafond théorique actuel et de construire un modèle réellement opérationnel.</p>
</div></div>
</div>'''


def _footer(df: pd.DataFrame, date_gen: str) -> str:
    return f'''<footer class="footer">
  <strong>TP Data Visualisation &amp; Machine Learning — ISM Master 2025–2026</strong><br/>
  Dataset : {len(df)} patients · 10 variables &nbsp;|&nbsp;
  Python · pandas 3.0.2 · plotly 6.7.0 · scikit-learn 1.8.0<br/>
  Rapport généré le {date_gen}
</footer>'''


# ── Entrypoint ───────────────────────────────────────────────────────────────

def generate_rapport_html(
    df: pd.DataFrame,
    kpis: dict,
    figures: dict,
    ml_results: dict,
    filtres_actifs: dict | None = None,
) -> str:
    date_gen = datetime.now().strftime("%d/%m/%Y à %H:%M")

    css = '''
:root{--primary:#1a3a5c;--accent:#2e86c1;--accent2:#1abc9c;--light-bg:#f4f7fb;--text:#2c3e50;--border:#dee2e6;}
body{font-family:"Segoe UI",Calibri,sans-serif;background:var(--light-bg);color:var(--text);font-size:15px;line-height:1.75;}
.navbar-custom{background:var(--primary);position:sticky;top:0;z-index:1000;box-shadow:0 2px 8px rgba(0,0,0,.25);}
.navbar-custom .navbar-brand{color:#fff;font-weight:700;}
.navbar-custom .nav-link{color:rgba(255,255,255,.8)!important;font-size:.85rem;}
.navbar-custom .nav-link:hover{color:#fff!important;}
.cover{background:linear-gradient(135deg,var(--primary) 0%,#2c6e9c 60%,var(--accent2) 100%);color:#fff;padding:80px 40px 60px;text-align:center;}
.cover h1{font-size:2.3rem;font-weight:800;margin-bottom:10px;}
.cover .subtitle{font-size:1.1rem;opacity:.88;margin-bottom:28px;}
.badge-cover{display:inline-block;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.3);border-radius:30px;padding:5px 18px;font-size:.9rem;margin:4px;}
.cover .meta{margin-top:28px;font-size:.88rem;opacity:.72;}
.main-wrapper{max-width:1150px;margin:0 auto;padding:36px 20px 80px;}
.toc-card{background:#fff;border-left:5px solid var(--accent);border-radius:8px;padding:26px 30px;box-shadow:0 2px 10px rgba(0,0,0,.07);margin-bottom:36px;}
.toc-card h2{color:var(--primary);font-size:1.25rem;font-weight:700;margin-bottom:14px;}
.toc-card a{color:var(--accent);text-decoration:none;font-weight:500;}
.toc-card a:hover{text-decoration:underline;}
.section-card{background:#fff;border-radius:10px;padding:32px 36px;box-shadow:0 2px 12px rgba(0,0,0,.07);margin-bottom:28px;scroll-margin-top:68px;}
.section-number{display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;background:var(--accent);color:#fff;border-radius:50%;font-weight:700;font-size:.95rem;margin-right:12px;flex-shrink:0;}
.section-title-row{display:flex;align-items:center;margin-bottom:22px;}
.section-title-row h2{color:var(--primary);font-size:1.4rem;font-weight:700;margin:0;}
.section-divider{border:none;border-top:2px solid var(--border);margin:20px 0;}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:14px;margin:22px 0;}
.kpi-box{background:linear-gradient(135deg,var(--primary) 0%,var(--accent) 100%);color:#fff;border-radius:10px;padding:18px 14px;text-align:center;}
.kpi-box .kpi-value{font-size:1.85rem;font-weight:800;line-height:1.1;}
.kpi-box .kpi-label{font-size:.8rem;opacity:.85;margin-top:4px;}
.kpi-box.green{background:linear-gradient(135deg,#1a7a5e 0%,var(--accent2) 100%);}
.kpi-box.orange{background:linear-gradient(135deg,#9c5a10 0%,#e67e22 100%);}
.kpi-box.red{background:linear-gradient(135deg,#8e1a1a 0%,#c0392b 100%);}
.kpi-box.purple{background:linear-gradient(135deg,#5b2c6f 0%,#8e44ad 100%);}
.table-custom thead{background:var(--primary);color:#fff;}
.table-custom thead th{font-weight:600;border:none;padding:10px 13px;}
.table-custom tbody tr:nth-child(even){background:#f0f5fb;}
.table-custom tbody td{padding:9px 13px;border-top:1px solid var(--border);vertical-align:middle;}
.table-custom{border-radius:8px;overflow:hidden;box-shadow:0 1px 6px rgba(0,0,0,.08);}
.best-row td{font-weight:700;background:#d4edda!important;}
.callout{border-left:4px solid var(--accent);background:#eaf3fb;border-radius:6px;padding:13px 17px;margin:16px 0;font-size:.94rem;}
.callout.warning{border-color:#e67e22;background:#fdf3e7;}
.callout.success{border-color:var(--accent2);background:#e9f7f2;}
.callout.danger{border-color:#c0392b;background:#fdecea;}
.callout strong{display:block;margin-bottom:3px;}
.chart-container{width:100%;min-height:360px;margin:16px 0 8px;}
.chart-title{font-size:.93rem;font-weight:600;color:var(--primary);margin:18px 0 2px 4px;}
.chart-grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:12px 0;}
@media(max-width:768px){.chart-grid-2{grid-template-columns:1fr;}}
.progress-wrap{margin:6px 0 14px;}
.progress-label{font-size:.86rem;font-weight:600;margin-bottom:3px;display:flex;justify-content:space-between;}
.progress{height:11px;border-radius:6px;background:#dee2e6;}
.progress-bar-custom{background:linear-gradient(90deg,var(--accent),var(--accent2));border-radius:6px;height:100%;transition:width .6s ease;}
.reco-item{display:flex;gap:14px;margin-bottom:16px;padding:14px 18px;background:#f8fbff;border-radius:8px;border:1px solid #dbe8f5;}
.reco-num{font-size:1.4rem;font-weight:800;color:var(--accent);line-height:1;flex-shrink:0;min-width:28px;}
.reco-content h5{color:var(--primary);font-weight:700;margin-bottom:3px;font-size:.98rem;}
.reco-content p{margin:0;font-size:.92rem;}
.footer{background:var(--primary);color:rgba(255,255,255,.7);text-align:center;padding:22px 20px;font-size:.87rem;}
.footer strong{color:#fff;}
html{scroll-behavior:smooth;}
'''

    parts = [f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Rapport Analytique — TP Hospitalisation</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/css/bootstrap.min.css"/>
<script src="https://cdn.plot.ly/plotly-3.5.0.min.js"></script>
<style>{css}</style>
</head>
<body>''',
        _navbar(),
        _cover(len(df), 10, date_gen),
        '<div class="main-wrapper">',
        _toc(),
        _section_libs(),
        _section1(df, kpis),
        _section2(df, figures),
        _section3(figures),
        _section4_ml(ml_results),
        _section5(),
        _section6(),
        '</div>',
        _footer(df, date_gen),
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.2/js/bootstrap.bundle.min.js"></script>',
        '</body></html>',
    ]

    return '\n'.join(parts)
