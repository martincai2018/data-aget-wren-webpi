"""完整案例的语义层验证：视图、计算字段、指标清单"""
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def call(session, name, args=None):
    r = await session.call_tool(name, args or {})
    return r.content[0].text


async def main():
    async with streamablehttp_client("http://localhost:9000/mcp") as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            checks = [
                ("视图 CustomerOrderSummary",
                 "query", {"sql": "SELECT * FROM CustomerOrderSummary ORDER BY gmv DESC LIMIT 3"}),
                ("视图 MonthlyGmv",
                 "query", {"sql": "SELECT * FROM MonthlyGmv LIMIT 3"}),
                ("计算字段 is_completed",
                 "query", {"sql": "SELECT DISTINCT orderstatus, is_completed FROM Orders ORDER BY 1"}),
            ]
            for title, tool, args in checks:
                print(f"\n=== {title} ===")
                print(await call(s, tool, args))
            print("\n=== 当前 MDL 语义对象 ===")
            import json
            m = json.loads(await call(s, "get_manifest"))
            print("models:", [x["name"] for x in m["models"]])
            print("views:", [x["name"] for x in m.get("views", [])])
            print("metrics:", [x["name"] for x in m.get("metrics", [])])
            print("enums:", [x["name"] for x in m.get("enumDefinitions", [])])
            print("relationships:", [x["name"] for x in m.get("relationships", [])])


asyncio.run(main())
