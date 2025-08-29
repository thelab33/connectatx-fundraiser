#!/usr/bin/env python3
"""
Starforge Inspector — Full-Stack Report Tool
------------------------------------------------
Run in project root. Collects and prints:
- Python env (Flask, SQLAlchemy, Celery, etc.)
- Node env (React, Tailwind, Vite, etc.)
- Git + .env details
- DB + services (Redis, Postgres, Stripe keys, S3 buckets)
- System info

Author: FundChamps / Starforge
"""

import os, sys, subprocess, platform, json, shutil, pathlib
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parent

def run(cmd, cwd=None):
    try:
        return subprocess.check_output(cmd, shell=True, cwd=cwd, stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return None

def read_json(path):
    try:
        with open(path) as f: return json.load(f)
    except Exception: return {}

def heading(title):
    print("\n" + "="*len(title))
    print(title)
    print("="*len(title))

def section(title):
    print(f"\n--- {title} ---")

def inspect_python():
    section("Python Environment")
    print("Python:", sys.version.split()[0])
    print("Platform:", platform.platform())
    pkgs = run("pip freeze")
    if pkgs:
        for k in ["Flask", "SQLAlchemy", "Celery", "Flask-SocketIO", "Flask-Migrate"]:
            for line in pkgs.splitlines():
                if line.lower().startswith(k.lower()):
                    print(" ", line)

def inspect_node():
    section("Node Environment")
    node, npm, pnpm = run("node -v"), run("npm -v"), run("pnpm -v")
    if node: print("Node:", node)
    if npm: print("npm:", npm)
    if pnpm: print("pnpm:", pnpm)
    pkg = read_json(ROOT/"package.json")
    if pkg:
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        for k in ["react", "vite", "tailwindcss", "eslint", "prettier"]:
            if k in deps: print(f" {k}:", deps[k])

def inspect_git():
    section("Git Repository")
    branch = run("git rev-parse --abbrev-ref HEAD")
    commit = run("git rev-parse --short HEAD")
    remote = run("git config --get remote.origin.url")
    if branch: print("Branch:", branch)
    if commit: print("Commit:", commit)
    if remote: print("Remote:", remote)

def inspect_env():
    section(".env Configuration")
    env_path = ROOT/".env"
    if not env_path.exists(): print("No .env file found"); return
    with open(env_path) as f:
        for line in f:
            if "=" not in line: continue
            key,val = line.strip().split("=",1)
            if "KEY" in key or "SECRET" in key or "PASS" in key:
                print(f"{key}=**** (hidden)")
            else:
                print(f"{key}={val}")

def inspect_services():
    section("Service Config")
    # Postgres / DB
    db = os.environ.get("DATABASE_URL") or os.environ.get("SQLALCHEMY_DATABASE_URI")
    if db: print("Database:", db.split("@")[-1]) # mask creds
    # Redis
    redis = os.environ.get("REDIS_URL")
    if redis: print("Redis:", redis.split("@")[-1])
    # Stripe
    stripe = os.environ.get("STRIPE_PUBLIC_KEY")
    if stripe: print("Stripe PK:", stripe[:12]+"…")
    # S3 / R2
    s3 = os.environ.get("AWS_S3_BUCKET") or os.environ.get("R2_BUCKET")
    if s3: print("S3 Bucket:", s3)

def inspect_frontend_build():
    section("Frontend Build")
    if (ROOT/"vite.config.js").exists() or (ROOT/"vite.config.ts").exists():
        print("Vite config found")
    if (ROOT/"tailwind.config.js").exists() or (ROOT/"tailwind.config.cjs").exists():
        print("Tailwind config found")
    if (ROOT/"esbuild.config.js").exists():
        print("Esbuild config found")

def main():
    heading("⚡ Starforge Full-Stack Inspector ⚡")
    print("Timestamp:", datetime.now().isoformat())
    print("Project root:", ROOT)
    inspect_python()
    inspect_node()
    inspect_git()
    inspect_env()
    inspect_services()
    inspect_frontend_build()
    print("\n✅ Inspection complete.")

if __name__ == "__main__":
    main()

