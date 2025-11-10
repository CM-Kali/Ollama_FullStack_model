# server.py
import asyncio
import json
import os
from typing import AsyncGenerator

import pandas as pd
import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2")  # change as needed

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load CSV once at startup
try:
    CSV_PATH = "pizza_reviews.csv"
    df = pd.read_csv(CSV_PATH)

    reviews_list = []
    for _, review in df.iterrows():
        reviews_list.append(
            f"Review {int(review['review_id'])}: {review['review_text']} (Rating: {review['rating']}/5, Sentiment: {review['sentiment']})"
        )
    REVIEWS_TEXT = "\n".join(reviews_list)
    logger.info(f"Loaded {len(reviews_list)} reviews successfully")
except Exception as e:
    logger.error(f"Error loading CSV: {e}")
    REVIEWS_TEXT = "No reviews available"

async def stream_from_ollama(prompt: str) -> AsyncGenerator[str, None]:
    """
    Call Ollama /api/generate in streaming mode and yield text chunks.
    """
    url = f"{OLLAMA_URL}/api/generate"
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True
    }

    logger.info(f"Streaming from Ollama with prompt length: {len(prompt)}")
    
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            async with client.stream("POST", url, json=payload) as resp:
                if resp.status_code != 200:
                    text = await resp.aread()
                    error_msg = f"Ollama response {resp.status_code}: {text.decode(errors='ignore')}"
                    logger.error(error_msg)
                    yield f"Error: {error_msg}"
                    return
                
                async for raw_line in resp.aiter_lines():
                    if not raw_line.strip():
                        continue
                    try:
                        obj = json.loads(raw_line)
                        if "response" in obj:
                            yield obj["response"]
                        elif "error" in obj:
                            yield f"Error: {obj['error']}"
                        # Check if this is the final response
                        if obj.get("done", False):
                            break
                    except json.JSONDecodeError as e:
                        logger.warning(f"JSON decode error: {e}, line: {raw_line}")
                        continue
    except httpx.ConnectError:
        error_msg = f"Cannot connect to Ollama at {OLLAMA_URL}. Please ensure Ollama is running."
        logger.error(error_msg)
        yield f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        yield f"Error: {error_msg}"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        # Expect initial JSON message from client
        data = await websocket.receive_text()
        message_data = json.loads(data)
        user_question = message_data.get("question", "").strip()
        
        if not user_question:
            await websocket.send_json({"type": "error", "message": "Empty question"})
            await websocket.close()
            return

        logger.info(f"Received question: {user_question}")

        # Build prompt
        prompt = f"""
You are an expert in analyzing pizza restaurant reviews.

Here are customer reviews:
{REVIEWS_TEXT}

Please answer this question: {user_question}

Provide a detailed analysis based on the reviews above.
"""

        # Stream response from Ollama
        async for chunk in stream_from_ollama(prompt):
            await websocket.send_json({"type": "chunk", "text": chunk})
            # Small delay to prevent overwhelming the client
            await asyncio.sleep(0.01)

        # Send completion message
        await websocket.send_json({"type": "done"})
        
    except WebSocketDisconnect:
        logger.info("Client disconnected normally")
    except json.JSONDecodeError:
        await websocket.send_json({"type": "error", "message": "Invalid JSON received"})
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"type": "error", "message": f"Server error: {str(e)}"})
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass

# Test endpoint to verify server is working
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "reviews_loaded": len(REVIEWS_TEXT) > 0,
        "ollama_url": OLLAMA_URL,
        "model": MODEL_NAME
    }

# Simple root page for manual testing
@app.get("/")
async def root():
    return HTMLResponse("""
    <html>
        <head>
            <title>Pizza Reviews AI</title>
        </head>
        <body>
            <h3>Pizza Reviews AI Server</h3>
            <p>WebSocket endpoint: /ws</p>
            <p>Health check: <a href="/health">/health</a></p>
            <div>
                <h4>Test the WebSocket:</h4>
                <input type="text" id="question" placeholder="Enter your question" style="width: 300px;">
                <button onclick="sendQuestion()">Send</button>
                <div id="response" style="margin-top: 20px; border: 1px solid #ccc; padding: 10px; min-height: 100px;"></div>
            </div>
            <script>
                let ws = null;
                
                function connect() {
                    ws = new WebSocket('ws://localhost:8000/ws');
                    
                    ws.onopen = function() {
                        console.log('Connected to server');
                    };
                    
                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        const responseDiv = document.getElementById('response');
                        
                        if (data.type === 'chunk') {
                            responseDiv.innerHTML += data.text;
                        } else if (data.type === 'error') {
                            responseDiv.innerHTML = '<span style="color: red;">Error: ' + data.message + '</span>';
                        } else if (data.type === 'done') {
                            responseDiv.innerHTML += '<hr><em>Response complete</em>';
                        }
                    };
                    
                    ws.onclose = function() {
                        console.log('Connection closed');
                    };
                    
                    ws.onerror = function(error) {
                        console.error('WebSocket error:', error);
                        document.getElementById('response').innerHTML = '<span style="color: red;">Connection error</span>';
                    };
                }
                
                function sendQuestion() {
                    const question = document.getElementById('question').value;
                    const responseDiv = document.getElementById('response');
                    
                    if (!ws || ws.readyState !== WebSocket.OPEN) {
                        connect();
                    }
                    
                    responseDiv.innerHTML = 'Loading...';
                    
                    // Wait a bit for connection to establish
                    setTimeout(() => {
                        if (ws && ws.readyState === WebSocket.OPEN) {
                            ws.send(JSON.stringify({question: question}));
                        } else {
                            responseDiv.innerHTML = '<span style="color: red;">Not connected to server</span>';
                        }
                    }, 100);
                }
                
                // Connect on page load
                connect();
            </script>
        </body>
    </html>
    """)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")