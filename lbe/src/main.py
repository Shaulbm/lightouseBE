import datetime
from threading import Timer
from fastapi import FastAPI, Request
from fastapi import HTTPException
from typing import List
from gateway import router
import gateway
from fastapi.middleware.cors import CORSMiddleware
import schedule
from concurrent.futures import ThreadPoolExecutor
import time
from moovLogic import MoovScheduler
from schedule import every, repeat

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

shuttingDown = False

@app.middleware('http')
async def get_user_details_from_header(request: Request, call_next):
    userContext = None
    
    if "X-USER-ID" in request.headers:
        userId = request.headers["X-USER-ID"]
        gateway.set_user_context(userId)
    else:
        print ('request called with no user context')

    response = await call_next(request)
    
    return response

def verifyTTL():
    MoovScheduler.verifyTTLObjects()

# runu on a thread of it's own - load the scheduler with jobs and run pending jobs
# every 5 seconds (if there are no current pending tasks the action is costless)
def runTTLVerification():
    schedule.every(15).seconds.do(verifyTTL)

    index = 0

    while not shuttingDown:
        schedule.run_pending()
        time.sleep(5)

@app.on_event("startup")
def startup():
    print ('on startup')
    executor = ThreadPoolExecutor(2)
    executor.submit(runTTLVerification)

@app.on_event("shutdown")
def shutdown():
    shuttingDown = True
