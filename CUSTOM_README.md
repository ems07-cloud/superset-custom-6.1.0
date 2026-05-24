# Superset 6.1.0 — Custom Build

Production build of Apache Superset 6.1.0 with the following changes:

- `clickhouse-connect` bundled in the image
- "Powered by Apache Superset" removed from Settings → About
- Custom favicon (`superset/static/custom-favicon.svg`) and logo
  (`superset/static/custom-logo.svg`)
- Default landing dashboard configurable via the
  `SUPERSET_DEFAULT_DASHBOARD_ID` environment variable
- `/superset/` URL prefix dropped sitewide (e.g. `/dashboard/1/`
  instead of `/superset/dashboard/1/`)

## Build

```bash
docker build --target lean -t superset:6.1.0-custom .
```

## Run

First-time bootstrap (creates admin user, runs migrations):

```bash
docker run --rm -d --name superset -p 8088:8088 \
  -e SUPERSET_SECRET_KEY=change-me \
  -e ADMIN_USERNAME=admin -e ADMIN_PASSWORD=admin -e ADMIN_EMAIL=admin@example.com \
  -e SUPERSET_DEFAULT_DASHBOARD_ID=1 \
  superset:6.1.0-custom
docker exec superset bash /app/docker/docker-init.sh
```

Subsequent runs:

```bash
docker run --rm -d -p 8088:8088 \
  -e SUPERSET_SECRET_KEY=change-me \
  -e SUPERSET_DEFAULT_DASHBOARD_ID=1 \
  superset:6.1.0-custom
```

Open `http://localhost:8088`.

## Environment variables

| Variable | Purpose |
| -------- | ------- |
| `SUPERSET_SECRET_KEY` | Flask session signing key (required). |
| `SUPERSET_DEFAULT_DASHBOARD_ID` | Dashboard `id` or `slug`. When set, `/` redirects to `/dashboard/<id>/`. Accepts a numeric id (`1`) or slug (`sales_overview`). |
| `SUPERSET_CONFIG_PATH` | Path to a Python file that overrides `superset/config.py`. |
| `DATABASE_URL` | SQLAlchemy URL for the metadata database. Defaults to SQLite under `/app/superset_home/`. |

## URL changes

| Before | After |
| ------ | ----- |
| `/superset/welcome/` | `/welcome/` |
| `/superset/dashboard/<id>/` | `/dashboard/<id>/` |
| `/superset/explore/p/<key>/` | `/explore/p/<key>/` |
| `/superset/tags/` | `/tags/` |
| `/superset/all_entities/` | `/all_entities/` |
| `/superset/sql/<id>/` | `/sql/<id>/` |

If you have old bookmarks behind a proxy, add a 301:

```nginx
location /superset/ { rewrite ^/superset/(.*)$ /$1 permanent; }
```

## Landing dashboard

`/` redirects to `/dashboard/<id>/` when `SUPERSET_DEFAULT_DASHBOARD_ID`
is set (one 302, same as upstream's `/` → `/welcome/`). Access is
governed by the dashboard's own permissions — non-Admin users see it
when they are an owner, have a role granted on the dashboard, or the
dashboard is published with their role. Without access they get 404
(Superset's standard behaviour for denied dashboards).

`/welcome/` keeps the standard Home page.

## Applying the patch series

```bash
git checkout 6.1.0
git checkout -b superset-custom-6.1.0
git am PR/*.patch
```
