from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import json
import jwt
from jose import JWTError
import traceback
from fastapi import Depends


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            # Default user to unauthenticated
            user = "Unauthenticated"
            
            # Try to get user identity from JWT
            try:
                # Assuming you're using Authorization header with Bearer token
                auth_header = request.headers.get('Authorization')
                if auth_header and auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                    # You'll need to replace this with your actual JWT decoding logic
                    # This is a placeholder and should match your actual token verification
                    try:
                        payload = jwt.decode(token, options={"verify_signature": False})
                        print(payload,"jwt payload")
                        user = payload.get('user_id', 'Unauthenticated')
                    except (jwt.ExpiredSignatureError, JWTError):
                        print(f"Invalid or expired token for request: {request.url.path}")
            except Exception as jwt_error:
                print(f"JWT Verification Error: {str(jwt_error)}")
            
            # Get client IP (works with most reverse proxies)
            client_ip = request.client.host
            
            # Get query parameters
            query_params = dict(request.query_params)
            
            # Get request body data
            body_data = {}
            try:
                # Read the request body
                body = await request.body()
                if body:
                    try:
                        body_data = json.loads(body.decode('utf-8'))
                    except json.JSONDecodeError:
                        body_data = {"error": "Could not parse body"}
            except Exception as body_error:
                print(f"Error reading request body: {str(body_error)}")
            
            # Log request details
            print(
                f"API Request: "
                f"Method={request.method}, "
                f"Path={request.url.path}, "
                f"User={user}, "
                f"IP={client_ip}, "
                f"Query_Params={query_params}, "
                f"Body={body_data}"
            )
            
            # Continue with the request
            response = await call_next(request)
            print(f"Response : {response}")
            return response
        
        except Exception as e:
            # Log the unexpected error and re-raise so that FastAPI can handle it properly
            print(f"Unexpected error in request logging: {str(e)}")
            traceback.print_exc()
            raise
