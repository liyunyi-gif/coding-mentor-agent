"""快速验证 DeepSeek API 是否可用"""
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("AI_API_KEY")
if not api_key:
    print("[FAIL] AI_API_KEY is empty. Please set it in .env file")
    exit(1)

# 方式A：用 langchain-openai 测试（和项目一致）
print("=" * 50)
print("方式A：langchain-openai 调用测试")
print("=" * 50)
try:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(
        model="deepseek-chat",
        base_url="https://api.deepseek.com/v1",
        api_key=api_key,
        timeout=30,
        max_retries=2,
    )
    response = llm.invoke("用一句话解释什么是Python？")
    print(f"[OK] Success! Reply: {response.content[:200]}")
except Exception as e:
    print(f"[FAIL] Error: {e}")

# 方式B：用 openai SDK 直连测试
print()
print("=" * 50)
print("方式B：openai SDK 直连测试")
print("=" * 50)
try:
    from openai import OpenAI
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
        timeout=30,
    )
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "用一句话解释什么是Python？"}],
        max_tokens=200,
    )
    content = response.choices[0].message.content
    print(f"✅ 成功！回复: {content[:200]}")
except Exception as e:
    print(f"❌ 失败: {e}")
