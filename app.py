from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Provenance Guard API is running",
        "endpoints": ["/submit", "/appeal", "/log", "/analytics"]
    })


if __name__ == "__main__":
    app.run(debug=True)