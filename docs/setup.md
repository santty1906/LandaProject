# Local Development Setup

## 1) Clone

```bash
git clone <repository-url>
cd LandaProject
```

## 2) Environment files

Copy examples and edit values as needed:

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

## 3) Start database and backend with Docker

```bash
docker compose up --build
```

## 4) Backend local run (without Docker, optional)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
uvicorn app.main:app --reload
```

## 5) Frontend local run

```bash
cd frontend
flutter pub get
flutter run
```

## Collaboration workflow

- Create feature branches from `main`
- Keep PRs focused and small
- Run tests locally before opening PRs
- Use conventional commit messages when possible
