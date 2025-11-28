# tests/test_load_to_postgres.py

import sys
from pathlib import Path
import json
import io

import pandas as pd
import pytest

# Make sure we can import load_to_postgres from the package root
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import load_to_postgres as loader  # noqa: E402


# -----------------------------
# Small utilities
# -----------------------------

def test_coerce_intlike_basic():
    df = pd.DataFrame(
        {
            "a": [1.1, 2.9, None],
            "b": ["3", "4.7", ""],
            "c": ["x", "y", "z"],
        }
    )

    out = loader.coerce_intlike(df.copy(), ["a", "b", "missing"])

    # a and b become nullable integer
    assert str(out["a"].dtype) == "Int64"
    assert str(out["b"].dtype) == "Int64"
    # rounding applied
    assert list(out["a"]) == [1, 3, pd.NA]
    assert list(out["b"]) == [3, 5, pd.NA]
    # c untouched
    assert list(out["c"]) == ["x", "y", "z"]


def test_df_to_csv_buffer_formatting():
    df = pd.DataFrame(
        {
            "x": [1, 2],
            "y": [3.0, 4.0],   # floats but integral values
        }
    )
    buf = loader.df_to_csv_buffer(df)
    buf.seek(0)
    content = buf.read()

    # No header, no index
    assert content.strip().splitlines() == ["1,3", "2,4"]
    # ensure there's no ".0" in the representation
    assert ".0" not in content


# -----------------------------
# get_db_credentials
# -----------------------------

def test_get_db_credentials(monkeypatch):
    # Fake SSM and SecretsManager clients
    class FakeSSM:
        def __init__(self):
            self.values = {
                "/aidoctors/db/host": "db-host",
                "/aidoctors/db/port": "5432",
                "/aidoctors/db/user": "db-user",
                "/aidoctors/db/name": "db-name",
                "/aidoctors/db/schema": "db-schema",
                "/aidoctors/db/password-secret-arn": "secret-arn",
            }

        def get_parameter(self, Name):
            return {"Parameter": {"Value": self.values[Name]}}

    class FakeSecrets:
        def get_secret_value(self, SecretId):
            # SecretId is "secret-arn"
            return {
                "SecretString": json.dumps({"password": "super-secret-pw"})
            }

    def fake_client(service_name):
        if service_name == "ssm":
            return FakeSSM()
        elif service_name == "secretsmanager":
            return FakeSecrets()
        raise ValueError(f"unexpected service {service_name}")

    monkeypatch.setattr(loader.boto3, "client", fake_client)

    host, port, user, password, dbname, schema = loader.get_db_credentials()
    assert host == "db-host"
    assert port == "5432"
    assert user == "db-user"
    assert dbname == "db-name"
    assert schema == "db-schema"
    assert password == "super-secret-pw"


# -----------------------------
# connect()
# -----------------------------

def test_connect_success(monkeypatch):
    # Stub credentials
    monkeypatch.setattr(
        loader, "get_db_credentials",
        lambda: ("h", "5432", "u", "pw", "dbname", "myschema")
    )

    class FakeConn:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.autocommit = False

    def fake_connect(host, port, user, password, dbname):
        return FakeConn(
            host=host, port=port, user=user, password=password, dbname=dbname
        )

    monkeypatch.setattr(loader.psycopg2, "connect", fake_connect)

    conn, schema = loader.connect()
    assert isinstance(conn, FakeConn)
    assert conn.autocommit is True
    assert schema == "myschema"
    assert conn.kwargs["host"] == "h"


