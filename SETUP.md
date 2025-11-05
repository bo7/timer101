# Setup Anleitung - Zeit Erfassung

Komplette Anleitung zur Installation und Einrichtung des Zeit Erfassung Systems.

## Voraussetzungen

- **Python 3.10+** - für Backend
- **Node.js 18+** und npm - für Frontend
- **Git** - für Version Control

## Quick Start (5 Minuten)

### 1. Backend einrichten

```bash
cd backend

# Virtuelle Umgebung erstellen
python -m venv venv

# Aktivieren (Linux/Mac)
source venv/bin/activate

# Aktivieren (Windows)
# venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# Datenbank mit Testdaten befüllen
python seed_data.py

# Server starten
uvicorn app.main:app --reload
```

Backend läuft jetzt auf: **http://localhost:8000**

API Dokumentation: **http://localhost:8000/docs**

### 2. Frontend einrichten

In einem **neuen Terminal**:

```bash
cd frontend

# Dependencies installieren
npm install

# Environment-Datei erstellen
cp .env.example .env

# Dev-Server starten
npm run dev
```

Frontend läuft jetzt auf: **http://localhost:3000**

### 3. Anwendung testen

Öffne im Browser: **http://localhost:3000**

**Test-Zugangsdaten:**
- Mitarbeiter: `max.mueller` / `password123`
- Admin: `admin` / `admin123`

## Detaillierte Einrichtung

### Backend Setup (ausführlich)

1. **In das Backend-Verzeichnis wechseln:**
   ```bash
   cd backend
   ```

2. **Virtuelle Python-Umgebung erstellen:**
   ```bash
   python -m venv venv
   ```

3. **Virtuelle Umgebung aktivieren:**

   **Linux/Mac:**
   ```bash
   source venv/bin/activate
   ```

   **Windows (Command Prompt):**
   ```cmd
   venv\Scripts\activate.bat
   ```

   **Windows (PowerShell):**
   ```powershell
   venv\Scripts\Activate.ps1
   ```

4. **Python-Pakete installieren:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Environment-Variablen konfigurieren (optional):**
   ```bash
   cp .env.example .env
   # Bearbeite .env und ändere SECRET_KEY für Produktion!
   ```

6. **Datenbank initialisieren und mit Testdaten befüllen:**
   ```bash
   python seed_data.py
   ```

   Dies erstellt:
   - 3 Benutzer (1 Admin, 2 Mitarbeiter)
   - 4 Kunden
   - 7 Standorte
   - Beispiel-Zeiteinträge

7. **Backend-Server starten:**
   ```bash
   uvicorn app.main:app --reload
   ```

   Der Server läuft auf Port 8000.

8. **API-Dokumentation aufrufen:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Frontend Setup (ausführlich)

1. **In das Frontend-Verzeichnis wechseln:**
   ```bash
   cd frontend
   ```

2. **Node.js-Pakete installieren:**
   ```bash
   npm install
   ```

   Dies installiert:
   - Next.js 15.5
   - React 19
   - Tailwind CSS v4
   - TypeScript
   - und weitere Dependencies

3. **Environment-Datei erstellen:**
   ```bash
   cp .env.example .env
   ```

   Standardmäßig zeigt `NEXT_PUBLIC_API_URL` auf `http://localhost:8000`

4. **Entwicklungsserver starten:**
   ```bash
   npm run dev
   ```

   Der Frontend-Server läuft auf Port 3000.

5. **Anwendung im Browser öffnen:**
   ```
   http://localhost:3000
   ```

## Testdaten

Nach `python seed_data.py` sind folgende Daten verfügbar:

### Benutzer

| Benutzername   | Passwort      | Rolle       |
|---------------|---------------|-------------|
| admin         | admin123      | Administrator |
| max.mueller   | password123   | Mitarbeiter   |
| anna.schmidt  | password123   | Mitarbeiter   |

### Kunden

- Müller GmbH (C001)
- Schmidt & Partner (C002)
- Bauer AG (C003)
- Weber Industries (C004)

Jeder Kunde hat 1-2 Standorte.

### Zeiteinträge

