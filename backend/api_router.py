from typing import Callable
from fastapi import Request, Response
from fastapi.routing import APIRoute
import json
import time

class LoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            before = time.time()
            # Read body before the request is handled
            body = await request.body()
            # Restore body so it can be read again by the endpoint
            request._body = body

            try:
                response: Response = await original_route_handler(request)
            except Exception as e:
                # Log exception details here if needed
                print(f"Request failed with exception: {e}")
                raise e # Re-raise the exception to be handled by FastAPI

            duration = time.time() - before

            # Log request details
            user = "Unauthenticated"
            if hasattr(request.state, "user"):
                user = request.state.user.email

            body_data = {}
            if body:
                try:
                    body_data = json.loads(body.decode('utf-8'))
                except json.JSONDecodeError:
                    body_data = {"error": "Could not parse body"}

            print(
                f'API Request: '
                f'Method={request.method}, '
                f'Path={request.url.path}, '
                f'User={user}, '
                f'IP={request.client.host}, '
                f'Query_Params={dict(request.query_params)}, '
                f'Body={body_data}, '
                f'Status={response.status_code}, '
                f'Duration={duration:.2f}s'
            )

            return response

        return custom_route_handler
