from flask import Flask, jsonify
import os

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


@app.route("/hf-test")
def hf_test():

    token = os.getenv("HF_TOKEN")

    return jsonify({
        "success": bool(token),
        "message": "HF token found" if token else "HF token missing"
    })


@app.route("/space-test")
def space_test():

    try:

        space_name = "hysts-duplicates/IDM-VTON"

        return jsonify({
            "success": True,
            "space_name": space_name,
            "space_name_repr": repr(space_name)
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })


@app.route("/tryon")
def tryon():
    return jsonify({
        "success": True,
        "message": "Try-On endpoint ready"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
