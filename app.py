from flask import Flask, request, jsonify
from flask_cors import CORS
from gradio_client import Client, handle_file
import tempfile
import base64
import traceback

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
CORS(app)


@app.route("/")
def home():
    return "IDM-VTON Backend Running"


@app.route("/tryon", methods=["POST"])
def tryon():

    try:

        data = request.get_json()

        user_image_b64 = data["userImage"]
        cloth_image_b64 = data["clothImage"]

        user_image_b64 = user_image_b64.split(",")[1]
        cloth_image_b64 = cloth_image_b64.split(",")[1]

        user_bytes = base64.b64decode(user_image_b64)
        cloth_bytes = base64.b64decode(cloth_image_b64)

        user_temp = tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False
        )

        cloth_temp = tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False
        )

        user_temp.write(user_bytes)
        cloth_temp.write(cloth_bytes)

        user_temp.close()
        cloth_temp.close()

        client = Client("hysts-duplicates/IDM-VTON")

        result = client.predict(
            dict={
                "background": handle_file(user_temp.name),
                "layers": [],
                "composite": None
            },
            garm_img=handle_file(cloth_temp.name),
            garment_des="shirt",
            is_checked=True,
            is_checked_crop=False,
            denoise_steps=30,
            seed=42,
            api_name="/tryon"
        )

        output_path = result[1]

        with open(output_path, "rb") as f:
            image_base64 = base64.b64encode(
                f.read()
            ).decode("utf-8")

        return jsonify({
            "success": True,
            "image": "data:image/webp;base64," + image_base64
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e),
            "trace": traceback.format_exc()
        })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=10000
    )
