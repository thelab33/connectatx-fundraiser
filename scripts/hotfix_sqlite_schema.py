import sqlite3, os, sys
DB = os.path.join(os.path.dirname(__file__), "..", "app", "data", "app.db")
DB = os.path.abspath(DB)

def col_exists(cur, table, col):
    cur.execute("PRAGMA table_info(%s)" % table)
    return any(r[1] == col for r in cur.fetchall())

def table_empty(cur, table):
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    return cur.fetchone()[0] == 0

def main():
    print(f"[hotfix] DB: {DB}")
    con = sqlite3.connect(DB)
    cur = con.cursor()

    # sponsors.status
    if not col_exists(cur, "sponsors", "status"):
        print("[hotfix] Adding sponsors.status (TEXT DEFAULT 'approved')")
        cur.execute("ALTER TABLE sponsors ADD COLUMN status TEXT DEFAULT 'approved'")

    # sponsors.deleted
    if not col_exists(cur, "sponsors", "deleted"):
        print("[hotfix] Adding sponsors.deleted (INTEGER DEFAULT 0)")
        cur.execute("ALTER TABLE sponsors ADD COLUMN deleted INTEGER DEFAULT 0")

    # campaign_goals.uuid
    if not col_exists(cur, "campaign_goals", "uuid"):
        print("[hotfix] Adding campaign_goals.uuid (TEXT)")
        cur.execute("ALTER TABLE campaign_goals ADD COLUMN uuid TEXT")

    con.commit()

    # Ensure one active goal exists
    # If table has zero rows, insert a default active row.
    if table_empty(cur, "campaign_goals"):
        print("[hotfix] Seeding default active campaign goal (goal_amount=10000, total=0)")
        cur.execute("""
            INSERT INTO campaign_goals (uuid, goal_amount, total, active, created_at, updated_at, deleted)
            VALUES ('seed-default', 10000, 0, 1, datetime('now'), datetime('now'), 0)
        """)
        con.commit()

    print("[hotfix] Done.")
    con.close()

if __name__ == "__main__":
    main()
