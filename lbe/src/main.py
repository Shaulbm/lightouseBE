from fastapi import FastAPI, Request
from fastapi import HTTPException
from typing import List
from gateway import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.middleware('http')
async def get_user_details_from_header(request: Request, call_next):
    userId = request.headers["X-USER-ID"]
    print ("server request user id is {}", userId)
    response = await call_next(request)
    return response


@app.on_event("startup")
def startup():
    pass

@app.on_event("shutdown")
def shutdown():
    pass
