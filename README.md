# LB2 Projektarbeit - StudyHub (Microservices)

## Projektidee
StudyHub ist eine kleine Lern- und Aufgabenplattform mit mehreren Services:
- API Gateway als Einstiegspunkt
- Users Service fuer Benutzerverwaltung
- Tasks Service fuer Aufgabenverwaltung
- Analytics Service fuer Kennzahlen
- PostgreSQL als persistente Datenbank im Hintergrund

Damit wirkt die App deutlich groesser als ein einzelner Webservice und passt gut zum LB2-Ziel (produktionsreifes Deployment mit mehreren Komponenten).

## Architekturuebersicht
### Services und Kommunikation
1. Client spricht nur mit dem API Gateway.
2. Gateway leitet Requests intern an Users/Tasks/Analytics weiter.
3. Users, Tasks und Analytics nutzen dieselbe PostgreSQL-Datenbank.
4. Jeder Service hat einen eigenen Healthcheck.

### Diagramm (Text)
```text
Client
  |
  v
API Gateway (8000)
  |------> Users Service (8001) -----|
  |------> Tasks Service (8002) -----|--> PostgreSQL (5432)
  |------> Analytics Service (8003) -|
```

## Technologie-Stack
- Python, FastAPI, Gunicorn, Uvicorn
- SQLAlchemy + PostgreSQL
- Docker / Docker Compose
- GitHub Actions (Lint/Test/Build/Deploy-Trigger)
- Render als Zielplattform

## Setup-Anleitung
### Voraussetzungen
- Docker Desktop

### Lokal starten
1. Environment-Datei erstellen:
   ```bash
   cp .env.example .env
   ```
2. Alles starten:
   ```bash
   docker compose up --build
   ```
3. Schnelltest:
  - Gateway: http://localhost:8080/
  - Gateway Health: http://localhost:8080/health
   - Users Health: http://localhost:8001/health
   - Tasks Health: http://localhost:8002/health
   - Analytics Health: http://localhost:8003/health

### Beispiel-Requests ueber Gateway
Benutzer erstellen:
```bash
curl -X POST http://localhost:8080/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Saim","email":"saim@example.com"}'
```

Aufgabe erstellen:
```bash
curl -X POST http://localhost:8080/tasks \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"title":"LB2 Screencast aufnehmen","status":"todo"}'
```

Analytics abrufen:
```bash
curl http://localhost:8080/analytics/summary
```

## Render / CI-CD
Die Pipeline in [.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml) fuehrt aus:
1. Lint
2. Tests
3. Docker Build + Push nach GHCR
4. Deploy-Trigger fuer Render (Deploy Hook)

Hinweis: Fuer echtes Produktiv-Setup mit mehreren Services auf Render solltest du jeden Service als eigenen Render-Service anlegen oder alternativ nur den Gateway-Service auf Render deployen und Backends separat hosten.

## Entscheidungsbegruendungen
- Microservices statt Monolith: zeigt Service-Kommunikation und erhoeht Komplexitaet nachvollziehbar.
- Gateway Pattern: ein klarer Einstiegspunkt fuer Clients.
- PostgreSQL: realistische Persistenz fuer Produktionsszenarien.
- Compose: reproduzierbarer Start mit einem Kommando.

## Learnings
- Service-Grenzen frueh definieren hilft bei sauberer Architektur.
- Gemeinsame Datenbank ist einfach, aber spaeter ein Entkopplungsrisiko.
- Healthchecks pro Service machen Fehlersuche deutlich einfacher.

## Screencast-Guide (5-10 Minuten)
1. Architektur und Services erklaeren.
2. `docker compose up --build` zeigen.
3. API-Calls: User anlegen, Task anlegen, Analytics abrufen.
4. Pipeline-Lauf nach Push demonstrieren.
5. Render-Deployment und laufende Anwendung zeigen.

## LB2 Checkliste
- [x] Dockerfile vorhanden
- [x] Docker Compose mit mehreren Services + DB
- [x] Healthchecks vorhanden
- [x] Env-Variablen verwendet
- [x] CI/CD vorbereitet
- [ ] Screencast aufnehmen

## KI-Nutzung
Dieses Projekt wurde mit KI-Unterstuetzung erstellt (Struktur, Docker/CI-Ideen, Dokumentation). Alle Inhalte wurden manuell geprueft und koennen erklaert werden.
