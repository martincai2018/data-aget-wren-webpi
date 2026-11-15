"""端到端验证：通过运行中的 ibis-server 查询本地 Parquet（local_file 连接器）"""
import base64
import json
import urllib.request

DATA_DIR = "C:/AI/wren-engine/example/duckdb-tpch-example/data"

manifest = {
    "catalog": "demo",
    "schema": "tpch",
    "models": [
        {
            "name": "Orders",
            "tableReference": {"table": f"{DATA_DIR}/orders.parquet"},
            "columns": [
                {"name": "orderkey", "expression": "o_orderkey", "type": "integer"},
                {"name": "custkey", "expression": "o_custkey", "type": "integer"},
                {"name": "orderstatus", "expression": "o_orderstatus", "type": "varchar"},
                {"name": "totalprice", "expression": "o_totalprice", "type": "float"},
                {"name": "orderdate", "expression": "o_orderdate", "type": "date"},
            ],
            "primaryKey": "orderkey",
        }
    ],
}

payload = {
    "manifestStr": base64.b64encode(json.dumps(manifest).encode()).decode(),
    "sql": 'SELECT orderstatus, COUNT(*) AS cnt, ROUND(SUM(totalprice),2) AS gmv '
           'FROM "Orders" GROUP BY orderstatus ORDER BY orderstatus',
    "connectionInfo": {"url": DATA_DIR, "format": "parquet"},
}

req = urllib.request.Request(
    "http://localhost:8000/v3/connector/local_file/query",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(req, timeout=60) as resp:
    result = json.loads(resp.read())

print("HTTP OK")
print("columns:", result["columns"])
print("dtypes :", result["dtypes"])
for row in result["data"]:
    print("  row:", row)
