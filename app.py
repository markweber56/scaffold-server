from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {"abc": 123}

    return data

if __name__ == '__main__':
    app.run(debug=True)