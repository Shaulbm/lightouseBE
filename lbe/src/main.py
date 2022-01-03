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
from mongoLogic import MoovScheduler
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

@app.middleware('http')
async def get_user_details_from_header(request: Request, call_next):
    userContext = None
    
    if "X-USER-ID" in request.headers:
        userId = request.headers["X-USER-ID"]
        # print ("server request user id is {0}", userId)
        gateway.set_user_context(userId)
    else:
        print ('request called with no user context')

    response = await call_next(request)
    
    return response

shuttingDown = False

def job():
    print ('in a job')

@repeat(every(5).seconds)
def runTTLVerification():
    print ('in run TTL verification')
    moovScheduler = MoovScheduler()

    moovScheduler.verifyTTLObjects()
    # schedule.every(5).seconds.do(job)

    # while not shuttingDown:
    #     print ('in loop')
    #     schedule.run_pending()
    #     print ('in main runTTL time is ', datetime.datetime.utcnow().strftime())
    #     time.sleep(1)

@app.on_event("startup")
def startup():
    pass

@app.on_event("shutdown")
def shutdown():
    shuttingDown = True

