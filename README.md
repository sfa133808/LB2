# LB2 Projektarbeit - Deployment auf Render

## Projektübersicht
Diese Beispielanwendung ist eine schlanke FastAPI-Webanwendung mit zwei Endpunkten:
- `/`: Basisantwort mit Projektinformationen
- `/health`: Healthcheck fuer Plattform und Container-Orchestrierung

Ziel ist ein produktionsnahes Setup gemaess LB2:
- containerisiert (Multi-Stage Dockerfile, Non-Root-User)
- automatisierte CI/CD Pipeline
- Deployment auf Render
- Konfiguration via Environment-Variablen
- reproduzierbares Setup mit Docker Compose

## Architekturuebersicht
### Services und Kommunikation
1. Entwickler pusht Code nach GitHub.
2. GitHub Actions fuehrt Lint, Tests, Docker Build und Push nach GHCR aus.
3. Nach erfolgreichem Build wird Render per Deploy Hook getriggert.
4. Render baut/deployed den Service und prueft `/health`.

### Diagramm (Text)
```text
Developer
   |
   | git push
   v
GitHub Repository
   |
   | GitHub Actions: lint -> test -> docker build -> push ghcr
   v
GHCR (Container Registry)
   |
   | deploy hook
   v
Render Web Service
   |
   | healthcheck GET /health
   v
Running Application
```

## Technologie-Stack
- Backend: FastAPI, Uvicorn, Gunicorn
- Container: Docker (Multi-Stage Build, Non-Root)
- Lokale Orchestrierung: Docker Compose
- CI/CD: GitHub Actions
- Registry: GitHub Container Registry (GHCR)
- Zielplattform: Render

## Setup-Anleitung
### Voraussetzungen
- GitHub Repository
- Docker Desktop
- Render Account

### 1. Projekt lokal starten
1. `.env.example` nach `.env` kopieren.
2. Optional Werte in `.env` anpassen.
3. Starten:
   ```bash
   docker compose up --build
   ```
4. Testen:
   - App: `http://localhost:8000/`
   - Healthcheck: `http://localhost:8000/health`

### 2. Render konfigurieren
1. In Render neuen Web Service anlegen und mit GitHub verbinden.
2. Als Runtime `Docker` verwenden.
3. `render.yaml` als Basis nutzen (Blueprint oder manuelle Uebernahme).
4. Environment-Variablen in Render setzen:
   - `APP_NAME`
   - `APP_ENV=production`
   - `APP_VERSION`
   - `PORT` (Render nutzt typischerweise `10000`)
5. Deploy Hook URL erstellen und in GitHub Secret speichern:
   - Name: `RENDER_DEPLOY_HOOK_URL`

### 3. GitHub Actions aktivieren
Pipeline-Datei: `.github/workflows/ci-cd.yml`

Ablauf bei Push auf `main`:
1. Lint (`ruff check .`)
2. Tests (`pytest`)
3. Docker Image Build + Push nach GHCR
4. Deployment Trigger via Render Deploy Hook

Wichtige Secrets:
- `RENDER_DEPLOY_HOOK_URL`

Hinweis zu GHCR:
- Package-Sichtbarkeit auf `public` setzen oder Render mit den noetigen Registry-Credentials konfigurieren.

## Entscheidungsbegruendungen
- Render wurde gewaehlt, weil Deployment und Healthchecks schnell produktiv nutzbar sind.
- FastAPI ist fuer API-Projekte leichtgewichtig, testbar und schnell aufsetzbar.
- GHCR wurde als naheliegende Registry gewaehlt, da sie direkt mit GitHub Actions integriert ist.
- Deploy Hook trennt CI (Build/Test) und CD (Rollout) sauber.

## Learnings
- Multi-Stage Builds reduzieren Imagegroesse und halten Runtime-Images sauber.
- Non-Root-Ausfuehrung ist ein einfacher, aber wichtiger Security-Gewinn.
- Ein robuster Healthcheck ist zentral fuer stabile Deployments.
- Fruehes Aufsetzen von `.env.example` verhindert harte Codierung von Konfiguration.

## Screencast-Guide (5-10 Minuten)
Im Video zeigen:
1. Kurze Repo-Struktur (`app`, `tests`, `Dockerfile`, Workflow, `render.yaml`).
2. Einen Push auf `main`.
3. GitHub Actions Lauf mit allen Stages.
4. Render Deployment und laufende App.
5. Healthcheck Aufruf auf `/health`.
6. Kurze Erklaerung der Architektur und Tool-Entscheide.

## LB2 Checkliste (Mindestanforderungen)
- [x] Dockerfile vorhanden
- [x] CI/CD fuer Build + Deployment
- [x] Zielplattform Render eingeplant
- [x] Konfiguration via Environment-Variablen
- [x] Healthcheck implementiert
- [x] README mit Architektur, Setup, Entscheidungen, Learnings
- [ ] Screencast aufnehmen und abgeben

## KI-Nutzung (Deklaration)
Dieses Projekt wurde unterstuetzt durch KI-Tools (u. a. GitHub Copilot/ChatGPT) fuer:
- Strukturierung von Deployment-Dateien
- Formulierung der Dokumentation
- Vorschlaege fuer CI/CD und Docker-Optimierungen

Alle Inhalte wurden manuell geprueft, angepasst und koennen technisch erklaert werden.
