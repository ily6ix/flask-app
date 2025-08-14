# Flask Portfolio — Advanced

- Responsive UI (Bootstrap 5)
- GitHub integration: shows your 5 latest public repos for `ily6ix` with images
- Contact form backed by SQLite + Admin panel to view messages

## Quickstart

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt

# Optional (recommended) secrets (PowerShell):
$env:SECRET_KEY="change-this"
$env:ADMIN_PASSWORD="super-secret"
$env:GITHUB_USER="ily6ix"

python app.py
```
Open http://localhost:5000

### Admin
- Go to `/admin/login`
- Use the password from `ADMIN_PASSWORD` (default `changeme` — change it)

### Notes
- Project images use GitHub’s Open Graph previews.
- Messages are stored locally in `site.db` (SQLite).
