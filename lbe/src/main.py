from fastapi import FastAPI
from fastapi import HTTPException
from qrs_data import QrsLogic
from qrs_data import Quote
from typing import List
from stocks import stocks

app = FastAPI()
quotes_data = QrsLogic()

app.include_router(stocks)

@app.on_event("startup")
def startup():
    quotes_data.run_periodic(1000)

@app.on_event("shutdown")
def shutdown():
    quotes_data.end_periodic_check()
