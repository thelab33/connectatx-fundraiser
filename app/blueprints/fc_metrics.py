import os, json, datetime
from flask import Blueprint, request, jsonify
from redis import Redis

bp = Blueprint("fc_metrics", __name__, url_prefix="/api/metrics")
R = Redis.from_url(os.getenv("REDIS_URL","redis://localhost:6379/0"))

def _now(): return datetime.datetime.utcnow()
def _week_key(dt=None):
    dt = dt or _now(); iso = dt.isocalendar(); return f"{iso[0]}-W{iso[1]:02d}"

@bp.post("/impression")
def impression():
    key = request.json.get("key","hub")
    wk  = _week_key()
    R.hincrby(f"fc:roi:{wk}", f"imp:{key}", 1)
    R.hincrby(f"fc:roi:{wk}", "impressions", 1)
    return ("",204)

@bp.post("/click")
def click():
    key = request.json.get("key","sponsor")
    wk  = _week_key()
    R.hincrby(f"fc:roi:{wk}", f"click:{key}", 1)
    R.hincrby(f"fc:roi:{wk}", "clicks", 1)
    return ("",204)

@bp.get("/roi/weekly")
def weekly():
    wk = _week_key()
    h  = {k.decode(): v.decode() for k,v in R.hgetall(f"fc:roi:{wk}").items()}
    recent = [json.loads(x) for x in R.lrange("fc:recent_donations", 0, 24)]
    return jsonify({"week": wk, "metrics": h, "recent": recent})
