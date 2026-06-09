# 🚀 Project Consensus Setup Guide

## Overview
This guide will help you set up the **Project Consensus Multi-Agent AI Research Engine** with all API keys properly configured using environment variables.

## Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Get Your API Keys

### 1. **Google Gemini** (External Model 1)
- Go to: https://aistudio.google.com/
- Click "Get API Key"
- Create a new API key
- Copy the key

### 2. **Groq** (External Model 2 & Internal Agents)
- Go to: https://console.groq.com/
- Sign up and navigate to "API Keys"
- Create a new API key
- Copy the key

### 3. **OpenRouter** (External Model 3)
- Go to: https://openrouter.io/
- Sign up and go to "Keys"
- Create a new API key
- Copy the key

### 4. **DuckDuckGo** (Web Search - NO API KEY NEEDED! ✅)
- ✨ **No signup required!** 
- DuckDuckGo web search is built-in and completely free
- No rate limits for this project

## Step 3: Configure Your .env File

Open `.env` in the project directory and fill in your API keys:

```env
# Google Gemini API
GOOGLE_API_KEY=your_actual_google_key_here

# Groq API
GROQ_API_KEY=your_actual_groq_key_here

# OpenRouter API
OPENROUTER_API_KEY=your_actual_openrouter_key_here

# DuckDuckGo Search - No API key needed!
```

⚠️ **IMPORTANT**: 
- Never commit the `.env` file to version control
- The `.gitignore` should already include `.env`
- Use `.env.example` as a template

## Step 4: Verify Your Setup

Run the test script to verify all APIs are working:

```bash
python main.py
```

You should see:
- ✅ All API keys are configured!
- ✅ DuckDuckGo web search ready (no API key needed)
- Test responses from Gemini, Groq, and OpenRouter
- Search results from DuckDuckGo

## Project Structure

```
ai-research-engine/
├── main.py                 # Main test entry point
├── config.py               # API key configuration & validation
├── api_wrappers.py         # API wrapper classes for all services
├── requirements.txt        # Python dependencies
├── .env                    # Your API keys (DON'T COMMIT THIS!)
├── .env.example            # Template for .env file
├── .gitignore              # Ignore .env and other files
└── README.md               # This file
```

## Next Steps

After verifying the setup:

1. **Phase 3: Internal Debate** - Create agent prompt system
   - Researcher Agent
   - Statistician Agent
   - Critic Agent

2. **Phase 4: Judge & Output** - Implement final synthesis

3. **Phase 5: UI** - Build Streamlit interface

## Troubleshooting

### Error: "Missing API keys"
- Make sure you filled in all keys in the `.env` file
- Restart your terminal/IDE after updating `.env`

### Error: "Rate Limit" (429 Error)
- Free tier APIs have rate limits
- Add delays between queries: `await asyncio.sleep(2)`

### Error: "Connection timeout"
- Check your internet connection
- Verify the API endpoint is correct
- Some APIs may have regional restrictions

### ModuleNotFoundError
- Run: `pip install -r requirements.txt` again
- Make sure you're using the right Python version (3.10+)

## Security Notes

🔒 **CRITICAL**: 
- Never share your `.env` file
- Never commit `.env` to git
- Rotate API keys regularly
- Consider using environment variables in production instead

## Need Help?

- Check the `.env.example` file for the correct format
- Review API documentation on each provider's website
- Test each API individually using the wrapper classes

---

**Ready to build Project Consensus? Let's go! 🚀**
