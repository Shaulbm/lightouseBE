from fastapi import FastAPI
from fastapi import HTTPException
from qrs_data import QrsLogic
from qrs_data import Quote
from typing import List
from stocks import stocks
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

#quotes_data = QrsLogic()

app.include_router(stocks)

@app.on_event("startup")
def startup():
   # quotes_data.run_periodic(1000)
    pass

@app.on_event("shutdown")
def shutdown():
    #quotes_data.end_periodic_check()
    pass
