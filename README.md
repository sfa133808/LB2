# LB2 — StudyHub

Dieses Projekt ist eine Web‑App mit mehreren Diensten:

- `users-service`: Verwalten von Benutzern
- `tasks-service`: Verwalten von Aufgaben
- `analytics-service`: Zählt Benutzer und Aufgaben
- `frontend`: Einfaches Dashboard (Webseite)

Jeder Dienst hat zwei nützliche Seiten:
- `/health` zeigt, ob der Dienst gesund ist
- `/docs` zeigt die API‑Dokumentation (Swagger)

Diese README erklärt die Installation, Nutzung und das Deployment des Projekts.

---

## Architektur

```
┌─────────────┐
│  Frontend   │ (Port 3000)
│ (Dashboard) │
└──────┬──────┘
       │
       ├─→ Users Service    (Port 8001) ──┐
       ├─→ Tasks Service    (Port 8002) ──┤
       └─→ Analytics Service(Port 8003) ──┤
                                           │
                                    ┌──────▼─────┐
                                    │ PostgreSQL │
                                    │ (Database) │
                                    └────────────┘
```

Werkzeuge & Features:
- Docker Compose: Lokale Entwicklung
- GitHub Actions: CI/CD Pipeline
- Render: Production Deployment
- Healthchecks: `/health` Endpunkt pro Service

---

## Schnellstart

Voraussetzungen: Git und Docker (mit docker‑compose) installiert.

1) Klonen und Ordner wechseln
```bash
git clone <repo-url>
cd LB2
```

2) Beispiel‑Konfiguration kopieren
```bash
cp .env.example .env
```

3) Alles starten
```bash
docker compose up --build -d
```

4) Seiten prüfen
- Frontend: http://localhost:3000
- Users API: http://localhost:8001/
- Tasks API: http://localhost:8002/
- Analytics API: http://localhost:8003/

Logs ansehen:
```bash
docker compose logs -f
```

Beenden:
```bash
docker compose down -v
```

---

## Wichtige Endpunkte

- Health prüfen:
```bash
curl -i http://localhost:8001/health
```
- Alle Benutzer abrufen:
```bash
curl -i http://localhost:8001/users
```
- Einen Benutzer anlegen:
```bash
curl -i -X POST -H "Content-Type: application/json" \
   -d '{"name":"Max","email":"max@example.com"}' \
   http://localhost:8001/users
```
- Analytics zusammenfassung:
```bash
curl -i http://localhost:8003/analytics/summary
```

---

## Docker und Sicherheit

- Die Dockerfiles sind so gebaut, dass das End‑Image klein und sicher ist (Multi‑Stage, non‑root).
- `.dockerignore` verhindert, dass unnötige Dateien ins Image kommen.
- Sensible Daten kommen nicht ins Git — sie stehen in `.env` oder in den Secrets der Plattform.

---

## CI/CD 

- Es gibt eine GitHub Actions Pipeline in `.github/workflows/ci-cd.yml`.
- Die Pipeline macht: Lint → Tests → Sicherheits‑Scans → Image bauen → Deploy auslösen.
- Für das automatische Deploy brauchst du zwei Secrets in GitHub: `RENDER_DEPLOY_HOOK_URL_API` und `RENDER_DEPLOY_HOOK_URL_FRONTEND`.

---

## Deploy auf Render

Die App ist auf Render deployt und unter den folgenden URLs erreichbar:

Live‑URLs:
- `https://lb2-frontend.onrender.com`
- `https://lb2-users-service.onrender.com`
- `https://lb2-tasks-service.onrender.com`
- `https://lb2-analytics-service.onrender.com`

Deploy‑Ablauf:
1. CI baut Images und pusht sie (GHCR).
2. CI ruft die in GitHub Secrets hinterlegten Render‑Deploy‑Hooks auf.
3. Render aktualisiert die Services.

---

## Tests & Smoke‑Checks

- Unit‑/Integration‑Tests laufen mit `pytest` (siehe `tests/`).
- Smoke‑Script `smoke.sh` prüft die `/health`‑Endpunkte remote:

`smoke.sh`:
```bash
#!/usr/bin/env bash
set -e
for url in \
  "https://lb2-analytics-service.onrender.com/health" \
  "https://lb2-users-service.onrender.com/health" \
  "https://lb2-tasks-service.onrender.com/health"; do
  echo "Checking $url"
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  if [ "$status" != "200" ]; then
    echo "FAIL: $url -> $status" >&2
    exit 1
  fi
done
echo "All health endpoints OK"
```

Ausführen:
```bash
chmod +x smoke.sh
./smoke.sh
```

---

## Häufige Probleme und Lösungen

- 404 auf `/` oder `/docs`: Stelle sicher, dass das Service aktuell deployed ist. Prüfe CI Logs und Render Logs.
- DB‑Fehler: Prüfe `DATABASE_URL` / `.env` und ob DB gestartet ist (`docker compose ps`).
- CI schlägt fehl wegen Secrets: Setze erforderliche Secrets in GitHub Repository Settings.

Logs lokal:
```bash
docker compose logs -f users-service
```

Logs remote: Render Dashboard → Service → Logs

## Architekturentscheidungen

