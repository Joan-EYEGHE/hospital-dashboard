# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

*NB: Réponds moi toujours en français.* 

## Running the App

```bash
# Activate virtual environment
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac

# Run development server (debug=True, hot reload)
python app.py
# → http://127.0.0.1:8050

# Production
gunicorn app:server --bind 0.0.0.0:8080
```

## Validating the Data Pipeline

```bash
python modules/preprocessing.py
# Prints dataset summary, derived columns, and KPI values — useful for checking preprocessing changes
```

## Architecture Overview

**Stack:** Dash 4.1.0 + Plotly 6.7.0 + Bootstrap 5.3.2 + Pandas 3.0.2 + scikit-learn 1.8.0

**Data flow:**
1. `modules/preprocessing.py` — loads `data/hospital_data.csv` (500 patients, semicolon-separated) and engineers 6 new columns (`TrancheAge`, `MoisAdmission`, `CoutParJour`, `SejourLong`, `Saison`, `MoisLabel`). Exposes `load_data()`, `apply_filters()`, `get_kpis()`, `get_filter_options()`.
2. `modules/figures.py` — 6 Plotly Express charts, each accepting a filtered DataFrame. All have empty-data fallbacks and share a consistent color palette (`#1D3557`, `#E63946`, `#457B9D`, `#2A9D8F`, `#E9C46A`).
3. `modules/ml.py` — runs at startup (not filter-reactive). Three-tier pipeline: Level 1 (6 raw features), Level 2 (11 enriched features + interaction terms), Level 3 (VotingClassifier). Target: `SejourLong` (1 if DureeSejour > median 8 days). Results cached in `ML_SCORES` and `FI_FIG`.
4. `modules/rapport.py` — generates a downloadable HTML report embedding all 6 Plotly figures as inline JSON + JavaScript.
5. `app.py` — wires everything together. Three callbacks:
   - **Global** (3 filter inputs → KPI row + 6 graphs + badge)
   - **ML** (static, displays pre-computed results)
   - **Download** (button click → `rapport_hospitalier.html`)

## Key Conventions

- All figures are stateless functions receiving a filtered DataFrame — never read global state inside `figures.py`.
- ML training is computed once at import time in `ml.py`, not inside callbacks.
- The ML target (`SejourLong`) is defined in `preprocessing.py` as `DureeSejour > DureeSejour.median()`.
- Filters (department, gender, age bracket) are applied via `preprocessing.apply_filters()` before any figure or KPI computation.
- Report HTML is self-contained (Bootstrap CDN + inline Plotly JSON) so it opens without a running server.

## Deployment

Target: Render (WSGI via Gunicorn). The `server` object exported from `app.py` is the WSGI entry point.
