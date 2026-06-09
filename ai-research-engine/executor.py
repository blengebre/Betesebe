"""
Parallel Execution Module
Implements efficient concurrent API calls for Phase 1 (Parallel Data Gathering)
"""
import asyncio
from typing import Dict, List
from api_wrappers import gemini, groq, openrouter, tavily


async def parallel_external_queries(prompt: str) -> Dict[str, str]:
    """
    Phase 1: Query all 3 external LLMs in parallel
    Instead of 15 seconds (sequential), this takes ~3-5 seconds
    """
    print("⚡ Querying 3 external AI models in parallel...")
    
    try:
        results = await asyncio.gather(
            gemini.query(prompt),
            groq.query(prompt),
            openrouter.query(prompt),
            return_exceptions=True
        )
        
        return {
            "Gemini (1.5-Flash)": results[0] if not isinstance(results[0], Exception) else f"Error: {results[0]}",
            "Groq (Llama-3.1-70B)": results[1] if not isinstance(results[1], Exception) else f"Error: {results[1]}",
            "OpenRouter (Llama-3.1-8B)": results[2] if not isinstance(results[2], Exception) else f"Error: {results[2]}"
        }
    except Exception as e:
        print(f"Error in parallel queries: {e}")
        return {}


async def parallel_data_gathering(user_prompt: str) -> Dict:
    """
    Phase 1 Complete: Gather all external data in parallel
    Executes LLM queries AND web search simultaneously
    """
    print("\n" + "="*70)
    print("PHASE 1: PARALLEL DATA GATHERING")
    print("="*70)
    
    # Run external LLM queries and web search in parallel
    lm_responses, search_results = await asyncio.gather(
        parallel_external_queries(user_prompt),
        tavily.search(user_prompt, max_results=5)
    )
    
    print(f"\n✅ Phase 1 Complete!")
    print(f"   - Got responses from 3 LLMs")
    print(f"   - Got {len(search_results)} web search results")
    
    return {
        "user_prompt": user_prompt,
        "external_models": lm_responses,
        "web_search_results": search_results
    }


async def run_internal_debate(phase1_data: Dict) -> Dict:
    """
    Phase 2: Internal Peer Review Debate
    Researcher -> Statistician -> Critic sequentially
    """
    from agents import researcher, statistician, critic
    
    print("\n" + "="*70)
    print("PHASE 2: INTERNAL PEER REVIEW DEBATE")
    print("="*70)
    
    # Researcher analyzes web search results
    print("\n📊 Researcher Agent analyzing web facts...")
    researcher_analysis = await researcher.analyze(phase1_data["web_search_results"])
    
    # Statistician checks external model responses
    print("📈 Statistician Agent checking for logical errors...")
    statistician_analysis = await statistician.analyze(phase1_data["external_models"])
    
    # Critic compares everything
    print("🔍 Critic Agent identifying hallucinations...")
    critic_analysis = await critic.analyze(
        phase1_data["external_models"],
        researcher_analysis
    )
    
    print("\n✅ Phase 2 Complete!")
    
    return {
        "researcher_analysis": researcher_analysis,
        "statistician_analysis": statistician_analysis,
        "critic_analysis": critic_analysis
    }


async def judge_and_synthesize(phase1_data: Dict, phase2_debate: Dict) -> str:
    """
    Phase 3 & 4: Judge synthesizes everything into final Research Note
    """
    from agents import judge
    
    print("\n" + "="*70)
    print("PHASE 3 & 4: JUDGMENT & FINAL SYNTHESIS")
    print("="*70)
    
    print("\n⚖️  Judge Agent synthesizing final Research Note...")
    
    research_note = await judge.generate_research_note(
        user_prompt=phase1_data["user_prompt"],
        model_responses=phase1_data["external_models"],
        verified_facts=phase2_debate["researcher_analysis"],
        researcher_analysis=phase2_debate["researcher_analysis"],
        statistician_analysis=phase2_debate["statistician_analysis"],
        critic_analysis=phase2_debate["critic_analysis"]
    )
    
    print("\n✅ Phase 3 & 4 Complete!")
    
    return research_note


async def full_research_pipeline(user_prompt: str) -> str:
    """
    Execute the complete Project Consensus pipeline:
    Phase 1: Parallel Data Gathering (3-5 seconds)
    Phase 2: Internal Debate (2-3 seconds)
    Phase 3: Judge & Synthesize (5-10 seconds)
    Phase 4: Output Final Research Note
    """
    print("\n" + "="*70)
    print("🚀 PROJECT CONSENSUS - MULTI-AGENT RESEARCH ENGINE")
    print("="*70)
    
    # Phase 1
    phase1_data = await parallel_data_gathering(user_prompt)
    
    # Phase 2
    phase2_debate = await run_internal_debate(phase1_data)
    
    # Phase 3 & 4
    research_note = await judge_and_synthesize(phase1_data, phase2_debate)
    
    return research_note
