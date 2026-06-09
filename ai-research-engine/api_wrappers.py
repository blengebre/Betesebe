"""
API Wrappers for all external services
"""
import httpx
import asyncio
from typing import Optional
from config import GOOGLE_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY
from duckduckgo_search import DDGS


class GoogleGeminiAPI:
    """Wrapper for Google Gemini API (External Model 1 & Judge)"""

    def __init__(self):
        self.api_key = GOOGLE_API_KEY
        self.model = "gemini-2.5-flash"
        self.judge_model = "gemini-2.5-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def query(self, prompt: str, system_prompt: str = None, use_judge_model: bool = False) -> str:
        """
        Query Google Gemini API with retry logic for 503/429 errors.
        """
        model = self.judge_model if use_judge_model else self.model
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                payload: dict = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "maxOutputTokens": 4096,
                        "temperature": 0.7,
                    },
                }

                if system_prompt:
                    payload["systemInstruction"] = {
                        "parts": [{"text": system_prompt}]
                    }

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/{model}:generateContent",
                        params={"key": self.api_key},
                        json=payload,
                        timeout=60.0,
                    )
                    result = response.json()
                    
                    if "error" in result:
                        err_code = result["error"].get("code")
                        if err_code in [429, 503] and attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt) # Exponential backoff
                            continue
                        return f"Gemini API Error: {result['error']}"
                        
                    return (
                        result.get("candidates", [{}])[0]
                        .get("content", {})
                        .get("parts", [{}])[0]
                        .get("text", "No response from Gemini.")
                    )
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return f"Error querying Gemini: {str(e)}"


class GroqAPI:
    """Wrapper for Groq API (External Model 2 & Internal Agents)"""

    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.model = "llama-3.3-70b-versatile"   # updated from deprecated 3.1-70b
        self.base_url = "https://api.groq.com/openai/v1"

    async def query(self, prompt: str, system_prompt: str = None) -> str:
        """Query Groq API"""
        try:
            async with httpx.AsyncClient() as client:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 4096,
                    },
                    timeout=60.0,
                )
                result = response.json()
                return (
                    result.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "No response")
                )
        except Exception as e:
            return f"Error querying Groq: {str(e)}"


class OpenRouterAPI:
    """Wrapper for OpenRouter API (External Model 3)"""

    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.model = "meta-llama/llama-3.1-8b-instruct:free"
        self.base_url = "https://openrouter.io/api/v1"

    async def query(self, prompt: str, system_prompt: str = None) -> str:
        """Query OpenRouter API"""
        try:
            async with httpx.AsyncClient() as client:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 4096,
                    },
                    timeout=60.0,
                )
                result = response.json()
                return (
                    result.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "No response")
                )
        except Exception as e:
            return f"Error querying OpenRouter: {str(e)}"


class DuckDuckGoSearchAPI:
    """Wrapper for DuckDuckGo Web Search (No API key required!)"""

    async def search(self, query: str, max_results: int = 5) -> list:
        """Search the web using DuckDuckGo (Free, no API key needed)"""
        try:
            results = []
            with DDGS() as ddgs:
                for result in ddgs.text(query, max_results=max_results):
                    results.append({
                        'title': result.get('title', ''),
                        'content': result.get('body', ''),
                        'link': result.get('href', '')
                    })
            return results
        except Exception as e:
            return [{"error": f"Error searching: {str(e)}"}]


# Initialize API clients
gemini = GoogleGeminiAPI()
groq = GroqAPI()
openrouter = OpenRouterAPI()
tavily = DuckDuckGoSearchAPI()  # Using DuckDuckGo
