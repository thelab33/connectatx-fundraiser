#!/usr/bin/env python3
import click, sys, runpy, inspect, types
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

def _call_safely(fn, *args):
    """Try calling fn with given args; on TypeError (arity), try without args."""
    try:
        return fn(*args)
    except TypeError:
        return fn()

def _invoke_best_effort(mod, cmd_name: str, abs_path: Path):
    # Prefer a module-level "run"
    rn = getattr(mod, "run", None)
    if callable(rn) and not isinstance(rn, click.Command):
        # Always try run(cmd_name) first, then run()
        try:
            return _call_safely(rn, cmd_name)
        except SystemExit:
            raise
        except Exception:
            # Last chance: try no-arg again explicitly
            return rn()

    # Then try a module-level "main"
    mn = getattr(mod, "main", None)
    if callable(mn) and not isinstance(mn, click.Command):
        return _call_safely(mn, cmd_name)

    # Fallback: execute the file (may define __main__ behavior)
    ns = runpy.run_path(str(abs_path))
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

