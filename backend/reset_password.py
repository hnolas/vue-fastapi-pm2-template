from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# Generate a hash for the password "password"
hashed_password = get_password_hash("password")
print(f"Generated hash for 'password': {hashed_password}")
print('Update the RESEARCHER dictionary in backend/app/api/auth.py with this hash')