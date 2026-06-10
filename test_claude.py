import asyncio
import sys
sys.path.append('.')

from services.claude_api import ClaudeService

async def test_claude():
    claude = ClaudeService()
    
    print("Testing Claude API...")
    
    result = await claude.evaluate_answer(
        user_answer="Product A for beginners, Product B for advanced",
        ideal_answer="Product A - for beginners, Product B - for advanced users with experience",
        question="Which users are suitable for Products A and B?"
    )
    
    print("Raw result:", repr(result))
    print("Score:", result['score'])
    print("Passed:", result['passed'])
    print("Feedback:", result['feedback'][:200])

if __name__ == "__main__":
    asyncio.run(test_claude())