def test_connect_failure(monkeypatch):
    # Stub credentials
    monkeypatch.setattr(
        loader, "get_db_credentials",
        lambda: ("h", "5432", "u", "pw", "dbname", "myschema")
    )

    def fake_connect_fail(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(loader.psycopg2, "connect", fake_connect_fail)

    # Replace sys.exit with something that raises SystemExit
    def fake_exit(code):
        raise SystemExit(code)

    monkeypatch.setattr(loader.sys, "exit", fake_exit)

    with pytest.raises(SystemExit) as excinfo:
        loader.connect()
    assert excinfo.value.code == 1


# -----------------------------
# copy_df()
# -----------------------------

def test_copy_df(tmp_path):
    df = pd.DataFrame(
        {
            "a": [1, 2],
            "b": ["x", "y"],
        }
    )

    class FakeCursor:
        def __init__(self):
            self.calls = []

        def copy_expert(self, sql, buf):
            # read entire buffer
            buf.seek(0)
            self.calls.append((sql, buf.read()))

    cur = FakeCursor()
    loader.copy_df(cur, df, "myschema.mytable")

    assert len(cur.calls) == 1
    sql, data = cur.calls[0]
    assert "COPY myschema.mytable FROM STDIN" in sql
    # Should be plain CSV with no header
    assert data.strip().splitlines() == ["1,x", "2,y"]


# -----------------------------
# main()
# -----------------------------

def test_main_happy_path(tmp_path, monkeypatch):
    """
    End-to-end-ish test for main() with a fake connection and two CSVs:
    - aeolus_drug_outcome_lookup (normal copy_df path)
    - rxcui_to_ingredient_map    (special coerce_intlike + df_to_csv_buffer path)
    Other tables are skipped because their CSVs are missing.
    """
    out_dir = tmp_path / "datasets_output"
    out_dir.mkdir()
    monkeypatch.setattr(loader, "OUT", out_dir)

    # Create minimal CSVs
    df_aeolus = pd.DataFrame(
        {
            "rxcui": [111],
            "drug_name": ["Metformin"],
            "outcome_concept_id": [1],
            "outcome_text": ["Something"],
            "meddra_code": ["X"],
            "case_count": [10],
            "prr": [2.0],
            "ror": [3.0],
        }
    )
    df_aeolus.to_csv(out_dir / "aeolus_drug_outcome_lookup.csv", index=False)

    df_map = pd.DataFrame({"rxcui": [111.0], "ingredient_rxcui": [999.0]})
    df_map.to_csv(out_dir / "rxcui_to_ingredient_map.csv", index=False)

    # Fake connection + cursor
    class FakeCursor:
        def __init__(self):
            self.executed = []
            self.copied = []

        def execute(self, sql):
            self.executed.append(sql)

        def copy_expert(self, sql, buf):
            buf.seek(0)
            self.copied.append((sql, buf.read()))

    class FakeConn:
        def __init__(self):
            self.autocommit = False
            self.cursor_obj = FakeCursor()

        def cursor(self):
            # context manager wrapper
            conn_cursor = self.cursor_obj

            class Ctx:
                def __enter__(self_nonlocal):
                    return conn_cursor

                def __exit__(self_nonlocal, exc_type, exc, tb):
                    return False

            return Ctx()

    fake_conn = FakeConn()

    # connect() should return our fake connection and schema
    monkeypatch.setattr(loader, "connect", lambda: (fake_conn, "myschema"))

    loader.main()

    cur = fake_conn.cursor_obj
    # Schema setup
    all_sql = " ".join(cur.executed)
    assert "CREATE SCHEMA IF NOT EXISTS myschema;" in all_sql
    assert "SET search_path TO myschema;" in all_sql

    # Drop/create/truncate for at least the two tables we actually have CSV for
    assert any("DROP TABLE IF EXISTS myschema.aeolus_drug_outcome_lookup" in s for s in cur.executed)
    assert any("DROP TABLE IF EXISTS myschema.rxcui_to_ingredient_map" in s for s in cur.executed)
    assert any("TRUNCATE TABLE myschema.aeolus_drug_outcome_lookup;" in s for s in cur.executed)
    assert any("TRUNCATE TABLE myschema.rxcui_to_ingredient_map;" in s for s in cur.executed)

    # COPY calls for both tables
    copied_sql = [sql for (sql, _) in cur.copied]
    assert any("COPY myschema.rxcui_to_ingredient_map FROM STDIN" in sql for sql in copied_sql)
    assert any("COPY myschema.aeolus_drug_outcome_lookup FROM STDIN" in sql for sql in copied_sql)


def test_main_skips_missing_csvs(tmp_path, monkeypatch, capsys):
    """
    Ensure that when a CSV file is missing for some table,
    main() prints a 'Skipping' message and continues.
    We only create ONE csv and let the others be missing.
    """
    out_dir = tmp_path / "datasets_output"
    out_dir.mkdir()
    monkeypatch.setattr(loader, "OUT", out_dir)

    # Only create CSV for the first table → others should be skipped
    first_tbl, first_fname = loader.TABLES[0]
    pd.DataFrame({"dummy": [1]}).to_csv(out_dir / first_fname, index=False)

    class FakeCursor:
        def __init__(self):
            self.executed = []
            self.copied = []

        def execute(self, sql):
            self.executed.append(sql)

        def copy_expert(self, sql, buf):
            buf.seek(0)
            self.copied.append((sql, buf.read()))

    class FakeConn:
        def __init__(self):
            self.autocommit = False
            self.cursor_obj = FakeCursor()

        def cursor(self):
            c = self.cursor_obj

            class Ctx:
                def __enter__(self_self):
                    return c

                def __exit__(self_self, exc_type, exc, tb):
                    return False

            return Ctx()

    fake_conn = FakeConn()
    monkeypatch.setattr(loader, "connect", lambda: (fake_conn, "myschema"))

    loader.main()
    out = capsys.readouterr().out

    # We should see "Skipping ..." for at least one other table
    # (assuming TABLES has more than one)
    for tbl, fname in loader.TABLES[1:]:
        assert f"Skipping {tbl} (missing" in out
        break  # we just need to see at least one skip
