"""
rapport.py
----------
Génération du rapport HTML téléchargeable depuis le dashboard.
Inclut : KPIs, résumé des graphiques, résultats ML.
"""

import base64
import io
from datetime import datetime

import pandas as pd
import plotly.io as pio


def _kpi_html(kpis: dict) -> str:
    return f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-value">{kpis['nb_patients']}</div>
            <div class="kpi-label">Patients analysés</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{kpis['cout_moyen']:,.0f} FCFA</div>
            <div class="kpi-label">Coût moyen de séjour</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{kpis['duree_moyenne']} j</div>
            <div class="kpi-label">Durée moyenne de séjour</div>
        </div>
    </div>
    """


def _ml_html(ml_results: dict) -> str:
    if not ml_results:
        return "<p>Résultats ML non disponibles.</p>"

    rows = ""
    for model, scores in ml_results.items():
        rows += f"""
        <tr>
            <td><strong>{model}</strong></td>
            <td>{scores.get('f1_mean', 'N/A'):.3f}</td>
            <td>{scores.get('f1_std', 'N/A'):.3f}</td>
            <td>{scores.get('accuracy', 'N/A'):.3f}</td>
        </tr>
        """

    winner = max(ml_results, key=lambda m: ml_results[m].get("f1_mean", 0))
    return f"""
    <table>
        <thead>
            <tr>
                <th>Modèle</th>
                <th>F1-score (CV moyen)</th>
                <th>Écart-type</th>
                <th>Accuracy</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    <p class="winner">🏆 Meilleur modèle : <strong>{winner}</strong>
    (F1 = {ml_results[winner].get('f1_mean', 0):.3f})</p>
    """


def _fig_to_img_tag(fig) -> str:
    """Convertit une figure Plotly en balise <img> base64."""
    try:
        img_bytes = pio.to_image(fig, format="png", width=900, height=450, scale=1.5)
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        return f'<img src="data:image/png;base64,{b64}" style="width:100%;max-width:900px;margin:12px 0;">'
    except Exception:
        return "<p><em>[Graphique non disponible — kaleido non installé]</em></p>"


def generate_rapport_html(
    df: pd.DataFrame,
    kpis: dict,
    figures: dict,
    ml_results: dict,
    filtres_actifs: dict = None,
) -> str:
    """
    Génère le rapport HTML complet.

    Parameters
    ----------
    df          : DataFrame filtré utilisé pour le dashboard
    kpis        : dict retourné par get_kpis()
    figures     : dict { nom: figure_plotly }
    ml_results  : dict { modèle: { f1_mean, f1_std, accuracy } }
    filtres_actifs : dict des filtres appliqués (optionnel)

    Returns
    -------
    str : contenu HTML complet du rapport
    """
    date_gen = datetime.now().strftime("%d/%m/%Y à %H:%M")

    # Filtres en clair
    filtres_str = "Aucun filtre appliqué (données complètes)"
    if filtres_actifs:
        parties = []
        if filtres_actifs.get("departements"):
            parties.append(f"Département : {', '.join(filtres_actifs['departements'])}")
        if filtres_actifs.get("sexes"):
            parties.append(f"Sexe : {', '.join(filtres_actifs['sexes'])}")
        if filtres_actifs.get("tranches_age"):
            parties.append(f"Tranche d'âge : {', '.join(filtres_actifs['tranches_age'])}")
        if parties:
            filtres_str = " | ".join(parties)

    # Statistiques descriptives
    stats = df[["Age", "DureeSejour", "Cout", "CoutParJour"]].describe().round(1)
    stats_html = stats.to_html(classes="stats-table", border=0)

    # Graphiques
    figs_html = ""
    titres = {
        "tranches_age": "Distribution des âges par tranche",
        "cout_dept": "Coût moyen par département",
        "duree_maladie": "Durée de séjour par maladie",
        "traitements": "Répartition des traitements",
        "admissions": "Évolution des admissions par mois",
        "scatter": "Coût vs Durée de séjour",
    }
    for key, fig in figures.items():
        titre = titres.get(key, key)
        figs_html += f"<h3>{titre}</h3>{_fig_to_img_tag(fig)}"

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rapport — Dashboard Hospitalier</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', sans-serif; background: #f8f9fa; color: #212529; }}
  .container {{ max-width: 1000px; margin: 0 auto; padding: 40px 20px; }}

  header {{ background: linear-gradient(135deg, #1d3557, #457b9d); color: white;
            padding: 40px; border-radius: 12px; margin-bottom: 32px; }}
  header h1 {{ font-size: 2rem; margin-bottom: 8px; }}
  header p  {{ opacity: 0.85; font-size: 0.95rem; }}

  .section {{ background: white; border-radius: 10px; padding: 28px;
              margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,.06); }}
  .section h2 {{ font-size: 1.2rem; color: #1d3557; border-bottom: 2px solid #e63946;
                 padding-bottom: 10px; margin-bottom: 20px; }}
  .section h3 {{ font-size: 1rem; color: #457b9d; margin: 20px 0 8px; }}

  .kpi-grid {{ display: flex; gap: 16px; flex-wrap: wrap; }}
  .kpi-card {{ flex: 1; min-width: 160px; background: #f1faee;
               border-left: 4px solid #e63946; border-radius: 8px; padding: 16px; }}
  .kpi-value {{ font-size: 1.6rem; font-weight: 700; color: #1d3557; }}
  .kpi-label {{ font-size: 0.8rem; color: #6c757d; margin-top: 4px; }}

  table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
  th {{ background: #1d3557; color: white; padding: 10px 14px; text-align: left; }}
  td {{ padding: 8px 14px; border-bottom: 1px solid #e9ecef; }}
  tr:nth-child(even) td {{ background: #f8f9fa; }}

  .stats-table th {{ background: #457b9d; }}

  .winner {{ margin-top: 14px; padding: 12px 16px; background: #f1faee;
             border-radius: 8px; color: #2a9d8f; font-size: 0.95rem; }}

  .filtre-badge {{ display: inline-block; background: #e9ecef; border-radius: 20px;
                   padding: 4px 12px; font-size: 0.8rem; color: #495057; margin: 4px; }}
  footer {{ text-align: center; color: #adb5bd; font-size: 0.8rem; margin-top: 32px; }}
</style>
</head>
<body>
<div class="container">

  <header>
    <h1>🏥 Rapport — Dashboard Hospitalier</h1>
    <p>Généré le {date_gen} &nbsp;|&nbsp; {kpis['nb_patients']} patients analysés</p>
    <p style="margin-top:10px;">
      <strong>Filtres appliqués :</strong>
      <span class="filtre-badge">{filtres_str}</span>
    </p>
  </header>

  <div class="section">
    <h2>📊 Indicateurs clés (KPIs)</h2>
    {_kpi_html(kpis)}
  </div>

  <div class="section">
    <h2>📋 Statistiques descriptives</h2>
    {stats_html}
  </div>

  <div class="section">
    <h2>📈 Visualisations</h2>
    {figs_html if figs_html else "<p>Graphiques non inclus (kaleido requis pour l'export PNG).</p>"}
  </div>

  <div class="section">
    <h2>🤖 Résultats Machine Learning — Prédiction SejourLong</h2>
    <p style="margin-bottom:16px;font-size:.9rem;color:#6c757d;">
      Variable cible : <code>SejourLong</code> — séjour supérieur à la médiane (8 jours).
      Évaluation par Cross-Validation (5 folds), métrique F1-score.
    </p>
    {_ml_html(ml_results)}
  </div>

  <footer>
    <p>Dashboard Hospitalier — M2 CDSD, ISM Dakar &nbsp;|&nbsp;
    Généré automatiquement le {date_gen}</p>
  </footer>

</div>
</body>
</html>"""

    return html
