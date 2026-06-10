from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "IDM-VTON Backend Running"

@app.route("/test")
def test():
    return jsonify({
        "success": True,
        "message": "Python backend working"
    })

@app.route("/tryon")
def tryon():
    return jsonify({
        "success": True,
        "message": "Try-On endpoint ready"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
