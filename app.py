from flask import Flask, jsonify
from gradio_client import Client
import traceback
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "IDM-VTON Backend Running"

@app.route("/space-test")
def space_test():

    try:

        client = Client("hysts-duplicates/IDM-VTON")

        return jsonify({
            "success": True,
            "message": "Client created successfully"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e),
            "type": str(type(e)),
            "trace": traceback.format_exc()
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
