import os

from flask import Flask
from flask_cors import CORS
from random import randint

allowed_origins = [
    "http://localhost:3000",
    "https://scaffold-web-c43c33ecc8e5.herokuapp.com"
]

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

@app.route('/', methods=['GET'])
def home():
    return {"message": "you're home!"}

@app.route('/api/data', methods=['GET'])
def get_data():
    random_integer = randint(1, 100)
    data = {"abc": f"here's a random integer: {random_integer}"}

    return data

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use port provided by Heroku or default to 5000
    app.run(host='0.0.0.0', port=port)