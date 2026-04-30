# Data & AI Portfolio (Streamlit)

An interactive portfolio website for Data Engineer / Analyst / Scientist roles.

## Features
- Dashboard with dynamic filters (Plotly + Altair)
- Lightweight ML predictor demo (CPU-friendly)
- Data pipeline architecture + ETL metadata cards
- AI Playground using Hugging Face Inference API (Stable Diffusion)
- Markdown-based blog + resume page

## Run locally

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1

pip install -r requirements.txt
streamlit run app.py
```

## Hugging Face token (for AI Playground)
- **Local**: create `.streamlit/secrets.toml` (do not commit it) using the template:
  - `.streamlit/secrets.toml.example`
- **Streamlit Cloud**: App → Settings → Secrets

Example secrets:

```toml
HF_TOKEN = "hf_..."
```

## Deploy (Streamlit Community Cloud)
1. Push this repo to GitHub.
2. Go to Streamlit Cloud and create a new app from the repo.
3. Set `HF_TOKEN` in Secrets (optional; only needed for AI Playground).

## Streamlit Cloud notes (free tier)
- Prefer small datasets (or load from remote storage).
- Use caching (`st.cache_data` / `st.cache_resource`) to reduce CPU/RAM.
- AI image generation is done via Hugging Face API (no GPU required on Streamlit).

## Customize
- Replace sample data in `data/` with your real datasets (keep them small for free-tier).
- Replace resume content and add `assets/resume.pdf`.
- Add posts as markdown files in `posts/`.
