from flask import Flask, request, jsonify
from flask_cors import CORS
from gradio_client import Client, handle_file
import tempfile
import base64
import traceback
import os

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

CORS(app)

# Global client
client = None


def get_client():

    global client

    if client is None:

        print("Connecting to yisol/IDM-VTON...")

        client = Client(
            "yisol/IDM-VTON",
            download_files=False
        )

        print("Connected successfully!")

    return client


@app.route("/")
def home():

    return "IDM-VTON Backend Running"


@app.route("/tryon", methods=["POST"])
def tryon():

    global client

    user_temp_path = None
    cloth_temp_path = None

    try:

        print("TRY-ON REQUEST RECEIVED")

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "error": "No JSON data received"
            }), 400

        if "userImage" not in data:

            return jsonify({
                "success": False,
                "error": "userImage is missing"
            }), 400

        if "clothImage" not in data:

            return jsonify({
                "success": False,
                "error": "clothImage is missing"
            }), 400

        # Get Base64 data

        user_image_b64 = data["userImage"]
        cloth_image_b64 = data["clothImage"]

        # Remove data URL prefix

        if "," in user_image_b64:

            user_image_b64 = user_image_b64.split(",", 1)[1]

        if "," in cloth_image_b64:

            cloth_image_b64 = cloth_image_b64.split(",", 1)[1]

        # Decode images

        user_bytes = base64.b64decode(user_image_b64)

        cloth_bytes = base64.b64decode(cloth_image_b64)

        # Create temporary files

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

        user_temp_path = user_temp.name

        cloth_temp_path = cloth_temp.name

        print("Images saved")

        # Connect to official IDM-VTON Space

        hf_client = get_client()

        print("Sending images to IDM-VTON...")

        result = hf_client.predict(

            dict={

                "background": handle_file(
                    user_temp_path
                ),

                "layers": [],

                "composite": None

            },

            garm_img=handle_file(
                cloth_temp_path
            ),

            garment_des="upper body garment, shirt or top",

            is_checked=True,

            is_checked_crop=False,

            denoise_steps=30,

            seed=42,

            api_name="/tryon"

        )

        print("AI RESULT RECEIVED")

        print(result)

        # IDM-VTON returns result image as first item

        if not result:

            return jsonify({

                "success": False,

                "error": "No result returned from IDM-VTON"

            }), 500

        output_path = result[0]

        if not output_path or not os.path.exists(output_path):

            return jsonify({

                "success": False,

                "error": "Result image file not found"

            }), 500

        # Read output image

        with open(output_path, "rb") as f:

            image_base64 = base64.b64encode(

                f.read()

            ).decode("utf-8")

        return jsonify({

            "success": True,

            "image": (

                "data:image/png;base64,"

                + image_base64

            )

        })

    except Exception as e:

        print("ERROR OCCURRED")

        print(traceback.format_exc())

        # Reset client so next request reconnects

        client = None

        return jsonify({

            "success": False,

            "error": str(e),

            "trace": traceback.format_exc()

        }), 500

    finally:

        # Delete temporary files

        try:

            if user_temp_path and os.path.exists(
                user_temp_path
            ):

                os.remove(user_temp_path)

            if cloth_temp_path and os.path.exists(
                cloth_temp_path
            ):

                os.remove(cloth_temp_path)

        except Exception as cleanup_error:

            print(

                "Cleanup error:",

                cleanup_error

            )


if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=int(

            os.environ.get(

                "PORT",

                10000

            )

        )

    )
