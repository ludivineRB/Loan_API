from sqlmodel import Session, select
from app.database import engine
from app.models import User
from passlib.context import CryptContext

# # Initialisation du contexte de hashage
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # Détails de l'admin
# ADMIN_EMAIL = "admin@example.com"
# ADMIN_PASSWORD = "MonSuperMotDePasse123"

# def create_admin():
#     with Session(engine) as session:
#         # Vérifie si l'admin existe déjà
#         existing_admin = session.exec(select(User).where(User.email == ADMIN_EMAIL)).first()
#         if existing_admin:
#             print("⚠ Admin existe déjà !")
#             return
        
#         # Création du hash du mot de passe
#         hashed_password = pwd_context.hash(ADMIN_PASSWORD)

#         # Création de l'utilisateur admin
#         admin = User(email=ADMIN_EMAIL, password=hashed_password, role="admin", is_active=True)
#         session.add(admin)
#         session.commit()
#         print("✅ Admin ajouté avec succès !")

# if __name__ == "__main__":
#     create_admin()
from sqlmodel import Field, Session, SQLModel, create_engine
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

# Définir la base de données et la session
DATABASE_URL = "sqlite:///./app/database.db"
engine = create_engine(DATABASE_URL)


# Initialisation de passlib pour le hashage des mots de passe avec argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    """Fonction pour hacher le mot de passe avec argon2"""
    return pwd_context.hash(password)

def create_admin():
    """Fonction pour créer un utilisateur admin"""
    # Créer une session SQLModel
    with Session(engine) as session:
        # Hash du mot de passe
        hashed_password = hash_password("password123")

        # Créer un utilisateur admin
        user = User(
            email="admin@example.com",
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True,
        )

        # Ajouter l'utilisateur à la session
        session.add(user)
        try:
            session.commit()
            print("Utilisateur admin créé avec succès.")
        except IntegrityError as e:
            print(f"Erreur d'intégrité lors de la création de l'utilisateur : {e}")
            session.rollback()
        except Exception as e:
            print(f"Erreur lors de la création de l'utilisateur : {e}")
            session.rollback()

# Créer l'admin dans la base de données
create_admin()
