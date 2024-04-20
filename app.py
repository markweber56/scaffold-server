from flask import Flask
from flask_cors import CORS
from random import randint

allowed_origins = [
    "http://localhost:3000",
    "https://scaffold-web-c43c33ecc8e5.herokuapp.com/"
]

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

@app.route('/api/data', methods=['GET'])
def get_data():
    random_integer = randint(1, 100)
    data = {"abc": f"here's a random integer: {random_integer}"}

    return data

if __name__ == '__main__':
    app.run(debug=True)