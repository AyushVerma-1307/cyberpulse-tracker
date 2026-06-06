# cyberpulse-tracker

Mobile number lookup tool with a cyberpunk terminal UI.

## Deploy on GitHub Pages

1. Go to repo **Settings → Pages**
2. **Source**: Deploy from a branch → `main` → `/ (root)` → **Save**
3. Live at `https://ayushverma-1307.github.io/cyberpulse-tracker/`

## Run locally

Double-click **`start.bat`** (uses PowerShell to serve the page).

Or use any HTTP server:
```bash
npx serve .
python -m http.server 8000
```
Then open `http://localhost:8000`

## Paste fallback

If CORS proxies fail, the page shows a textarea. Paste the raw API response there to parse it.
