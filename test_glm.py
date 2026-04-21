import asyncio
from openai import AsyncOpenAI

async def test_brain():
    # Direct hit to your local RTX 3090
    client = AsyncOpenAI(api_key="EMPTY", base_url="http://localhost:8000/v1")
    model_id = "/home/ubuntu/glm4_flash_int4"
    
    print(f"Checking connection to {model_id}...")
    try:
        response = await client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": "Prove you are alive. Reply with: 'Vixero GPU Online'."}],
            max_tokens=20
        )
        print(f"\n✅ GPU RESPONSE: {response.choices[0].message.content}\n")
    except Exception as e:
        print(f"❌ CONNECTION FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_brain())