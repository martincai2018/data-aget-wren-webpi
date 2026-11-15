"""从上游 TPC-H parquet 示例数据生成演示用 DuckDB（tpch.duckdb）。

用法（在 mcp-server 目录下；duckdb 作为临时依赖注入，不进项目依赖清单）：
    uv run --with duckdb python demo-data/build_demo_duckdb.py

生成的 tpch.duckdb 不入库（见 .gitignore），需要时随时重新生成。
"""
from pathlib import Path

import duckdb

HERE = Path(__file__).resolve().parent
PARQUET_DIR = HERE.parent.parent / "example" / "duckdb-tpch-example" / "data"
DB_PATH = HERE / "tpch.duckdb"
TABLES = ["orders", "customer", "lineitem", "nation", "part"]


def main() -> None:
    if not PARQUET_DIR.exists():
        raise SystemExit(f"parquet 示例目录不存在: {PARQUET_DIR}")
    con = duckdb.connect(str(DB_PATH))
    for table in TABLES:
        parquet = PARQUET_DIR / f"{table}.parquet"
        con.execute(
            f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_parquet(?)",
            [str(parquet)],
        )
    rows = con.execute("SHOW TABLES").fetchall()
    print("tables:", [r[0] for r in rows])
    print("orders:", con.execute("SELECT COUNT(*) FROM orders").fetchone()[0])
    print("written to:", DB_PATH)


if __name__ == "__main__":
    main()
