from fastapi import Header, APIRouter
from qrs_data import QrsLogic
from qrs_data import Quote
from fastapi import HTTPException

stocks = APIRouter()
quotes_data = QrsLogic()

@stocks.post("/register")
def register_stock(stock):
    quotes_data.register_stock(stock)

@stocks.post("/unregister")
def unregister_stock(stock):
    quotes_data.unregister_stock(stock)
    
@stocks.get("/run")
def run_periodic():
    pass

@stocks.get("/quotes")
def read_default():
    current_stocks = quotes_data.get_current_stocks()
    if len(current_stocks) == 0:
        raise HTTPException (status_code = 404, detail="the stocks list is empy")
    return current_stocks
