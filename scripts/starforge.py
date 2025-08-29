#!/usr/bin/env python3
import click, sys, runpy, inspect
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]

SAFE = {
    "inspect-stack": "starforge_inspect.py",
    "audit-partials": "starforge_check_partials.py",
    "audit-templates": "starforge_check_templates.py",
    "audit-jinja": "audit_jinja.py",
    "audit-static": "audit_static_files.py",
    "audit-project": "audit_project.py",
    "audit-spacing": "audit_section_spacing.py",
}

def _load_module(abs_path: Path):
    spec = importlib.util.spec_from_file_location(abs_path.stem, abs_path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Cannot import {abs_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[abs_path.stem] = mod
    spec.loader.exec_module(mod)
    return mod

def _invoke_best_effort(mod, cmd_name: str, abs_path: Path):
    # Try run(cmd), run(), main(), else run as script via runpy.
    if hasattr(mod, "run"):
        sig = inspect.signature(mod.run)
        if len(sig.parameters) == 1:
            return mod.run(cmd_name)
        return mod.run()
    if hasattr(mod, "main"):
        return mod.main()
    # Last resort: execute file (may define __main__ behavior)
    ns = runpy.run_path(str(abs_path))
    # If it exposes RESULT, use it; otherwise assume success
    return ns.get("RESULT", 0)

@click.group(help="Starforge MVP CLI — safe, read-only audits")
def cli():
    pass

def _make_cmd(cmd, rel_path):
    @cli.command(name=cmd)
    def _cmd():
        abs_path = (ROOT / rel_path).resolve()
        try:
            mod = _load_module(abs_path)
            rc = _invoke_best_effort(mod, cmd, abs_path)
            if isinstance(rc, bool):
                rc = 0 if rc else 1
            if rc not in (None, 0):
                click.secho(f"{cmd} exited with code {rc}", fg="red")
                sys.exit(rc)
        except SystemExit:
            raise
        except Exception as e:
            click.secho(f"Error running {cmd}: {e}", fg="red")
            sys.exit(1)
    return _cmd

for _cmd, _path in SAFE.items():
    _make_cmd(_cmd, _path)

if __name__ == "__main__":
    cli()

