from contextlib import nullcontext
from fastapi import FastAPI, Request
import asyncio, uvicorn
from sqlalchemy import true
from sse_starlette.sse import EventSourceResponse
from fastapi.responses import HTMLResponse
import random
app = FastAPI()

@app.get('/')
def root(request: Request):
    html = """
    <html>
        <head>
            <title>Some HTML in here</title>
            <script src="https://unpkg.com/htmx.org@1.4.1"></script>

        </head>
        <body hx-sse="connect:/stream">
            <h1 hx-sse="swap:new_message">Look ma! HTML!</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)


STREAM_DELAY = 1  # second
RETRY_TIMEOUT = 15000  # milisecond

@app.get('/stream')
async def message_stream(request: Request):
    def new_messages():
        # Add logic here to check for new messages
        yield 'Hello World'
    async def event_generator():
        while True:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break

            # Checks for new messages and return them to client if any
            yield {
                    "event": "new_message",
                    "id": "message_id",
                    "retry": RETRY_TIMEOUT,
                    "data": str(random.randint(0,100))
            }

            await asyncio.sleep(STREAM_DELAY)

    return EventSourceResponse(event_generator())