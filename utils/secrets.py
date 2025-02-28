from passlib.context import CryptContext

passwordManager = CryptContext(schemes=["bcrypt"], deprecated="auto")
