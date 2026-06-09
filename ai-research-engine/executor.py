"""
Iterative Deep Search Executor
Implements the multi-stage research pipeline:
1. Deep Search (Broad search -> sub-questions -> targeted searches -> massive dossier)
2. Multi-Model Expert Analysis
3. Judge Synthesis (Deep Research Paper)
"""
import asyncio
import time
from typing import Dict, List, Callable, Optional, Any
from api_wrappers import gemini, groq, openrouter, tavily


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def format_search_results(results_list: List[Dict], source_name: str) -> str:
    """Format search results into a readable dossier chunk"""
    if not results_list:
        return f"--- Results for: {source_name} ---\nNo results found.\n"
        
    out = [f"--- Results for: {source_name} ---"]
    for i, r in enumerate(results_list, 1):
        out.append(f"{i}. {r.get('title', 'Unknown Title')}")
        out.append(f"   URL: {r.get('link', 'No URL')}")
        out.append(f"   Content: {r.get('content', '')}\n")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Phase 1 — Iterative Deep Search
# ---------------------------------------------------------------------------

async def deep_search(user_prompt: str, emit: Callable) -> Dict:
    """
    Phase 1: Iterative Deep Search
    1. Broad search
    2. Sub-question generation
    3. Targeted deep searches
    """
    from agents import researcher
    
    t0 = time.perf_counter()

    emit("phase", {"phase": 1, "status": "running", "label": "Broad Initial Search..."})
    print("\n[Deep Search] Performing initial broad search...")
    initial_results = await tavily.search(user_prompt, max_results=5)
    
    dossier_chunks = [format_search_results(initial_results, "Broad Initial Search")]
    all_results = list(initial_results)
    
    emit("phase", {"phase": 1, "status": "running", "label": "Generating Sub-Questions..."})
    print("[Deep Search] Researcher Agent generating sub-questions...")
    sub_questions = await researcher.generate_sub_questions(user_prompt, initial_results)
    print(f"   Generated {len(sub_questions)} questions: {sub_questions}")
    
    emit("phase", {"phase": 1, "status": "running", "label": f"Deep Searching {len(sub_questions)} Sub-Questions..."})
    
    # Run deep searches concurrently
    print("[Deep Search] Running deep searches concurrently...")
    deep_search_tasks = [tavily.search(q, max_results=5) for q in sub_questions]
    deep_results = await asyncio.gather(*deep_search_tasks, return_exceptions=True)
    
    for q, results in zip(sub_questions, deep_results):
        if not isinstance(results, Exception) and results:
            dossier_chunks.append(format_search_results(results, q))
            all_results.extend(results)
            
    massive_dossier = "\n\n".join(dossier_chunks)
    elapsed = round(time.perf_counter() - t0, 2)
    print(f"✅ Deep Search Complete! ({elapsed}s, {len(all_results)} total sources)")
    
    return {
        "massive_dossier": massive_dossier,
        "phase1_time": elapsed,
        "source_count": len(all_results)
    }

# ---------------------------------------------------------------------------
# Phase 2 — Multi-Model Expert Analysis
# ---------------------------------------------------------------------------

async def multi_model_analysis(user_prompt: str, massive_dossier: str) -> Dict:
    """
    Phase 2: External APIs analyze the massive dossier.
    """
    t0 = time.perf_counter()
    print("\n[Expert Analysis] 3 Models analyzing massive dossier...")
    
    system_prompt = """You are an Expert Analyst. I am providing you with a comprehensive dossier of verified facts, data points, and context gathered from multiple deep web searches.

Instructions:
Analyze this data deeply and provide a detailed, academic-style breakdown of the topic. 
- Synthesize the findings.
- Highlight any contradictions, varying estimates, or competing viewpoints found in the data.
- Rely ONLY on the provided dossier. Do not hallucinate outside information."""

    prompt = f"""**Core Topic:** "{user_prompt}"

**Deep Search Dossier (Facts & Data):**
{massive_dossier}"""

    results = await asyncio.gather(
        gemini.query(prompt, system_prompt=system_prompt),
        groq.query(prompt, system_prompt=system_prompt),
        openrouter.query(prompt, system_prompt=system_prompt),
        return_exceptions=True
    )
    
    elapsed = round(time.perf_counter() - t0, 2)
    print(f"✅ Expert Analysis Complete! ({elapsed}s)")
    
    return {
        "gemini": results[0] if not isinstance(results[0], Exception) else f"Error: {results[0]}",
        "groq": results[1] if not isinstance(results[1], Exception) else f"Error: {results[1]}",
        "openrouter": results[2] if not isinstance(results[2], Exception) else f"Error: {results[2]}",
        "phase2_time": elapsed
    }

