"""向运行中的 Wren MCP Web UI(9001) 写入 DuckDB 连接并部署演示 MDL"""
import json
import urllib.parse
import urllib.request

BASE = "http://localhost:9001"
DEMO_DIR = "C:/AI/wren-engine/mcp-server/demo-data"

# 1. 保存连接（表单编码，和浏览器 UI 提交一致）
form = {"datasource": "DUCKDB", "url": DEMO_DIR, "format": "duckdb"}
data = urllib.parse.urlencode(form).encode()
req = urllib.request.Request(f"{BASE}/connection", data=data)
print("connection ->", urllib.request.urlopen(req, timeout=30).status)

# 2. 部署 MDL（tpch.duckdb -> catalog=tpch, schema=main）
mdl = {
    "catalog": "wren",
    "schema": "tpch",
    "dataSource": "duckdb",
    "models": [
        {
            "name": "Orders",
            "tableReference": {"catalog": "tpch", "schema": "main", "table": "orders"},
            "columns": [
                {"name": "orderkey", "expression": "o_orderkey", "type": "integer"},
                {"name": "custkey", "expression": "o_custkey", "type": "integer"},
                {"name": "orderstatus", "expression": "o_orderstatus", "type": "varchar"},
                {"name": "totalprice", "expression": "o_totalprice", "type": "double"},
                {"name": "orderdate", "expression": "o_orderdate", "type": "date"},
            ],
            "primaryKey": "orderkey",
        },
        {
            "name": "Customer",
            "tableReference": {"catalog": "tpch", "schema": "main", "table": "customer"},
            "columns": [
                {"name": "custkey", "expression": "c_custkey", "type": "integer"},
                {"name": "name", "expression": "c_name", "type": "varchar"},
                {"name": "marketsegment", "expression": "c_mktsegment", "type": "varchar"},
            ],
            "primaryKey": "custkey",
        },
    ],
    "relationships": [
        {
            "name": "CustomerOrders",
            "models": ["Customer", "Orders"],
            "joinType": "ONE_TO_MANY",
            "condition": '"Customer".custkey = "Orders".custkey',
        }
    ],
}
req = urllib.request.Request(
    f"{BASE}/mdl", data=json.dumps(mdl).encode(),
    headers={"Content-Type": "application/json"},
)
print("mdl deploy ->", urllib.request.urlopen(req, timeout=30).status)
print("done")
