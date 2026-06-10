from bot.config import load_config
import anthropic

config = load_config()
print("API Key length:", len(config.claude_api_key))
print("API Key starts with:", config.claude_api_key[:15])

try:
    client = anthropic.Anthropic(api_key=config.claude_api_key)
    print("✅ Client created")
    
    # Простой тест API
    response = client.messages.create(
        model="claude-sonnet-4-20250514", #"claude-3-haiku-20240307",
        max_tokens=10,
        messages=[{"role": "user", "content": "Hi"}]
    )
    print("✅ API works! Response:", response.content[0].text[:50])
    
except Exception as e:
    print("❌ API Error:", str(e))