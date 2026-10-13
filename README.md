# Library Management System with Automated CI/CD Pipeline

Flask + SQLite application integrated with Git/GitHub, Jenkins, Docker, Pytest and a persistent Docker Volume.

## Features
- Add books and view the catalogue
- Register and view members
- Issue books and record returns
- Dashboard counters and `/health` endpoint
- Jenkins pipeline: checkout, Docker build, automated tests, deployment and verification
- Docker Volume `library_data` preserves SQLite records across container replacement

## Run locally (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000

## Test
```powershell
python -m pytest -q tests
```

## Docker
```powershell
docker build -t library-management-system:latest .
docker volume create library_data
docker run -d --name library-management-app -p 5001:5000 -v library_data:/app/data library-management-system:latest
```
Open http://localhost:5001

## Jenkins requirements
The Jenkins agent must have Git, Docker CLI, Docker Engine access, and a Unix-compatible shell for the `sh` steps. Configure a Pipeline job as **Pipeline script from SCM**, select Git, enter the GitHub repository URL, and set Script Path to `Jenkinsfile`. Configure a GitHub webhook or SCM polling for automatic triggers.

This is a classroom demonstration, not a production-ready system. Add authentication, authorization, CSRF protection, backups and secure deployment settings before real-world use.
