from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import LoanRequest
from app.database import get_session
import pickle
import pandas as pd
import os
from app.schemas import LoanApplication
import sklearn
import catboost

router = APIRouter(prefix="/loans", tags=["Loans"])
# Charger le modèle une seule fois au démarrage
#MODEL_PATH = os.path.join(os.path.dirname(__file__), "loan_model.pkl")

with open("app/loan_model.pkl", "rb") as f:
    model = pickle.load(f)

FEATURES = ['State', 'NAICS', 'NewExist', 'RetainedJob', 
            'FranchiseCode', 'UrbanRural', 'GrAppv', 'Bank', 'Term']

@router.post("/predict")
def predict_loan_eligibility(application: LoanApplication):
     # Convertir l'entrée en DataFrame pour le modèle
    input_data = pd.DataFrame([application.dict()])

    # Faire la prédiction
    prediction = model.predict(input_data)

    # Retourner la prédiction (ex: 1 = Eligible, 0 = Non éligible)
    return {"eligible": bool(prediction[0])}

@router.post("/request")
def request_loan(amount: float, user_id: int, session: Session = Depends(get_session)):
    loan_request = LoanRequest(user_id=user_id, amount=amount)
    session.add(loan_request)
    session.commit()
    return {"message": "Loan request submitted"}

@router.get("/history")
def get_loan_history(user_id: int, session: Session = Depends(get_session)):
    loans = session.exec(select(LoanRequest).where(LoanRequest.user_id == user_id)).all()
    return {"history": loans}
