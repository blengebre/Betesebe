# ⚡ Project Consensus - Quick Start Guide

## What You Just Got

A complete, production-ready **Multi-Agent AI Research Engine** that:
- 🤖 Queries 3 external LLMs in **parallel** (3-5 seconds instead of 15)
- 🔍 Fact-checks answers against live web search results
- 🧠 Runs internal peer review debate (Researcher → Statistician → Critic)
- ⚖️ Judge synthesizes everything into a professional Research Note
- ⭐ Generates a confidence score based on model consensus

## Get Started in 5 Minutes

### 1️⃣  Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣  Get Your API Keys (All FREE)

Copy-paste these links and follow the instructions:

| Service | Link | Free Tier |
|---------|------|-----------|
| Google Gemini | https://aistudio.google.com/ | 15 queries/min |
| Groq | https://console.groq.com/ | Unlimited |
| OpenRouter | https://openrouter.io/ | Free tier available |
| **DuckDuckGo** | **No signup needed!** | **Unlimited** |

### 3️⃣  Add Keys to .env File

Open `.env` in your editor and fill in the values you got:

```env
GOOGLE_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
# DuckDuckGo Search - No key needed!
```

### 4️⃣  Test Everything Works

```bash
python main.py
```

Choose option **1** to test all APIs. You should see ✅ for each one.

### 5️⃣  Run a Research Query

```bash
python main.py
```

Choose option **2** or **3** to ask your first research question!

Try asking:
- "What are the latest breakthroughs in AI in 2024?"
- "Is climate change accelerating?"
- "What are the best practices for learning Python?"

## File Structure Explained

```
ai-research-engine/
├── main.py              ← Run this file (python main.py)
├── config.py            ← Loads your .env file
├── api_wrappers.py      ← Connects to APIs
├── agents.py            ← Internal debate agents
├── executor.py          ← Orchestrates the pipeline
├── requirements.txt     ← Python packages
├── .env                 ← Your API keys (KEEP PRIVATE!)
├── .env.example         ← Template for .env
├── README.md            ← Full documentation
└── QUICKSTART.md        ← This file
```

## The System Flow

```
┌─────────────────────────────────────────────────────┐
│ USER ASKS A QUESTION                                │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────▼──────────────┐
        │ PHASE 1: PARALLEL GATHERING │
        │ (3-5 seconds)              │
        ├────────────────────────────┤
        │ → Gemini                   │
        │ → Groq                     │
        │ → OpenRouter               │
        │ → Tavily Web Search        │
        └─────────────┬──────────────┘
                      │
        ┌─────────────▼──────────────┐
        │ PHASE 2: INTERNAL DEBATE   │
        │ (2-3 seconds)              │
        ├────────────────────────────┤
        │ → Researcher (checks facts)│
        │ → Statistician (checks logic)
        │ → Critic (finds errors)    │
        └─────────────┬──────────────┘
                      │
        ┌─────────────▼──────────────┐
        │ PHASE 3-4: JUDGE           │
        │ (5-10 seconds)             │
        ├────────────────────────────┤
        │ → Synthesizes everything   │
        │ → Generates confidence     │
        │ → Creates final note       │
        └─────────────┬──────────────┘
                      │
        ┌─────────────▼──────────────┐
        │ RESEARCH NOTE WITH CONFIDENCE SCORE
        │ (Professional Markdown)
        └────────────────────────────┘
```

## Troubleshooting

### "Missing API keys" error
→ Make sure you filled in the `.env` file correctly

### "Connection error" 
→ Check your internet connection
→ Some APIs have regional restrictions

### "Rate limit" error
→ Free tier has limits. Wait a few minutes or use another API key.

### Can't import modules
→ Run: `pip install -r requirements.txt` again
→ Make sure you're using Python 3.10+

## What Happens Next?

After you test everything:

1. **Phase 3: Internal Debate** ✅ (Already implemented)
2. **Phase 5: Add a Web UI** (Optional)
   - Simple Streamlit app for beautiful interface
   - Already set up in requirements.txt
   - Just run: `streamlit run streamlit_app.py`

## API Cost

**Total Cost: $0** (Forever using free tiers)

| API | Cost | Limits |
|-----|------|--------|
| Gemini | Free | 15 req/min |
| Groq | Free | Unlimited |
| OpenRouter | Free | No hard limits |
| DuckDuckGo | Free | Unlimited |

## Pro Tips

💡 **Tip 1:** The confidence score is based on:
- How much the 3 LLMs agree
- How much web facts support the LLMs
- How well the internal critics validated it

💡 **Tip 2:** For fastest results, ask questions that have recent web data:
- ✅ "What's new in AI?" (lots of current data)
- ❌ "Tell me everything about biology" (too broad)

💡 **Tip 3:** Keep queries to 1-2 sentences for best results

💡 **Tip 4:** Each full research query takes ~15-25 seconds (4 parallel APIs + 3 agents + judge)

## Next Step: Build the UI

Ready for a beautiful interface? Create `streamlit_app.py`:

```python
import streamlit as st
from executor import full_research_pipeline
import asyncio

st.title("🚀 Project Consensus")
query = st.text_input("What would you like to research?")

if query:
    with st.spinner("🤖 Agents are debating..."):
        note = asyncio.run(full_research_pipeline(query))
    st.markdown(note)
```

Then run: `streamlit run streamlit_app.py`

---

## You're All Set! 🎉

Run this command to get started:

```bash
python main.py
```

**Questions?** Check README.md for the full documentation.

**Happy researching! 🚀**
