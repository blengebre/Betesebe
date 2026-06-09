import asyncio
from executor import full_research_pipeline

async def test():
    res = await full_research_pipeline("what is climate change", lambda phase, payload: print(f"[{phase}] {payload}"))
    print("\n\nFINAL NOTE:\n", res["note"])

asyncio.run(test())