### Warum Microservices?
Für diese Aufgabe wurde eine Microservice-Architektur gewählt. Dadurch sind Benutzerverwaltung, Aufgabenverwaltung und Analytics voneinander getrennt. Jeder Service kann unabhängig entwickelt, getestet und deployed werden.

### Warum PostgreSQL?
PostgreSQL wurde als relationale Datenbank eingesetzt. Ursprünglich wäre auch Supabase möglich gewesen. Da ich Supabase bereits für andere Projekte nutze und die kostenlose Version Einschränkungen bei den Ressourcen hat, entschied ich mich für eine separate PostgreSQL-Datenbank auf Render.

### Warum Docker Compose?
Docker Compose ermöglicht es, alle Services inklusive Datenbank mit einem einzigen Befehl lokal zu starten. Dadurch erhalten alle Teammitglieder dieselbe Entwicklungsumgebung.

### Warum GitHub Actions?
GitHub Actions automatisiert Build-, Test- und Deployment-Prozesse. Fehler werden früh erkannt und Deployments laufen reproduzierbar ab.

### Warum Render?
Render bietet eine einfache Möglichkeit, Container-Anwendungen kostenlos zu deployen und direkt mit GitHub zu verbinden. Dadurch eignet sich die Plattform gut für Lern- und Studienprojekte.



## Entscheidungen und Learnings

Diese Aufgabe war leichter als C1, C2 und C3, weil ich das Wissen schon hatte. Aber so einfach war es dann nicht.

Aus C1 kannte ich Docker, aus C2 GitHub Actions, aus C3 Cloud-Deployment. Bei LB2 musste ich alles zusammen nutzen. Das Problem: Du kennst etwas und kannst es trotzdem falsch machen.

### Was mich am meisten gerettet hat

Der 404-Fehler war das beste Beispiel. Lokal war alles okay, remote kam "404 Not Found". Ich dachte, mein Code ist kaputt. Aber nein — das Service war einfach noch nicht neu deployed. Das war blöd, weil im Remote alles länger dauert. CI muss bauen, das Image hochladen, Render zieht es — das dauert 10-15 Minuten. Local war es in 30 Sekunden klar.

Das hat mich gelehrt: lokal = nicht produktiv.

### Warum PostgreSQL statt Supabase?

Ich nutze Supabase schon für zwei andere Projekte (Prog 3 und meine Diplomarbeit). Die kostenlose Version hat aber Limits. Wenn ich noch eine dritte Datenbank dort mache, gibt es Probleme mit zu vielen Connections gleichzeitig. Also habe ich PostgreSQL in Render gemacht. So haben alle Projekte ihre eigene Datenbank und es gibt keine Konflikte.

### Copilot hilft, aber denkt nicht für dich

Copilot hat mir Unmengen Zeit bei Code sparen geholfen. Aber ob Supabase oder PostgreSQL besser ist, das musste ich selbst überlegen. Das Tool schrebt Code, nicht Architektur.

### Sachen die ich gelernt habe

1. **Multi-Stage Dockerfiles**
   
   Ich dachte, das ist fancy und optional. In Wahrheit: Das macht die Image-Größe um 60% kleiner und der Build-Müll ist weg. Das mache ich jetzt immer.

2. **Health-Checks retten dich**
   
   `/health` ist nicht nur. Das ist deine Sicherung. Render schaut drauf und sieht sofort, wenn was kaputt ist. Dann deployed es nicht weiter.

3. **Logs sind alles**
   
   Anfangs habe ich viel geraten. Dann bin ich zu den Logs gegangen und da war sofort die Antwort. Das war schneller.

4. **Deploy dauert Zeit**
   
   Lokal: 30 Sekunden. Remote: 10-15 Minuten. Das ist normal. Es bedeutet auch: Du kannst nicht alle 5 Minuten neu probieren. Das ist eigentlich gut — komische Fehler machst du nicht mehr so oft.

### Vorher und jetzt

- **C1**: Erstes Mal Docker Compose
- **C2**: GitHub Actions und Automated Builds
- **C3**: Wie deploye ich das in die Cloud
- **LB2**: Das alles zusammen und es muss funktionieren

### Das größte Learning

Die Grenze zwischen "läuft lokal" und "läuft produktiv" ist riesig. Das war die Überraschung. LB2 ist nicht so kompliziert wie C1 oder C2. Aber das Betreiben (Logs lesen, fixen, neu deployen) ist kniffliger als Code schreiben.

Jetzt, am Ende von LB2, sehe ich auch ein Problem mit meiner Diplomarbeit: Ich habe die nicht deployed, weil ich dachte, das ist zu kompliziert. Der Grund war, dass ich diesen Stoff noch nicht kannte. Jetzt könnte ich das ganz einfach. Und: Wenn die Diplomarbeit deployed wäre, müsste ich sie nicht immer lokal neu starten zum Testen. Das würde viel Zeit sparen.

**Hinweis für zukünftige Studenten:** Dieses Modul (LB2 / DevOps) sollte im 4. Semester sein, nicht im 5. Dann könnte man das Wissen noch in der Diplomarbeit nutzen. Ich hätte die wahrscheinlich ganz anders gemacht — mit Docker, CI/CD, ordentlichem Deployment. Jetzt ist es zu spät.

---

