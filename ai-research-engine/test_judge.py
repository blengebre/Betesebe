import asyncio
from agents import judge

async def test():
    # Provide a very long dossier string
    dossier = "This is a fact about climate change. " * 500
    res = await judge.generate_research_note(
        "what is climate change",
        dossier,
        "Gemini analysis goes here",
        "Groq analysis goes here",
        "OpenRouter analysis goes here"
    )
    print("Result:")
    print(res)

asyncio.run(test())
