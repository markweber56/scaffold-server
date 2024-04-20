import os

from flask import Flask, request
from flask_cors import CORS
from random import randint

allowed_origins = [
    "http://localhost:3000",
    "https://scaffold-web"
    
]

app = Flask(__name__)
# cors = CORS(app, resources={r"/api/*": {"origins": allowed_origins}})
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return {"message": "you're home!"}

@app.route('/api/data', methods=['GET'])
def get_data():
    random_integer = randint(1, 100)
    data = {"abc": f"here's a random integer: {random_integer}"}

    return data

@app.after_request
def apply_cors(response):
    allowed_origin = determine_allowed_origin(request.headers.get('Origin'))
    response.headers.add('Access-Control-Allow-Origin', allowed_origin)
    return response

def determine_allowed_origin(origin):
    # Check if the origin matches the pattern you want to allow
    for allowed_origin in allowed_origins:
        print(f"origin: {origin}")
        if origin and origin.startswith(allowed_origin):
            print(f"allowed origin: {allowed_origin}")
            print(f"origin starts with: {origin.startswith(allowed_origin)}")
            print(f'origin: {origin} is allowed')
            return origin
        elif origin is None:
            print(f'origin is None allowing request')
            return '*'
        
    print(f'origin {origin} not allowed')
    return 'null' # Deny requests from other origins

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use port provided by Heroku or default to 5000
    app.run(host='0.0.0.0', port=port)