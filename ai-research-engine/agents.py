"""
Iterative Deep Search Agents
Implements the Researcher (Sub-Question Generator) and Judge (Paper Synthesizer)
"""
import re
from typing import List, Dict
from api_wrappers import groq, gemini


class ResearcherAgent:
    """
    Lead Researcher Agent - Deconstructs a complex topic into sub-questions.
    """

    system_prompt = """You are the Lead Academic Researcher for an elite intelligence and research agency.
Your goal is to deconstruct a complex topic into highly specific, academic sub-questions that must be answered to write a comprehensive research paper."""

    async def generate_sub_questions(self, user_query: str, initial_search_results: List[Dict]) -> List[str]:
        """Generate specific sub-questions based on initial broad search results."""
        if not initial_search_results:
            initial_search_results = [{"title": "No data", "content": "Initial search yielded no results."}]

        results_text = "\n".join([
            f"- {r.get('title', '')}: {r.get('content', '')}"
            for r in initial_search_results if r.get('title') or r.get('content')
        ])

        prompt = f"""**User's Core Topic:** "{user_query}"

**Initial Broad Search Results:**
{results_text}

**Instructions:**
Based on the initial search results and the core topic, break down the user's main question into exactly 3 to 4 highly specific, academic sub-questions. These sub-questions should target the missing details, underlying mechanics, and complex nuances of the topic.

Do NOT answer the questions. Only output the 3-4 questions. Format your output as a simple numbered list."""

        response = await groq.query(prompt, self.system_prompt)
        
        # Parse the numbered list
        questions = []
        for line in response.split('\n'):
            line = line.strip()
            # Match lines starting with a number and a dot/parenthesis
            match = re.match(r'^\d+[\.\)]\s*(.*)', line)
            if match:
                q = match.group(1).strip()
                # strip asterisks just in case
                q = q.replace("**", "").replace("*", "")
                if q:
                    questions.append(q)
        
        # Fallback if regex parsing fails
        if not questions:
            questions = [q.strip().replace("**", "") for q in response.split('\n') if q.strip() and len(q) > 10][:4]
            
        return questions


class JudgeAgent:
    """
    Chief Scientific Officer / Judge Agent - Synthesizes everything into a comprehensive Research Paper
    Uses gemini-2.0-flash with a dedicated system_prompt for richer, structured output.
    """

    system_prompt = """You are the Chief Scientific Officer and Lead Author. You will receive a comprehensive set of verified web data along with deep analytical breakdowns from three Expert AI Analysts. 

Act as a Lead Academic Researcher. Using ONLY the provided debate transcripts and verified web data, write a comprehensive, multi-section Research Paper. 

You MUST format the Research Paper EXACTLY with these sections (use Markdown headers):

# 📄 DEEP RESEARCH PAPER: [Insert Topic Name]

### 1. Abstract
[Provide a high-level summary of the entire paper's findings in 1-2 paragraphs.]

### 2. Introduction & Context
[Explain the background, why this topic matters, and the current landscape.]

### 3. Methodology & Data Landscape
[Briefly summarize the breadth of data gathered and identify any limitations in the available web data.]

### 4. Deep Analysis
[This is the core of the paper. Break this down into 3+ subheadings based on the sub-questions researched. Synthesize the facts, dates, and statistics.]

### 5. Points of Contention & AI Debate
[Detail where the 3 Expert AI Analysts disagreed in their interpretations of the data, or where the data itself is contradictory.]

### 6. Conclusion
[Deliver a final, synthesized verdict on the topic.]

### 7. References
[Provide a formatted, bulleted list of URLs and sources used in the research.]"""

    async def generate_research_note(
        self,
        user_prompt: str,
        massive_dossier: str,
        gemini_analysis: str,
        groq_analysis: str,
        openrouter_analysis: str
    ) -> str:
        """Generate final Research Paper using the deep search dossier and 3 expert analyses"""

        full_context = f"""**Core Topic:** "{user_prompt}"

**Verified Web Data (The Deep Search Dossier):**
{massive_dossier}

**Expert Analyst 1 (Gemini):**
{gemini_analysis}

**Expert Analyst 2 (Groq):**
{groq_analysis}

**Expert Analyst 3 (OpenRouter):**
{openrouter_analysis}

Now, write the final Deep Research Paper."""

        response = await gemini.query(
            full_context,
            system_prompt=self.system_prompt,
            use_judge_model=True
        )
        return response


# Initialize agents
researcher = ResearcherAgent()
judge = JudgeAgent()