# ---------------------------------------------------------------------------
# Phase 3 & 4 — Judge Synthesis
# ---------------------------------------------------------------------------

async def judge_and_synthesize(user_prompt: str, massive_dossier: str, phase2_data: Dict) -> Dict:
    """
    Phase 3: Judge synthesizes everything into the final Research Paper.
    """
    from agents import judge
    t0 = time.perf_counter()
    print("\n[Judge Synthesis] Writing final Research Paper...")
    
    research_note = await judge.generate_research_note(
        user_prompt=user_prompt,
        massive_dossier=massive_dossier,
        gemini_analysis=phase2_data["gemini"],
        groq_analysis=phase2_data["groq"],
        openrouter_analysis=phase2_data["openrouter"]
    )
    
    elapsed = round(time.perf_counter() - t0, 2)
    print(f"✅ Judge Synthesis Complete! ({elapsed}s)")
    
    return {
        "note": research_note,
        "phase3_time": elapsed
    }

# ---------------------------------------------------------------------------
# Full Pipeline
# ---------------------------------------------------------------------------

async def full_research_pipeline(
    user_prompt: str,
    event_callback: Optional[Callable[[str, Any], None]] = None,
) -> Dict:
    """
    Execute the complete Deep Research pipeline.
    """
    print("\n" + "=" * 70)
    print("🚀 DEEP RESEARCH ENGINE - ITERATIVE DEEP SEARCH")
    print("=" * 70)

    total_t0 = time.perf_counter()

    def emit(phase: str, payload: Any):
        if event_callback:
            try:
                event_callback(phase, payload)
            except Exception:
                pass 

    # ---- Phase 1 ----
    emit("phase", {"phase": 1, "status": "running", "label": "Iterative Deep Web Search"})
    phase1_data = await deep_search(user_prompt, emit)
    emit("phase", {
        "phase": 1, "status": "done",
        "label": f"Deep Search Complete ({phase1_data['source_count']} Sources)",
        "time_s": phase1_data["phase1_time"],
    })

    # ---- Phase 2 ----
    emit("phase", {"phase": 2, "status": "running", "label": "Multi-Model Expert Analysis"})
    phase2_data = await multi_model_analysis(user_prompt, phase1_data["massive_dossier"])
    emit("phase", {
        "phase": 2, "status": "done",
        "label": "Expert Analysis Complete",
        "time_s": phase2_data["phase2_time"],
    })

    # ---- Phase 3 ----
    emit("phase", {"phase": 3, "status": "running", "label": "Lead Researcher Synthesis"})
    phase3_result = await judge_and_synthesize(user_prompt, phase1_data["massive_dossier"], phase2_data)
    emit("phase", {
        "phase": 3, "status": "done",
        "label": "Research Paper Complete",
        "time_s": phase3_result["phase3_time"],
    })

    # ---- Phase 4 ----
    total_elapsed = round(time.perf_counter() - total_t0, 2)

    result = {
        "note": phase3_result["note"],
        "confidence_score": 100,  # We've removed confidence scoring as this is a full paper now
        "timings": {
            "phase1": phase1_data["phase1_time"],
            "phase2": phase2_data["phase2_time"],
            "phase3": phase3_result["phase3_time"],
            "total":  total_elapsed,
        },
        "models": {
            "external": ["Gemini 2.5-Flash", "Groq Llama-3.3-70B", "OpenRouter Llama-3.1-8B"],
            "judge": "Gemini 2.5-Flash",
        },
    }

    emit("result", result)
    emit("done", {})

    return result
