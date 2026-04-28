# The Career Alchemist

AI-powered Streamlit app that helps tailor CV content and cover letters to specific job descriptions.

## Stack
- Python
- Streamlit
- Google Gemini API
- pypdf

## Run Locally

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add environment variable in a local `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

4. Start the app:

```bash
streamlit run app.py
```

## Publish Option 1: Streamlit Community Cloud (Recommended)

1. Push this repository to GitHub.
2. Go to Streamlit Community Cloud and create a new app from this repo.
3. Set:
	- Main file path: `app.py`
	- Python dependencies: auto-detected from `requirements.txt`
4. In app settings, add secret:
	- Key: `GOOGLE_API_KEY`
	- Value: your API key
5. Deploy.

Notes:
- This repo includes `.streamlit/config.toml` for production-friendly server settings.
- You can use `.streamlit/secrets.toml.example` as a reference for local secrets format.

## Publish Option 2: Render or Railway

This repo includes a `Procfile`:

```text
web: streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-8501}
```

Deployment steps are similar on both platforms:

1. Create a new Web Service from this GitHub repo.
2. Runtime: Python.
3. Build command:

```bash
pip install -r requirements.txt
```

4. Start command: use `Procfile` or paste the same streamlit command.
5. Set environment variable:

```text
GOOGLE_API_KEY=your_google_api_key_here
```

## Troubleshooting

- If you see an API key error at startup, confirm `GOOGLE_API_KEY` is configured in platform secrets/env vars.
- If deploy succeeds but app fails at runtime, check service logs for missing dependency or invalid key errors.
