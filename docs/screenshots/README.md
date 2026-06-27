# Screenshot Capture Guide

Run the app locally, then capture screenshots for the main README.

## Start the app

```powershell
docker compose up -d db
python -m alembic upgrade head
python fast_seed.py
uvicorn app.main:app --reload
```

In another terminal:

```powershell
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

Login:

```text
demo@hotel.com
demopass123
```

## Save screenshots with these exact names

Place these files in `docs/screenshots/`:

```text
dashboard.png
reviews.png
analyze.png
upload.png
keywords.png
dark-mode.png
```

## Recommended captures

- `dashboard.png`: full dashboard with charts visible
- `reviews.png`: review explorer with filters and sentiment badges
- `analyze.png`: live analysis page after analyzing a sample review
- `upload.png`: CSV upload screen
- `keywords.png`: dashboard keyword intelligence panel
- `dark-mode.png`: dashboard in dark mode

Use Windows Snipping Tool or browser screenshot tools.