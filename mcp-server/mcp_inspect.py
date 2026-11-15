"""检查 Wren MCP 暴露给 agent 的语义/知识能力：工具描述 + 关键工具返回内容"""
import asyncio
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    async with streamablehttp_client("http://localhost:9000/mcp") as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = (await s.list_tools()).tools
            print("=== 工具及说明 ===")
            for t in tools:
                desc = (t.description or "").strip().splitlines()[0][:90]
                print(f"- {t.name}: {desc}")

            for name in ["get_manifest", "get_relationships", "get_wren_guide",
                         "get_current_data_source_type", "is_deployed"]:
                print(f"\n=== {name} ===")
                try:
                    res = await s.call_tool(name, {})
                    txt = res.content[0].text
                    print(txt[:900] + ("..." if len(txt) > 900 else ""))
                except Exception as e:
                    print("error:", e)


asyncio.run(main())
