from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.models import LoanRequest
from app.database import get_session
import pickle
import pandas as pd
from app.schemas import LoanApplication
from app.dependencies import get_current_user
from datetime import datetime
from typing import Optional


router = APIRouter(prefix="/loans", tags=["Loans"])
# Charger le modèle une seule fois au démarrage
#MODEL_PATH = os.path.join(os.path.dirname(__file__), "loan_model.pkl")

with open("app/loan_model.pkl", "rb") as f:
    model = pickle.load(f)

FEATURES = ['State', 'NAICS', 'NewExist', 'RetainedJob', 
            'FranchiseCode', 'UrbanRural', 'GrAppv', 'Bank', 'Term']

@router.post("/predict")
def predict_loan_eligibility(application: LoanApplication, current_user: dict = Depends(get_current_user), db: Session = Depends(get_session)):
     # Convertir l'entrée en DataFrame pour le modèle
    input_data = pd.DataFrame([application.dict()])
    # Faire la prédiction
    prediction = model.predict(input_data)
    # Stocker la requête dans LoanRequest
    loan_request = LoanRequest(
        user_id=current_user["id"],  # ID de l'utilisateur connecté
        amount=application.GrAppv,   # Montant demandé
        status="approved" if prediction[0] == 1 else "denied",
        created_at=datetime.utcnow()
    )

    db.add(loan_request)
    db.commit()
    db.refresh(loan_request)

    # Retourner la prédiction (ex: 1 = Eligible, 0 = Non éligible)
    return {"eligible": bool(prediction[0]), "loan_request_id": loan_request.id}

@router.post("/request")
def request_loan(amount: float, user_id: int, session: Session = Depends(get_session)):
    loan_request = LoanRequest(user_id=user_id, amount=amount)
    session.add(loan_request)
    session.commit()
    return {"message": "Loan request submitted"}

@router.get("/history")
def get_loan_history(
    current_user: dict = Depends(get_current_user),  
    db: Session = Depends(get_session),
    status: Optional[str] = Query(None, description="Filtrer par statut (approved, denied, pending)")
):
    # Récupérer toutes les demandes de l'utilisateur
    query = select(LoanRequest).where(LoanRequest.user_id == current_user["id"])

    # Appliquer un filtre si un statut est donné
    if status:
        query = query.where(LoanRequest.status == status)

    loan_requests = db.exec(query).all()

    # Retourner l'historique des demandes
    return [
        {
            "id": request.id,
            "amount": request.amount,
            "status": request.status,
            "created_at": request.created_at
        }
        for request in loan_requests
    ]