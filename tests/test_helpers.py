import pytest
import app.helpers as helpers


# ───────────────────────────────────────────────
# _num parsing
# ───────────────────────────────────────────────

@pytest.mark.parametrize("inp, expected", [
    (0, 0.0),
    (123, 123.0),
    (123.45, 123.45),
    ("1,200", 1200.0),
    ("$1_200", 1200.0),
    ("USD 1,200", 1200.0),
    ("(123.45)", -123.45),
    ("10k", 10_000.0),
    ("1.2m", 1_200_000.0),
    ("2b", 2_000_000_000.0),
    ("", 0.0),
    ("garbage", 0.0),
    (None, 0.0),
])
def test__num_parsing(inp, expected):
    assert helpers._num(inp) == pytest.approx(expected)


# ───────────────────────────────────────────────
# _pct stable percentage
# ───────────────────────────────────────────────

@pytest.mark.parametrize("n, d, expected", [
    (50, 100, 50.0),
    (1, 3, 33.3),
    (0, 10, 0.0),
    (10, 0, 0.0),
    ("25", "200", 12.5),
])
def test__pct(n, d, expected):
    assert helpers._pct(n, d) == pytest.approx(expected, rel=1e-3, abs=1e-3)


# ───────────────────────────────────────────────
# _calc_next_milestone_gap
# ───────────────────────────────────────────────

def test__calc_next_milestone_gap_basic():
    total = 1000
    allocated = 200
    milestones = [
        {"label": "Stage A", "cost": 200},
        {"label": "Stage B", "cost": 300},
        {"label": "Stage C", "cost": 500},
    ]
    gap, label = helpers._calc_next_milestone_gap(total, allocated, milestones)
    assert gap == pytest.approx(300.0)
    assert label == "Stage B"


def test__calc_next_milestone_gap_past_all():
    total, allocated = 1000, 950
    milestones = [
        {"label": "A", "cost": 200},
        {"label": "B", "cost": 300},
        {"label": "C", "cost": 500},
    ]
    gap, label = helpers._calc_next_milestone_gap(total, allocated, milestones)
    assert gap == pytest.approx(50.0)
    assert label == "Goal"


def test__calc_next_milestone_gap_no_milestones():
    gap, label = helpers._calc_next_milestone_gap(800, 120, milestones=[])
    assert gap == pytest.approx(680.0)
    assert label == "Goal"


def test__calc_next_milestone_gap_fully_funded():
    gap, label = helpers._calc_next_milestone_gap(500, 500, milestones=[{"label": "A", "cost": 250}])
    assert gap == 0.0
    assert label == "Fully funded"


# ───────────────────────────────────────────────
# emit_funds_update smoke
# ───────────────────────────────────────────────

class StubSocketIO:
    def __init__(self):
        self.emits = []

    def emit(self, event, payload, broadcast=False):
        self.emits.append((event, payload.copy(), {"broadcast": bool(broadcast)}))


def test_emit_funds_update_with_socketio():
    stub = StubSocketIO()
    helpers.emit_funds_update(raised=1000, goal=5000, sponsor_name="TechNova", socketio=stub)
    helpers.emit_funds_update(raised=1250, goal=5000, sponsor_name=None, socketio=stub)

    assert len(stub.emits) == 2
    ev1, p1, kw1 = stub.emits[0]
    ev2, p2, kw2 = stub.emits[1]

    assert ev1 == ev2 == "funds:update"
    assert kw1["broadcast"] is True and kw2["broadcast"] is True
    assert p1["raised"] == 1000.0 and p1["goal"] == 5000.0
    assert p2["raised"] == 1250.0
    assert isinstance(p1["seq"], int) and p2["seq"] > p1["seq"]


def test_emit_funds_update_with_explicit_seq_and_fallback():
    captured = {}

    def fbk(r, g, s, seq):
        captured.update({"r": r, "g": g, "s": s, "seq": seq})

    helpers.emit_funds_update(raised="2k", goal="10k", sponsor_name=None, seq=42, fallback=fbk)

    assert captured == {"r": 2000.0, "g": 10000.0, "s": None, "seq": 42}

