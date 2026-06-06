# cyberpulse-tracker

Mobile number lookup tool with a cyberpunk terminal UI.

## Deploy on GitHub Pages

1. Go to repo **Settings → Pages**
2. **Source**: Deploy from a branch → `main` → `/ (root)` → **Save**
3. Site will be live at `https://ayushverma-1307.github.io/cyberpulse-tracker/`

The app is fully client-side (HTML/CSS/JS). The API call goes through a CORS proxy when needed.

## Run locally (static)

Just open `index.html` in any browser, or serve it:
```bash
python -m http.server 8000
# Then open http://localhost:8000
```

## Flask version (alternative)

```bash
pip install flask requests
python track.py
```
