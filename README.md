# Automated CI/CD Pipeline for a Containerized QR Code Generator

A Flask web service that generates real QR codes from URLs or plain text. It is
tested with pytest, packaged with Docker, and built and published through
GitHub Actions.

## Features

- Responsive HTML/CSS browser interface
- Server-side PNG QR generation with `qrcode` and Pillow
- Downloadable QR code images
- Empty, whitespace-only, and oversized input validation
- Flask health endpoint at `/healthz`
- Gunicorn production server
- Non-root Docker image with a health check
- Pull-request testing and main-branch GHCR publishing

## Architecture

```text
Browser -> Flask/Gunicorn -> qrcode + Pillow
                    |
             Docker container
                    |
       GitHub Actions -> GHCR
```

The optional remote deployment setup adds Caddy as an HTTPS reverse proxy:

```text
Internet -> Caddy (80/443) -> Flask container (5000)
```

## Project structure

```text
app.py                         Flask routes and QR generation
templates/index.html           Generator page
templates/error.html           Error page
static/style.css               Responsive styling
tests/test_app.py              Flask test-client tests
Dockerfile                     Gunicorn production image
compose.yaml                   Local Docker Compose setup
.github/workflows/ci-cd.yml    CI and GHCR publishing
deploy/                        Optional SSH/Caddy deployment files
```

## Requirements

Install on Windows:

- Python 3.12
- Docker Desktop
- Git

## Run locally with Python

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python app.py
```

Open <http://localhost:5000>.

## Test

```powershell
.\.venv\Scripts\Activate.ps1
pytest --cov=. --cov-report=term-missing --cov-fail-under=85
ruff check .
ruff format --check .
```

## Run with Docker Compose

```powershell
docker compose up --build
```

Open:

- <http://localhost:5000>
- <http://localhost:5000/healthz>

Stop it with:

```powershell
docker compose down
```

## API and form routes

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/` | Web generator interface |
| POST | `/generate` | Validate input and display a QR code |
| POST | `/download` | Return a QR PNG as an attachment |
| GET | `/healthz` | Container health check |

The default maximum input length is 1024 characters and can be changed with
`QR_MAX_DATA_LENGTH`.

## GitHub Actions and GHCR

[.github/workflows/ci-cd.yml](.github/workflows/ci-cd.yml) runs on pull requests
and pushes to `main`. It:

1. Installs dependencies.
2. Runs Ruff and pytest on Python 3.11 and 3.12.
3. Audits runtime dependencies.
4. Builds and smoke-tests the Docker image.
5. Publishes only trusted `main` builds to GHCR.

Create a GitHub repository and push from PowerShell:

```powershell
git init
git add .
git commit -m "Build Flask QR generator"
git branch -M main
git remote add origin https://github.com/OWNER/REPOSITORY.git
git push -u origin main
```

The workflow publishes an image similar to:

```text
ghcr.io/owner/repository:main
```

To pull it from another computer, make the GHCR package public in GitHub
package settings, then run:

```powershell
docker pull ghcr.io/owner/repository:main
docker run --rm -p 5000:5000 ghcr.io/owner/repository:main
```

For a private package, authenticate first with a GitHub token that has
`read:packages`:

```powershell
docker login ghcr.io -u GITHUB_USERNAME
docker pull ghcr.io/owner/repository:main
```

## Optional server deployment

The files in `deploy/` are intended for an Ubuntu Docker host with a domain,
ports 80/443 open, and an SSH deploy user. Configure the `staging` and
`production` GitHub environments with:

- Variables: `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_PATH`, `APP_DOMAIN`
- Secrets: `SSH_PRIVATE_KEY`, `SSH_KNOWN_HOSTS`

The deployment workflow copies the Compose, Caddy, and rollback scripts, logs
into GHCR, and verifies `/healthz`, `/`, and `/download`. A real server,
domain, SSH key, and GitHub settings are required; this local project does not
claim that a remote deployment has occurred.

## Troubleshooting

- **Port already in use:** run `docker compose down`, or change the host side
  of `5000:5000`.
- **PowerShell activation blocked:** run
  `Set-ExecutionPolicy -Scope Process Bypass`.
- **Docker daemon unavailable:** start Docker Desktop and retry.
- **GHCR permission denied:** make the package public or use a token with
  `read:packages`.
- **404 at the browser root:** confirm the container exposes port 5000 and
  open `http://localhost:5000`, not port 8000.

## Demonstration checklist

1. Run `docker compose up --build`.
2. Open the web interface and then enter `https://example.com`.
3. Show the generated QR code and download it.
4. Open `/healthz` to show the container probe.
5. Show the GitHub Actions run and its test/build stages.
6. Show the GHCR image only after a real push has completed.
