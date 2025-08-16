import jwt
import datetime
import sys
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_token.py <email>")
        sys.exit(1)

    user_email = sys.argv[1]
    
    # Set the expiration time for the token
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Generate the token
    access_token = create_access_token(
        data={"sub": user_email}, expires_delta=access_token_expires
    )
    
    print(f"Generated token for {user_email}:")
    print(access_token)
