from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from config import settings

# middleware for api key validation
class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # don't require API KEY validation
        bypass_paths = ["/docs", "/redoc", "/openapi.json", "/health"]
        
        if request.url.path in bypass_paths:
            return await call_next(request)
            
        api_key = request.headers.get("X-API-Key")
        
        if not api_key or api_key != settings.api_key:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or missing API key."}
            )
            
        response = await call_next(request)
        return response