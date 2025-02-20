from passlib.context import CryptContext
import bcrypt

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
hashed = pwd_context.hash("test123")

print(hashed)  # Vérifie si ça retourne bien un hash
print(bcrypt.__version__)