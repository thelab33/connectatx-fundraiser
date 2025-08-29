#!/usr/bin/env python3
"""
🔎 Starforge Elite Audit — FundChamps Edition
Production-grade, CSP-first, a11y-aware, Flask-native project auditor.

Usage:
  python tools/starforge_audit.py --config app.config.DevelopmentConfig
  python tools/starforge_audit.py --config app.config.ProductionConfig --json audit.json --fail-on warn
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import traceback
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# ---------- Paths ----------
PROJECT_ROOT = Path(__file__).resolve().parents[1] if Path(__file__).resolve().parent.name == "tools" else Path(__file__).resolve().parent
APP_DIR       = PROJECT_ROOT / "app"
CONFIG_PATH   = APP_DIR / "config"
ROUTES_DIR    = APP_DIR / "routes"
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR    = APP_DIR / "static"
INIT_FILE     = APP_DIR / "__init__.py"

# ---------- Console ----------
console = Console()

# ---------- Types ----------
@dataclass
class Finding:
    check: str
    severity: str  # "info" | "ok" | "warn" | "fail"
    message: str
    file: Optional[str] = None
    ref: Optional[str] = None
    line: Optional[int] = None
    extra: Optional[dict] = None

# ---------- Helpers ----------
SEVERITY_ORDER = {"info": 0, "ok": 0, "warn": 1, "fail": 2}

def section(title: str):
    console.rule(f"[bold yellow]{title}")

def safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def add(finds: List[Finding], *items: Finding) -> None:
    finds.extend(items)

def cmd_exists(bin_name: str) -> bool:
    from shutil import which
    return which(bin_name) is not None

def run_cmd(args: List[str], cwd: Optional[Path] = None, timeout: int = 120) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(args, cwd=str(cwd) if cwd else None, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except Exception as e:
        return 1, "", str(e)

def summarize(finds: List[Finding]) -> Tuple[int, int, int, int]:
    ok = sum(1 for f in finds if f.severity == "ok")
    info = sum(1 for f in finds if f.severity == "info")
    warn = sum(1 for f in finds if f.severity == "warn")
    fail = sum(1 for f in finds if f.severity == "fail")
    return ok, info, warn, fail

# ---------- Core Checks ----------
def check_required_files() -> List[Finding]:
    req = {
        "init": INIT_FILE,
        "routes_dir": ROUTES_DIR,
        "templates": TEMPLATES_DIR,
        "static": STATIC_DIR,
    }
    finds: List[Finding] = []
    section("📦 Required Layout")
    for label, path in req.items():
        if path.exists():
            add(finds, Finding("structure", "ok", f"Found {label}", str(path)))
            print(f"[green]✅[/] {label} → {path}")
        else:
            add(finds, Finding("structure", "fail", f"Missing {label}", str(path)))
            print(f"[red]❌[/] Missing {label} → {path}")
    # Strongly suggested files
    suggested = [TEMPLATES_DIR / "base.html", TEMPLATES_DIR / "partials/ui_bootstrap.html"]
    for p in suggested:
        if p.exists():
            add(finds, Finding("structure", "ok", "Suggested file present", str(p)))
        else:
            add(finds, Finding("structure", "warn", "Suggested file missing", str(p)))
            print(f"[yellow]⚠️[/] Suggested but missing: {p}")
    return finds

def check_config_files() -> List[Finding]:
    finds: List[Finding] = []
    section("⚙️ Config Files")
    expected = ["__init__.py", "team_config.py", "config.py"]
    if not CONFIG_PATH.exists():
        add(finds, Finding("config", "fail", "No config directory", str(CONFIG_PATH)))
        print(f"[red]❌[/] No config dir at {CONFIG_PATH}")
        return finds
    for f in expected:
        p = CONFIG_PATH / f
        if p.exists():
            add(finds, Finding("config", "ok", f"Found {f}", str(p)))
            print(f"[green]✅[/] {f}")
        else:
            add(finds, Finding("config", "warn", f"Missing {f}", str(p)))
            print(f"[yellow]⚠️[/] Missing: {f}")
    return finds

def load_app(app_config: str):
    spec = importlib.util.spec_from_file_location("app", INIT_FILE)
    app_module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(app_module)  # type: ignore[attr-defined]
    app = app_module.create_app(app_config)
    return app

def audit_routes(app_config: str) -> List[Finding]:
    finds: List[Finding] = []
    section("🧭 Routes & Blueprints")
    try:
        app = load_app(app_config)
        routes = [r.rule for r in app.url_map.iter_rules()]
        bps = list(app.blueprints.keys())
        # Basics
        add(finds, Finding("routes", "ok" if "/" in routes else "fail", "Homepage route '/' present" if "/" in routes else "Homepage route '/' missing"))
        add(finds, Finding("routes", "ok" if "main" in bps else "warn", "Blueprint 'main' registered" if "main" in bps else "Blueprint 'main' not registered"))
        # Endpoints referenced by partials (nice-to-have)
        expected_ep = ["main.donate", "main.stats_json"]
        present = {r.endpoint for r in app.url_map.iter_rules()}
        for ep in expected_ep:
            if ep in present:
                add(finds, Finding("routes", "ok", f"Endpoint '{ep}' registered"))
            else:
                add(finds, Finding("routes", "warn", f"Endpoint '{ep}' not found (some widgets will fallback)"))
        # Print listing
        print("[blue]📌 Registered routes:[/]")
        for r in sorted(routes):
            print(f"  • {r}")
    except Exception as e:
        add(finds, Finding("routes", "fail", f"Route audit failed: {type(e).__name__}: {e}", str(INIT_FILE)))
        traceback.print_exc()
    return finds

def check_env_vars() -> List[Finding]:
    finds: List[Finding] = []
    section("🌐 Environment / Secrets")
    needed = ["FLASK_ENV", "FLASK_CONFIG", "FLASK_DEBUG", "DATABASE_URL", "STRIPE_API_KEY", "SECRET_KEY"]
    for var in needed:
        val = os.getenv(var)
        if val:
            add(finds, Finding("env", "ok", f"{var} set"))
            print(f"[green]✅[/] {var} = {val[:6]}…")
        else:
            add(finds, Finding("env", "warn", f"{var} is unset"))
            print(f"[yellow]⚠️[/] {var} is unset")
    # Secret hygiene
    if os.getenv("SECRET_KEY") in (None, "", "changeme", "dev", "secret", "please-change-me"):
        add(finds, Finding("env", "fail", "SECRET_KEY is default/weak or missing"))
    # Stripe hygiene
    sk = os.getenv("STRIPE_API_KEY", "")
    if sk and sk.startswith("pk_"):
        add(finds, Finding("env", "fail", "Using a Stripe publishable key as server secret (should be 'sk_…')"))
    return finds

def check_database_connection() -> List[Finding]:
    finds: List[Finding] = []
    section("🔌 Database")
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        add(finds, Finding("db", "warn", "DATABASE_URL not set"))
        print("[yellow]⚠️[/] DATABASE_URL is not set")
        return finds
    try:
        from sqlalchemy import create_engine
        engine = create_engine(db_url)
        with engine.connect() as _:
            add(finds, Finding("db", "ok", f"Connected to DB"))
            print(f"[green]✅[/] DB connection OK")
    except Exception as e:
        add(finds, Finding("db", "fail", f"DB connection failed: {e}"))
        traceback.print_exc()
    return finds

IMG_EXT_BAD = {".bmp", ".tif", ".tiff"}
IMG_EXT_OK  = {".png", ".jpg", ".jpeg", ".webp", ".svg"}

def audit_static_files() -> List[Finding]:
    finds: List[Finding] = []
    section("📁 Static Assets")
    if not STATIC_DIR.exists():
        add(finds, Finding("static", "fail", f"No static dir at {STATIC_DIR}"))
        print(f"[red]❌[/] No static directory at {STATIC_DIR}")
        return finds

    css_files = list(STATIC_DIR.glob("css/*.css"))
    js_files  = list(STATIC_DIR.glob("js/*.js"))
    img_files = list(STATIC_DIR.glob("images/*"))

    print(f"[blue]CSS:[/] {len(css_files)} • [blue]JS:[/] {len(js_files)} • [blue]Images:[/] {len(img_files)}")

    # .map leakage and oversized bundles
    for f in js_files + css_files:
        if f.suffix == ".map" or f.name.endswith(".map"):
            add(finds, Finding("static", "warn", "Source map present in production build", str(f)))
        size_kb = (f.stat().st_size / 1024) if f.exists() else 0
        if f.suffix == ".js" and size_kb > 800:
            add(finds, Finding("static", "warn", f"Large JS bundle ~{size_kb:.0f} KB", str(f)))
        if f.suffix == ".css" and size_kb > 600:
            add(finds, Finding("static", "warn", f"Large CSS file ~{size_kb:.0f} KB", str(f)))

    # Images: format/size
    for f in img_files:
        ext = f.suffix.lower()
        size_kb = (f.stat().st_size / 1024) if f.exists() else 0
        if ext in IMG_EXT_BAD:
            add(finds, Finding("static", "warn", f"Legacy/inefficient image format {ext}", str(f)))
        if size_kb > 800:
            add(finds, Finding("static", "warn", f"Oversized image ~{size_kb:.0f} KB", str(f)))

    # Check for sourcemaps alongside bundles
    for f in js_files:
        if (f.parent / (f.name + ".map")).exists():
            add(finds, Finding("static", "warn", "JS sourcemap alongside bundle", str(f.parent / (f.name + ".map"))))

    return finds

IMG_TAG_RE    = re.compile(r"<img\b[^>]*>", re.I)  # finds entire <img ...> tag
ALT_IMG_RE    = IMG_TAG_RE  # backwards compatibility for older code
ALT_ATTR_RE   = re.compile(r'\balt\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^>\s]+)', re.I)
SCRIPT_TAG_RE = re.compile(r"<script\b[^>]*>", re.I)
DUP_ID_RE = re.compile(r'id="([^"]+)"')
BAD_ANCHOR_RE = re.compile(r'<a\b[^>]*href=["\']#["\'][^>]*>', re.I)

def validate_templates() -> List[Finding]:
    finds: List[Finding] = []
    section("🖼 Templates (a11y/CSP/lint)")
    if not TEMPLATES_DIR.exists():
        add(finds, Finding("templates", "fail", "Templates dir not found", str(TEMPLATES_DIR)))
        print("[red]❌[/] No templates directory found")
        return finds

    # Enumerate templates
    html_files = list(TEMPLATES_DIR.glob("**/*.html"))
    print(f"[blue]📄 HTML templates:[/] {len(html_files)} files")

    for path in html_files:
        content = safe_read(path)
        # Images without alt
        for tag in ALT_IMG_RE.findall(content):
            if not ALT_ATTR_RE.search(tag):
                add(finds, Finding("a11y", "warn", "Image missing alt attribute", str(path)))
        # <script> without nonce (inline only)
        for tag in SCRIPT_TAG_RE.findall(content):
            # ignore external scripts with src (nonce is still OK but not strictly required)
            if "src=" in tag:
                continue
            add(finds, Finding("csp", "warn", "Inline <script> without nonce attribute", str(path)))
        # Duplicate IDs
        ids = DUP_ID_RE.findall(content)
        if ids and len(ids) != len(set(ids)):
            add(finds, Finding("html", "warn", "Duplicate id attributes found", str(path), extra={"duplicates": [i for i in ids if ids.count(i) > 1]}))
        # Anchors linking to "#" (suggest role/button)
        if BAD_ANCHOR_RE.search(content):
            add(finds, Finding("a11y", "info", "Anchor href=\"#\" found (consider role='button' + JS handler)", str(path)))
        # Aria presence
        if "aria-" not in content:
            add(finds, Finding("a11y", "info", "No ARIA attributes detected in file (may be fine)", str(path)))

    # Duplication guard: sponsors hub vs spotlight/wall on homepage
    homepage = TEMPLATES_DIR / "index.html"
    home_fallbacks = [TEMPLATES_DIR / "home.html", TEMPLATES_DIR / "pages/home.html"]
    home = homepage if homepage.exists() else next((p for p in home_fallbacks if p.exists()), None)
    if home:
        c = safe_read(home)
        if "partials/sponsors_hub.html" in c and ("sponsor_spotlight.html" in c or "sponsor_wall.html" in c or "sponsor_wall_widget.html" in c):
            add(finds, Finding("duplication", "warn", "Sponsors Hub used with individual sponsor widgets — may double-render", str(home)))

    return finds

def check_app_health_and_headers(app_config: str) -> List[Finding]:
    finds: List[Finding] = []
    section("🩺 App Health & Security Headers")
    try:
        app = load_app(app_config)
        with app.test_client() as c:
            # Health endpoint (optional)
            resp = c.get("/status")
            if resp.status_code == 200:
                add(finds, Finding("health", "ok", "Status endpoint healthy (/status)"))
                print("[green]✅[/] /status OK")
            else:
                add(finds, Finding("health", "info", f"/status returned {resp.status_code}"))

            # Home headers
            r = c.get("/")
            required = {
                "Content-Security-Policy": "csp",
                "Strict-Transport-Security": "hsts",
                "X-Frame-Options": "xfo",
                "Referrer-Policy": "referrer",
                "Permissions-Policy": "perm",
            }
            for h, tag in required.items():
                if h in r.headers:
                    add(finds, Finding("headers", "ok", f"{h} set"))
                else:
                    sev = "warn" if h != "Content-Security-Policy" else "fail"
                    add(finds, Finding("headers", sev, f"{h} missing"))

            # Cookie flags (common names)
            for cookie_name in ("session", "csrftoken"):
                morsel = next((c for c in r.headers.getlist("Set-Cookie") if c.lower().startswith(cookie_name+"=")), None)
                if not morsel:
                    continue
                low = morsel.lower()
                if "secure" not in low:
                    add(finds, Finding("cookies", "warn", f"Cookie '{cookie_name}' missing Secure"))
                if "httponly" not in low:
                    add(finds, Finding("cookies", "warn", f"Cookie '{cookie_name}' missing HttpOnly"))
                if "samesite" not in low:
                    add(finds, Finding("cookies", "info", f"Cookie '{cookie_name}' missing SameSite"))
    except Exception as e:
        add(finds, Finding("health", "fail", f"App health/header check failed: {e}"))
        traceback.print_exc()
    return finds

def check_js_fast_lints() -> List[Finding]:
    finds: List[Finding] = []
    section("🔧 JS Quick Lints")
    js_files = list(STATIC_DIR.glob("js/*.js")) if STATIC_DIR.exists() else []
    for f in js_files:
        text = safe_read(f)
        if "undefined" in text:
            add(finds, Finding("js", "info", "'undefined' literal appears (may be fine)", str(f)))
        if "console.log(" in text:
            add(finds, Finding("js", "info", "console.log present", str(f)))
        if "eval(" in text:
            add(finds, Finding("js", "warn", "eval() usage detected", str(f)))
    # Optional: eslint if present
    if cmd_exists("npx") and (PROJECT_ROOT / "package.json").exists():
        code, out, err = run_cmd(["npx", "--yes", "eslint", "--version"], cwd=PROJECT_ROOT, timeout=30)
        if code == 0:
            code, out, err = run_cmd(["npx", "--yes", "eslint", "--max-warnings=0", "."], cwd=PROJECT_ROOT, timeout=300)
            sev = "ok" if code == 0 else "warn"
            add(finds, Finding("js", sev, "ESLint run", extra={"exit": code, "out": out[-4000:], "err": err[-4000:]}))
    return finds

def check_css_fast_lints() -> List[Finding]:
    finds: List[Finding] = []
    section("🎨 CSS Quick Lints")
    css_files = list(STATIC_DIR.glob("css/*.css")) if STATIC_DIR.exists() else []
    for f in css_files:
        text = safe_read(f)
        if "@import" in text:
            add(finds, Finding("css", "info", "CSS @import present (could block rendering)", str(f)))
    return finds

def run_optional_tools() -> List[Finding]:
    finds: List[Finding] = []
    section("🧪 Optional Toolchain (ruff/bandit/pytest)")
    # ruff
    if cmd_exists("ruff"):
        code, out, err = run_cmd(["ruff", "check", "--output-format", "text", "."], cwd=PROJECT_ROOT)
        sev = "ok" if code == 0 else "warn"
        add(finds, Finding("tools", sev, "ruff check", extra={"exit": code, "out": out[-4000:], "err": err[-4000:]}))
        print(f"[cyan]ruff[/] exit {code}")
    else:
        add(finds, Finding("tools", "info", "ruff not installed; skipping"))
    # bandit
    if cmd_exists("bandit"):
        code, out, err = run_cmd(["bandit", "-q", "-r", "app"], cwd=PROJECT_ROOT)
        sev = "ok" if code == 0 else "warn"
        add(finds, Finding("tools", sev, "bandit security scan", extra={"exit": code, "out": out[-4000:], "err": err[-4000:]}))
        print(f"[cyan]bandit[/] exit {code}")
    else:
        add(finds, Finding("tools", "info", "bandit not installed; skipping"))
    # pytest
    if cmd_exists("pytest") and (PROJECT_ROOT / "tests").exists():
        code, out, err = run_cmd(["pytest", "-q"], cwd=PROJECT_ROOT)
        sev = "ok" if code == 0 else "warn"
        add(finds, Finding("tools", sev, "pytest suite", extra={"exit": code, "out": out[-4000:], "err": err[-4000:]}))
        print(f"[cyan]pytest[/] exit {code}")
    else:
        add(finds, Finding("tools", "info", "pytest not run (missing or no tests)"))
    return finds

# ---------- Main ----------
def run_audit(app_config: str) -> List[Finding]:
    all_finds: List[Finding] = []
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as prog:
        prog.add_task(description="Scanning structure…", total=None)
        all_finds += check_required_files()
        all_finds += check_config_files()

        prog.add_task(description="Inspecting app routes…", total=None)
        all_finds += audit_routes(app_config)

        prog.add_task(description="Checking environment…", total=None)
        all_finds += check_env_vars()

        prog.add_task(description="Database connectivity…", total=None)
        all_finds += check_database_connection()

        prog.add_task(description="Static assets…", total=None)
        all_finds += audit_static_files()

        prog.add_task(description="Template & a11y lint…", total=None)
        all_finds += validate_templates()

        prog.add_task(description="App health & headers…", total=None)
        all_finds += check_app_health_and_headers(app_config)

        prog.add_task(description="JS/CSS quick lints…", total=None)
        all_finds += check_js_fast_lints()
        all_finds += check_css_fast_lints()

        prog.add_task(description="Optional external tools…", total=None)
        all_finds += run_optional_tools()

    return all_finds

def print_summary(finds: List[Finding], fail_on: str) -> int:
    ok, info, warn, fail = summarize(finds)

    # Pretty table
    table = Table(title="Audit Summary", show_lines=False)
    table.add_column("Severity", style="bold")
    table.add_column("Count", justify="right")
    table.add_row("✅ OK", str(ok))
    table.add_row("ℹ️ Info", str(info))
    table.add_row("⚠️ Warn", str(warn))
    table.add_row("❌ Fail", str(fail))
    console.print(table)

    # Exit code policy
    threshold = SEVERITY_ORDER.get(fail_on, 2)
    worst = max((SEVERITY_ORDER.get(f.severity, 0) for f in finds), default=0)
    exit_code = 1 if worst >= threshold and worst > 0 else 0

    # Detail panel (top offenders)
    if warn or fail:
        section("Top Findings")
        # show up to 30
        shown = 0
        for f in finds:
            if f.severity in ("warn", "fail"):
                loc = f.file if f.file else ""
                console.print(f"[{ 'red' if f.severity=='fail' else 'yellow'}]{f.severity.upper()}[/] {f.check}: {f.message} {loc}")
                shown += 1
                if shown >= 30:
                    console.print("… (truncated)")
                    break

    badge = "[bold green]PASS[/]" if exit_code == 0 else "[bold red]ATTENTION REQUIRED[/]"
    console.print(Panel.fit(f"{badge} • ok={ok} info={info} warn={warn} fail={fail}", style="magenta"))
    return exit_code

def main():
    parser = argparse.ArgumentParser(description="Starforge Elite Audit")
    parser.add_argument("--config", default="app.config.DevelopmentConfig", help="Flask app config import path")
    parser.add_argument("--json", dest="json_out", default=None, help="Write findings JSON to path")
    parser.add_argument("--fail-on", choices=["warn", "fail"], default="fail", help="Exit non-zero on ≥ this severity")
    args = parser.parse_args()

    print(Panel.fit("[bold cyan]🧪 Starforge Elite Auditor[/]  —  CSP • A11Y • Headers • Routes • Assets", style="bold magenta"))

    try:
        findings = run_audit(args.config)
    except Exception as e:
        console.print(f"[red]Fatal audit error:[/] {e}")
        traceback.print_exc()
        sys.exit(2)

    # JSON output
    if args.json_out:
        payload = [asdict(f) for f in findings]
        Path(args.json_out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"[blue]📝 Wrote JSON report →[/] {args.json_out}")

    exit_code = print_summary(findings, args.fail_on)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

