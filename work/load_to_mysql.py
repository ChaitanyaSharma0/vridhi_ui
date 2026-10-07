"""Load the Vriddhi database into MySQL (local MySQL 8 or a hosted MySQL such as Railway).

Connection is read from environment variables or a .env file next to this script:
    MYSQL_URL=mysql://user:password@host:port/vriddhi        (Railway provides this as MYSQL_URL / MYSQL_PUBLIC_URL)
  or MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

Runs, in order: 01_create_schema.sql, 02_load_staging.sql, 03_load_core.sql, 04_views.sql, then 05_verify.sql
and prints every verification result.  Usage:  python load_to_mysql.py
Requires:  pip install pymysql
"""
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

import pymysql

HERE = Path(__file__).resolve().parent
SQL = HERE / "database" / "sql"


def read_env():
    env = dict(os.environ)
    f = HERE / ".env"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return env


def connection_args(env):
    url = env.get("MYSQL_PUBLIC_URL") or env.get("MYSQL_URL") or env.get("DATABASE_URL")
    if url:
        u = urlparse(url)
        if u.hostname and u.hostname.endswith(".railway.internal"):
            sys.exit("This is Railway's PRIVATE address (mysql.railway.internal) - it only works inside Railway.\n"
                     "Copy MYSQL_PUBLIC_URL instead (host like xxxx.proxy.rlwy.net:PORT) from the MySQL service's Variables tab.\n"
                     "If it is missing: MySQL service -> Settings -> Networking -> enable the TCP proxy / public networking.")
        return dict(host=u.hostname, port=u.port or 3306, user=unquote(u.username or ""), password=unquote(u.password or ""),
                    database=(u.path or "/").lstrip("/") or None)
    return dict(host=env.get("MYSQL_HOST", "127.0.0.1"), port=int(env.get("MYSQL_PORT", 3306)), user=env.get("MYSQL_USER", "root"),
                password=env.get("MYSQL_PASSWORD", ""), database=env.get("MYSQL_DATABASE"))


def statements(path):
    """Data files: one INSERT per line. DDL/view files: statements end with ';' at end of line (no ';' inside them)."""
    text = path.read_text(encoding="utf-8")
    text = "\n".join(l for l in text.splitlines() if not l.strip().startswith("--"))
    return [s.strip().rstrip(";").strip() for s in re.split(r";\s*\n", text + "\n") if s.strip().rstrip(";").strip()]


def main():
    env = read_env()
    args = connection_args(env)
    target_db = args.pop("database") or "vriddhi"
    print(f"Connecting to {args['host']}:{args['port']} as {args['user']} (database '{target_db}') ...")
    conn = pymysql.connect(**args, charset="utf8mb4", autocommit=False, local_infile=False)
    cur = conn.cursor()
    for name in ["01_create_schema.sql", "02_load_staging.sql", "03_load_core.sql", "04_views.sql"]:
        stmts = statements(SQL / name)
        if target_db != "vriddhi":  # hosted DBs (e.g. Railway's 'railway') may not allow CREATE DATABASE
            stmts = [s for s in stmts if not s.upper().startswith("CREATE DATABASE")]
            stmts = [f"USE `{target_db}`" if s.upper().startswith("USE ") else s for s in stmts]
        for i, s in enumerate(stmts, 1):
            cur.execute(s)
            if i % 25 == 0 or i == len(stmts):
                print(f"  {name}: {i}/{len(stmts)} statements", end="\r")
        conn.commit()
        print(f"  {name}: done ({len(stmts)} statements)          ")
    print("\nVerification:")
    failed = 0
    for s in statements(SQL / "05_verify.sql"):
        if s.upper().startswith("USE "):
            cur.execute(f"USE `{target_db}`")
            continue
        cur.execute(s)
        cols = [d[0] for d in cur.description]
        for row in cur.fetchall():
            r = dict(zip(cols, row))
            ok = r.get("result", "PASS" if str(r.get("actual")) == str(r.get("expected")) or
                       (r.get("actual") is not None and r.get("expected") is not None and abs(float(r["actual"]) - float(r["expected"])) < 1e-3) else "FAIL")
            failed += ok != "PASS"
            print(f"  [{ok}] {r.get('check_name')} {r.get('table_name') or r.get('dimension_code') or ''}: actual={r.get('actual')} expected={r.get('expected')}")
    conn.close()
    print(f"\n{'ALL CHECKS PASSED' if not failed else f'{failed} CHECK(S) FAILED'}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
