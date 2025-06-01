import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes import customer, driver, truck, order, delivery

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Logistics Management API",
    description="A comprehensive API for managing logistics operations",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Se for produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    logger.info(f"Request: {request.method} {request.url}")

    try:
        response = await call_next(request)

        process_time = time.time() - start_time

        logger.info(
            f"Response: {response.status_code} - "
            f"Time: {process_time:.4f}s - "
            f"Path: {request.url.path}"
        )

        response.headers["X-Process-Time"] = str(process_time)

        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Error: {str(e)} - "
            f"Time: {process_time:.4f}s - "
            f"Path: {request.url.path}"
        )
        raise


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    from app.database import SessionLocal

    db = SessionLocal()
    request.state.db = db

    try:
        response = await call_next(request)
        return response
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        db.close()


app.include_router(customer.router, prefix="/api/v1", tags=["customers"])
app.include_router(driver.router, prefix="/api/v1", tags=["drivers"])
app.include_router(truck.router, prefix="/api/v1", tags=["trucks"])
app.include_router(order.router, prefix="/api/v1", tags=["orders"])
app.include_router(delivery.router, prefix="/api/v1", tags=["deliveries"])


@app.get("/")
async def root():
    return {
        "message": "Logistics Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True,
        log_level="info"
    )
