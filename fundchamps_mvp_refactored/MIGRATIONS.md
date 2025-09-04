# Migrations

Use Alembic for schema changes.

```bash
alembic init migrations
alembic revision -m "init" --autogenerate
alembic upgrade head
```

Notes:

- Keep models authoritative; autogenerate, then review.
- Record any manual data migrations here.
