from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

REQUEST_COUNT=Counter("http_requests_total", "Total HTTP requests",['method','endpoint','status'])
REQUEST_LATENCY=Histogram("http_request_duration_seconds", "HTTP request latency",['method','endpoint'])


class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time=time.time()
        
        response:Response=await call_next(request)

        duration=time.time()-start_time
        endpoint=request.url.path
        
        REQUEST_LATENCY.labels(method=request.method,endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(method=request.method,endpoint=endpoint,status=response.status_code).inc()
        
        return response
    

def setup_metrics(app:FastAPI):
    app.add_middleware(PrometheusMiddleware)
    
    @app.get("/metrics",include_in_schema=False,)
    def metrics():
      return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST)
    

    
    
    