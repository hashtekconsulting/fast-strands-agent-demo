import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from strands import Agent
from strands.models.gemini import GeminiModel

app = FastAPI()

# Initialize Strands Agent with native Gemini provider
try:
    model = GeminiModel(
        model_id="gemini-2.5-flash",
        client_args={
            "api_key": os.environ.get("GEMINI_API_KEY")
        }
    )
    agent = Agent(model=model)
except Exception as e:
    print(f"Warning: Failed to initialize Strands Agent: {e}")
    agent = None

# Define the structured output model
class Answer(BaseModel):
    component: str = Field(description="The response from the model")

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not agent:
        raise HTTPException(status_code=503, detail="Strands Agent not initialized")
    
    async def generate():
        try:
            # Stream the response using stream_async with structured output
            async for event in agent.stream_async(
                request.message,
                structured_output_model=Answer
            ):
                if "data" in event:
                    # Yield the raw JSON chunks as they are generated
                    yield event["data"]
        except Exception as e:
            yield f"Error: {str(e)}"

    # Return text/plain or application/json depending on preference, 
    # but since we are streaming raw partial JSON, text/plain might be safer for simple clients
    # or application/x-ndjson if it were line delimited, but here it's a single JSON object streamed.
    return StreamingResponse(generate(), media_type="application/json")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
