"""
Project Consensus: Multi-Agent AI Research Engine
Main entry point for testing and running the system
"""
import asyncio
import sys
from config import validate_api_keys
from api_wrappers import gemini, groq, openrouter, tavily


async def test_all_apis():
    """Test all API connections"""
    print("🚀 Testing Project Consensus API Connections...\n")
    
    # Validate API keys first
    if not validate_api_keys():
        print("\n❌ Cannot proceed without API keys. Please fill in .env file.")
        return False
    
    test_prompt = "Hello! Please respond with a single sentence confirming you are working."
    
    print("\n" + "="*60)
    print("Testing External LLMs")
    print("="*60)
    
    # Test Gemini
    print("\n1️⃣  Testing Google Gemini (gemini-1.5-flash)...")
    try:
        gemini_result = await gemini.query(test_prompt)
        print(f"✅ Response: {gemini_result[:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test Groq
    print("\n2️⃣  Testing Groq (llama-3.1-70b-versatile)...")
    try:
        groq_result = await groq.query(test_prompt)
        print(f"✅ Response: {groq_result[:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test OpenRouter
    print("\n3️⃣  Testing OpenRouter (llama-3.1-8b-instruct)...")
    try:
        openrouter_result = await openrouter.query(test_prompt)
        print(f"✅ Response: {openrouter_result[:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "="*60)
    print("Testing Web Search")
    print("="*60)
    
    # Test DuckDuckGo Search
    print("\n🔍 Testing DuckDuckGo Web Search (No API key needed)...")
    try:
        search_results = await tavily.search("what is artificial intelligence", max_results=3)
        print(f"✅ Found {len(search_results)} results")
        if search_results and 'error' not in search_results[0]:
            print(f"   First result: {search_results[0].get('title', 'N/A')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ All API Tests Passed!")
    print("="*60)
    return True


async def run_research(query: str):
    """Run the full Project Consensus pipeline"""
    from executor import full_research_pipeline
    
    if not validate_api_keys():
        print("\n❌ Cannot proceed without API keys. Please fill in .env file.")
        return
    
    print(f"\n📝 User Query: {query}\n")
    research_note = await full_research_pipeline(query)
    
    print("\n" + "="*70)
    print("FINAL RESEARCH NOTE")
    print("="*70)
    print(research_note)
    print("="*70)


async def interactive_mode():
    """Interactive mode for running queries"""
    print("\n" + "="*70)
    print("🎯 PROJECT CONSENSUS - INTERACTIVE MODE")
    print("="*70)
    print("Enter your research question (or 'quit' to exit):")
    
    while True:
        try:
            query = input("\n🔍 Research Query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thank you for using Project Consensus!")
                break
            
            if not query:
                print("⚠️  Please enter a valid query.")
                continue
            
            await run_research(query)
            
        except KeyboardInterrupt:
            print("\n\n👋 Session ended.")
            break


async def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("🚀 PROJECT CONSENSUS - MULTI-AGENT AI RESEARCH ENGINE")
    print("="*70)
    print("\nOptions:")
    print("  1. Test API connections")
    print("  2. Run a research query")
    print("  3. Interactive mode")
    print("  4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        success = await test_all_apis()
        if success:
            print("\n✨ Ready to run research queries!")
    
    elif choice == "2":
        query = input("\n🔍 Enter your research question: ").strip()
        if query:
            await run_research(query)
        else:
            print("❌ No query provided.")
    
    elif choice == "3":
        await interactive_mode()
    
    elif choice == "4":
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid option. Please try again.")


if __name__ == "__main__":
    asyncio.run(main())