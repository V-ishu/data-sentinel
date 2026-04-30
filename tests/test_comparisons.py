import sqlite3
import pytest

@pytest.fixture
def demo_dbs(tmp_path):
    """Create two demo SQLite databases with intentional differences."""
    src = tmp_path / "src.sqlite"
    tgt = tmp_path / "tgt.sqlite"

    source_rows = [
        (1, "Alice", 90000),
        (2, "Bob", 80000),
        (3, "Charlie", 70000),
    ]
    target_rows = [
        (1, "Alice", 90000),  # same
        (2, "Bob", 85000),    # different salary
        (4, "Dan", 65000),  # new row
    ]

    for path, rows in [(src, source_rows), (tgt, target_rows)]:
        conn = sqlite3.connect(path)
        conn.execute(
            "CREATE TABLE employees ("
            "id INTEGER PRIMARY KEY, name TEXT, salary INTEGER)"
        )
        conn.executemany("INSERT INTO employees VALUES (?, ?, ?)", rows)
        conn.commit()
        conn.close()
    
    return f"sqlite:///{src}", f"sqlite:///{tgt}"


def test_create_comparison_returns_202(client, demo_dbs):
    src, tgt = demo_dbs
    response = client.post(
        "/api/v1/comparisons",
        json={"source_db": src, "target_db": tgt, "table": "employees"},
    )
    assert response.status_code == 202
    body = response.json()
    assert "job_id" in body
    assert body["status"] == "queued"


def test_get_nonexistent_job_returns_404(client):
    response = client.get("/api/v1/comparisons/does-not-exist")
    assert response.status_code == 404
    
def test_list_comparisons_initially_empty(client):
    response = client.get("/api/v1/comparisons")
    assert response.status_code == 200
    assert response.json() == []

def test_full_job_lifecycle(client, demo_dbs):
    src, tgt = demo_dbs
    # Create job
    create_resp = client.post(
        "/api/v1/comparisons",
        json={"source_db": src, "target_db": tgt, "table": "employees"},
    )
    assert create_resp.status_code == 202
    job_id = create_resp.json()["job_id"]

    get_resp = client.get(f"/api/v1/comparisons/{job_id}")
    assert get_resp.status_code == 200
    job = get_resp.json()
    assert job["status"] == "completed"
    assert job["result"] is not None

    summary = job["result"]["summary"]
    assert summary["total_issues"] == 3
    assert summary["mismatched_rows_count"] == 1
    assert summary["missing_in_target_count"] == 1
    assert summary["missing_in_source_count"] == 1

    list_resp = client.get("/api/v1/comparisons")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    del_resp = client.delete(f"/api/v1/comparisons/{job_id}")
    assert del_resp.status_code == 204

    after_delete = client.get(f"/api/v1/comparisons/{job_id}")
    assert after_delete.status_code == 404