"""
Internal Debate Agents for Project Consensus
Implements the Researcher, Statistician, Critic, and Judge agents
"""
import asyncio
from typing import List, Dict
from api_wrappers import groq, gemini


class ResearcherAgent:
    """
    Lead Researcher Agent - Extracts verified facts from web search results
    """
    
    system_prompt = """You are the Lead Researcher. You have been provided with live web search results. 
Your job is to extract the core, verified facts from these search results and summarize them. 
Ignore opinions; focus only on data, dates, and verifiable claims. 
Output a concise bulleted list of facts. Keep response under 200 words."""
    
    async def analyze(self, search_results: List[Dict]) -> str:
        """Analyze web search results and extract facts"""
        if not search_results:
            return "No search results available."
        
        results_text = "\n".join([
            f"- {r.get('title', '')}: {r.get('content', '')}"
            for r in search_results if r.get('title') or r.get('content')
        ])
        
        prompt = f"""Please analyze these search results and extract verified facts:

{results_text}

Provide only factual information, dates, and verifiable claims."""
        
        response = await groq.query(prompt, self.system_prompt)
        return response


class StatisticianAgent:
    """
    Lead Statistician Agent - Checks for logical/mathematical errors in LLM responses
    """
    
    system_prompt = """You are the Lead Statistician and Logic Checker. 
You have been provided with answers from three external AI models. 
Your job is to scan their answers for logical fallacies, mathematical errors, or contradictory statements. 
Point out exactly which model made which error. If the data looks solid, state that. 
Keep response under 200 words."""
    
    async def analyze(self, model_responses: Dict[str, str]) -> str:
        """Analyze responses from external models for logical errors"""
        responses_text = "\n".join([
            f"{model}: {response[:500]}"
            for model, response in model_responses.items()
        ])
        
        prompt = f"""Please analyze these responses for logical errors, contradictions, or mathematical mistakes:

{responses_text}

Identify which model (if any) has errors and explain them."""
        
        response = await groq.query(prompt, self.system_prompt)
        return response


class CriticAgent:
    """
    Lead Peer-Review Critic - Identifies hallucinations and compares against facts
    """
    
    system_prompt = """You are the Lead Peer-Review Critic. You are highly skeptical. 
Compare the external AI answers against the verified facts provided by the Researcher. 
Identify any hallucinations, outdated information, or biases. 
Explicitly state which AI model provided the most accurate answer and which provided the worst. 
Keep response under 200 words."""
    
    async def analyze(self, model_responses: Dict[str, str], verified_facts: str) -> str:
        """Critique external model responses against verified facts"""
        responses_text = "\n".join([
            f"{model}: {response[:400]}"
            for model, response in model_responses.items()
        ])
        
        prompt = f"""Compare these model responses against the verified facts and identify issues:

Model Responses:
{responses_text}

Verified Facts:
{verified_facts}

Identify hallucinations, inaccuracies, and which model is most reliable."""
        
        response = await groq.query(prompt, self.system_prompt)
        return response


class JudgeAgent:
    """
    Chief Scientific Officer / Judge Agent - Synthesizes everything into final Research Note
    """
    
    system_prompt = """You are the Chief Scientific Officer. 
You have reviewed the user's prompt, answers from 3 external AIs, live web search facts, 
and a debate transcript from internal peer-review agents (Researcher, Statistician, Critic).

Generate a final 'Research Note' for the user in the following Markdown format:

# 📄 RESEARCH NOTE: [Topic Name]

### 1. Executive Summary
[3-4 sentences summarizing the final, synthesized truth.]

### 2. Confidence Assessment
Confidence Score: [X]/100
Justification: [Explain exactly why you gave this score based on model consensus, fact-checking, and the debate.]

### 3. Comprehensive Analysis
[Break the topic down into 2-3 detailed sub-sections. Synthesize the best data from the models and the web search.]

### 4. Points of Contention & Resolutions
[Highlight where the external models disagreed. Explain how the internal agents resolved it.]

### 5. Limitations & Blind Spots
[State what is still unknown, unverified, or where the web search lacked data.]

Write in a highly professional, objective, and detailed tone."""
    
    async def generate_research_note(
        self,
        user_prompt: str,
        model_responses: Dict[str, str],
        verified_facts: str,
        researcher_analysis: str,
        statistician_analysis: str,
        critic_analysis: str
    ) -> str:
        """Generate final Research Note with all information"""
        
        full_context = f"""
User Query: {user_prompt}

External Model Responses:
{chr(10).join([f"- {model}: {resp[:300]}" for model, resp in model_responses.items()])}

Verified Web Search Facts:
{verified_facts}

Internal Debate Transcripts:
- Researcher: {researcher_analysis[:300]}
- Statistician: {statistician_analysis[:300]}
- Critic: {critic_analysis[:300]}
"""
        
        response = await gemini.query(full_context)
        return response


# Initialize agents
researcher = ResearcherAgent()
statistician = StatisticianAgent()
critic = CriticAgent()
judge = JudgeAgent()
