"""
SQLite 세션 DB(ai-memory.db) 내용을 읽기 쉬운 텍스트로 출력하는 스크립트.
실행: python view_db.py
"""
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "ai-memory.db"


def view_db(path: Path = DB_PATH) -> None:
    if not path.exists():
        print(f"DB 파일이 없습니다: {path}")
        return

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row  # 컬럼 이름으로 접근
    cur = conn.cursor()

    # 테이블 목록
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row[0] for row in cur.fetchall()]
    print(f"=== DB: {path.name} ===\n")
    print(f"테이블: {tables}\n")

    for table in tables:
        print(f"--- 테이블: {table} ---")
        cur.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cur.fetchall()]
        print(f"컬럼: {columns}")

        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()
        if not rows:
            print("  (데이터 없음)\n")
            continue
        for i, row in enumerate(rows, 1):
            print(f"  [{i}]")
            for col in columns:
                val = row[col] if isinstance(row, sqlite3.Row) else row[columns.index(col)]
                # 너무 긴 값은 잘라서 표시
                s = str(val)
                if len(s) > 200:
                    s = s[:200] + "..."
                print(f"      {col}: {s}")
            print()
        print()

    conn.close()
    print("(끝)")


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DB_PATH
    view_db(path)
