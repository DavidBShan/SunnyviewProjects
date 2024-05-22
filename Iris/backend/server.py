import json
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.websockets import WebSocketState
from fastapi.middleware.cors import CORSMiddleware
# from llm import LlmClient
from llm_with_func_calling import LlmClient
from twilio_server import TwilioClient
from retellclient.models import operations
from twilio.twiml.voice_response import VoiceResponse
import retellclient
from retellclient.models import operations, components
import asyncio

load_dotenv(override=True)

app = FastAPI()

# Allow requests from all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
retell = retellclient.RetellClient(
    api_key="6151b021-8443-4a07-8718-d1c2eae9e34f",
)

# twilio_client.create_phone_number(213, os.environ['RETELL_AGENT_ID'])
# twilio_client.delete_phone_number("+12133548310")
# twilio_client.register_phone_agent("+14154750418", os.environ['RETELL_AGENT_ID'])
# twilio_client.create_phone_call("+12138982019", "+19367304543", os.environ['RETELL_AGENT_ID'])

@app.post("/register-call-on-your-server")
async def register_call_on_your_server(request: Request):
    try:
        call_response = retell.register_call(operations.RegisterCallRequestBody(
            agent_id="a29d458e9d138371eeecb3932f328ed9",
            audio_websocket_protocol='web',
            audio_encoding='s16le',
            sample_rate=24000
        ))
        if call_response.status_code == 201:
            print(call_response.status_code)
            print(call_response.call_detail.__dict__)
            return JSONResponse(call_response.call_detail.__dict__)
    except Exception as err:
        print(f"Error in twilio voice webhook: {err}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

@app.websocket("/llm-websocket/{call_id}")
async def websocket_handler(websocket: WebSocket, call_id: str):
    await websocket.accept()
    print(f"Handle llm ws for: {call_id}")

    llm_client = LlmClient()

    # send first message to signal ready of server
    response_id = 0
    first_event = llm_client.draft_begin_messsage()
    await websocket.send_text(json.dumps(first_event))

    async def stream_response(request):
        nonlocal response_id
        for event in llm_client.draft_response(request):
            await websocket.send_text(json.dumps(event))
            if request['response_id'] < response_id:
                return # new response needed, abondon this one
    try:
        while True:
            message = await websocket.receive_text()
            request = json.loads(message)
            # print out transcript
            os.system('cls' if os.name == 'nt' else 'clear')
            print(json.dumps(request, indent=4))
            
            if 'response_id' not in request:
                continue # no response needed, process live transcript update if needed
            response_id = request['response_id']
            asyncio.create_task(stream_response(request))
    except WebSocketDisconnect:
        print(f"LLM WebSocket disconnected for {call_id}")
    except Exception as e:
        print(f'LLM WebSocket error for {call_id}: {e}')
    finally:
        print(f"LLM WebSocket connection closed for {call_id}")