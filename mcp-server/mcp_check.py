"""MCP 客户端验证：连接 streamable-http MCP，列出工具并执行一次 Wren 查询"""
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    async with streamablehttp_client("http://localhost:9000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("=== MCP tools ===")
            for t in tools.tools:
                print(" -", t.name)

            # 调用 Wren 查询工具（不同版本工具名可能是 query / wren_query）
            names = {t.name for t in tools.tools}
            query_tool = "query" if "query" in names else next(
                (n for n in names if "query" in n.lower()), None)
            print("\nusing tool:", query_tool)
            schema = next(t for t in tools.tools if t.name == query_tool)
            print("args schema:", schema.inputSchema.get("properties", {}).keys())

            result = await session.call_tool(query_tool, {
                "sql": 'SELECT orderstatus, COUNT(*) AS cnt FROM "Orders" '
                       'GROUP BY orderstatus ORDER BY orderstatus'
            })
            print("\n=== query result ===")
            for c in result.content:
                print(getattr(c, "text", c))


asyncio.run(main())
