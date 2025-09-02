# Build & Run

## Python (virtualenv)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Frontend
```bash
npm ci
npm run build   # outputs to static/build/
```

## Local Run
```bash
export $(grep -v '^#' .env.example | xargs)  # for local defaults
flask --app app run --debug
```

## Seeds
```bash
python -m app.seed seeds/seed.json
```
