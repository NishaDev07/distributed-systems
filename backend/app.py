from flask import Flask, jsonify
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS so frontend can access API

@app.route("/api/listings", methods=["GET"])
def get_listings():
    with open('backend/listings.json', "r") as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
