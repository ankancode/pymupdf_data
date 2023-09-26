from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import uvicorn
from starlette.requests import Request
from starlette.datastructures import Headers


limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Note: the route decorator must be above the limit decorator, not below it
@app.get("/home")
@limiter.limit("5/minute")
async def homepage(request: Request):
    print(request)
    return PlainTextResponse("test")

@app.get("/mars")
@limiter.limit("5/minute")
async def homepage(request: Request):
    print(request)
    return {"key": "value"}

if __name__ == "__main__":
    uvicorn.run("slowapi_based:app", reload=True)
