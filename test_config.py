from bot.config import load_config

config = load_config()
print(f"✅ Bot Token: {config.bot_token[:20]}...")
print(f"✅ Claude Key: {config.claude_api_key[:20]}...")
print(f"✅ DB URL: {config.database_url}")