import asyncio
import httpx
import os

async def test_streaming():
    url = "http://127.0.0.1:8013/chat"
    payload = {"message": "What is Amazon SageMaker?"}
    
    print(f"Sending request to {url}...")
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, json=payload, timeout=30.0) as response:
            print(f"Response status: {response.status_code}")
            full_content = ""
            async for chunk in response.aiter_text():
                print(f"Chunk: {repr(chunk)}")
                full_content += chunk
            
            print("\nFull content received:")
            print(full_content)
            
            try:
                import json
                parsed = json.loads(full_content)
                print("\nParsed JSON:")
                print(parsed)
            except json.JSONDecodeError as e:
                print(f"\nJSON Decode Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_streaming())