Es gibt bereits einige Beispiel-Zeiteinträge für die letzten Tage:
- Einträge von heute (nicht verarbeitet)
- Einträge von gestern (verarbeitet)
- Einträge von vorgestern (verarbeitet)

## Verwendung

### Mitarbeiter-Workflow

1. **Anmelden:** http://localhost:3000/login
2. **Dashboard:** Auswahl zwischen drei Optionen
3. **Heute erfassen:**
   - Kunde suchen (AJAX-Suche)
   - Standort wählen (dynamisch basierend auf Kunde)
   - Zeiten eingeben
   - Pause optional
   - Tätigkeit beschreiben
   - Weiteren Eintrag hinzufügen (+)
4. **Anderen Tag erfassen:**
   - Datum wählen
   - Gleicher Ablauf wie "Heute erfassen"
5. **Tag anzeigen:**
   - Datum wählen
   - Alle Einträge anzeigen
   - Nicht-verarbeitete Einträge bearbeiten/löschen
   - Verarbeitete Einträge nur ansehen

### Admin-Funktionen

Über die API (http://localhost:8000/docs):
- `PUT /api/admin/worktimes/{id}/process` - Eintrag verarbeiten
- `PUT /api/admin/worktimes/{id}/unprocess` - Verarbeitung rückgängig
- `GET /api/admin/users` - Alle Benutzer anzeigen

## Entwicklung

### Backend-Entwicklung

```bash
cd backend

# Tests ausführen (wenn implementiert)
pytest

# Code-Qualität prüfen
flake8 app/
black app/

# Neue Abhängigkeit hinzufügen
pip install <paket>
pip freeze > requirements.txt
```

### Frontend-Entwicklung

```bash
cd frontend

# TypeScript-Fehler prüfen
npm run build

# Linting
npm run lint

# Production Build
npm run build
npm run start
```

## Produktion

### Backend für Produktion vorbereiten

1. **SECRET_KEY ändern** in `.env`:
   ```env
   SECRET_KEY="ein-sehr-sicherer-zufälliger-string-min-32-zeichen"
   ```

2. **PostgreSQL-Datenbank einrichten** (optional):
   ```env
   DATABASE_URL="postgresql://user:password@localhost/zeiterfassung"
   ```

   Dann:
   ```bash
   pip install psycopg2-binary
   python -c "from app.core.database import init_db; init_db()"
   ```

3. **Gunicorn verwenden** statt uvicorn:
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Frontend für Produktion vorbereiten

1. **Production Build erstellen:**
   ```bash
   npm run build
   ```

2. **Production Server starten:**
   ```bash
   npm run start
   ```

3. **Oder mit einem Reverse Proxy (nginx):**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:3000;
       }

       location /api {
           proxy_pass http://localhost:8000;
       }
   }
   ```

## Troubleshooting

### Backend startet nicht

**Problem:** `ModuleNotFoundError`
```bash
# Lösung: Virtuelle Umgebung aktivieren
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

**Problem:** `Database is locked`
```bash
# Lösung: SQLite-Datei löschen und neu erstellen
rm zeiterfassung.db
python seed_data.py
```

### Frontend startet nicht

**Problem:** `Cannot find module`
```bash
# Lösung: Dependencies neu installieren
rm -rf node_modules package-lock.json
npm install
```

**Problem:** API-Fehler (CORS)
```bash
# Lösung: Backend CORS-Einstellungen prüfen
# In backend/app/core/config.py:
BACKEND_CORS_ORIGINS = ["http://localhost:3000"]
```

### Login funktioniert nicht

1. Prüfe, ob Backend läuft: http://localhost:8000/health
2. Prüfe, ob Testdaten geladen sind: `python seed_data.py`
3. Browser-Konsole öffnen (F12) und Netzwerk-Tab prüfen
4. Token im LocalStorage prüfen (Application > Local Storage)

## Weitere Hilfe

- Backend API Docs: http://localhost:8000/docs
- Next.js Docs: https://nextjs.org/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- Tailwind CSS Docs: https://tailwindcss.com/docs

Bei Problemen siehe auch: `README.md` und `DATABASE_SCHEMA.md`
