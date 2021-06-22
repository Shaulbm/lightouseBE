from fastapi import Header, APIRouter
from qrs_data import QrsLogic
from qrs_data import Quote
from fastapi import HTTPException
from users import UsersLogic

stocks = APIRouter()
quotes_data = QrsLogic()
users = UsersLogic()

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

@stocks.post("/registerUser")
def register_user(user):
    userDetails = users.registerUser(userName=user)
    return userDetails

@stocks.get("/createTrainingData")
def create_training_data():
    users.createTrainingData()
    pass

@stocks.post("/getTrainingStage")
def get_training_stage(issueId, stage):
    trainingDetails = users.getTrainingStage(issueId, stage)
    return trainingDetails
