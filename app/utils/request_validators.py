from flask import request
from ..extensions.redis import redis_client
from .api import decode_jwt

# TODO: Validator Response class: is_valid, validation_errors


class Validator:
    def __init__(self, route: str, request: request):
        self.route = route
        self.form = request.form.to_dict()
        self.request_json = request.get_json()
        self.headers = request.headers

    def get_validator(self):
        ROUTE_VALIDATORS = {
            'auth/login': self.validate_auth_login,
            'api': self.validate_user
        }

        return ROUTE_VALIDATORS.get(self.route)

    def validate(self):
        is_valid = False
        validation_method = self.get_validator()

        if validation_method:
            is_valid = validation_method()
        else:
            print(f'Validator for {self.route} does not exist')

        return is_valid

    def validate_auth_login(self):
        required_fields = ['email', 'password']
        has_required_fields, missing_fields = self.has_required_fields(required_fields)
        print("validating auth login")
        if not has_required_fields:
            print(f'Form is missing field(s): {missing_fields}')
            return False
        return True

    def has_required_fields(self, required_fields: list[str]):
        missing_fields = []
        has_required_fields = True
        for field in required_fields:
            if self.request_json.get(field) is None:
                missing_fields.append(field)
                has_required_fields = False

        return has_required_fields, missing_fields

    def validate_user(self):
        has_required_headers, missing_headers = self.has_required_headers()
        if not has_required_headers:
            print(f'Request is missing header(s): {missing_headers}')
            return False
        user_id = self.headers.get('X-User-ID')
        request_token = self.headers.get('Authorization')

        stored_token = redis_client.get(user_id).decode('utf-8')

        if stored_token is None:
            print('User not logged in')
            return False
        if request_token != stored_token:
            print('Bad token. Return to login')
            return False
        try:
            decoded_token = decode_jwt(request_token)
        except Exception:  # ExpiredSignatureError:
            print("Token expired. Return to sign in")
            return False

        print(f'Found a token: {decoded_token}')

        return True

    def has_required_headers(self):
        # required_headers = ['Authorization', 'X-User-ID']
        required_headers = ['Authorization']
        has_required_headers = True
        missing_headers = []
        for header in required_headers:
            if self.headers.get(header) is None:
                missing_headers.append(header)
                has_required_headers = False

        return has_required_headers, missing_headers
