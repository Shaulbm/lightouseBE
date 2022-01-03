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

def runTTLVerification():
    print ('in run TTL verification')
    moovScheduler = MoovScheduler()

    # schedule.every(5).seconds.do(moovScheduler.verifyTTLObjects)
    schedule.every(5).seconds.do(job)


    if shuttingDown:
        print ('shtting down is True')

    while not shuttingDown:
        print ('in loop')
        schedule.run_pending()
        print ('in main runTTL time is ', datetime.datetime.utcnow().strftime())
        time.sleep(15)

@app.on_event("startup")
def startup():
    print ('in startup')
    executor = ThreadPoolExecutor(2)
    executor.submit(runTTLVerification)

@app.on_event("shutdown")
def shutdown():
    shuttingDown = True

