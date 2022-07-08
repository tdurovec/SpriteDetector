from flask import Flask
from flask import redirect
from flask import url_for
from flask import render_template
from flask import request
from flask import jsonify
from flask import send_file

from alg import SpriteSlicer

from base64 import b64decode
from io import BytesIO
from zipfile import ZipFile
from PIL import Image


app = Flask(__name__)
app.secret_key = "secret key"

image_folder = None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/detection", methods=["POST"])
def detection():
    """
    take the settings from the frontend and 
    run the detection algorithm, send the 
    detected coordinates and a transparent 
    background image(base64) via
    json to the frontend
    :exception POST
    :return: List, String
    """
    context = {}

    if request.method == "POST":
        data = request.get_json()

        # data:image/png;base64, get rid of theese on start
        image = data["image"].split(",")[1]
        scale_percent = data["scale-percent"]
        toleranci = data["toleranci"]
        distance = data["distance"]
        char = data["char"]
        transparent_bg = data["transparent-bg"]

        coords, img_trans_bg = SpriteSlicer(
            image, scale_percent, distance, toleranci, char
        ).init()

        context = {"coords": coords}

        if transparent_bg:
            context["new_image"] = str(img_trans_bg.decode("utf-8"))

        return jsonify(context)

    return redirect(url_for("home"))


@app.route("/cut-image", methods=["POST"])
def image_cut():
    """
    take the image and coordinates from 
    the frontend and then cut the image
    according to the coordinates and put
    it in a zip folder
    :exception POST
    :return: None
    """
    global image_folder

    if request.method == "POST":
        data = request.get_json()

        # data:image/png;base64, get rid of theese on start
        image = data["image"].split(",")[1]
        coords = data["coords"]

        byte_data = b64decode(image)
        image_data = BytesIO(byte_data)
        image = Image.open(image_data)

        cropped_imgs = []

        for coord in coords:
            x = coord[0]
            y = coord[1]
            w = coord[2]
            h = coord[3]
            crop = image.crop((x, y, w + x, h + y))
            cropped_imgs.append(crop)

        img_count = 0
        image_folder = BytesIO()
        with ZipFile(image_folder, "w") as zf:
            for img in cropped_imgs:

                file_obj = BytesIO()
                img.save(file_obj, "PNG")
                img.close()

                image = file_obj.getvalue()

                zf.writestr("sprite_{}.png".format(img_count), image)
                img_count += 1

        image_folder.seek(0)

        return jsonify()

    return redirect(url_for("home"))


@app.route("/download", methods=["POST"])
def download():
    '''
    send zip folder file user can download it
    :exception POST
    :return: BytesIO object
    '''
    global image_folder

    if image_folder is not None:
        return send_file(
            image_folder, as_attachment=True, attachment_filename="Sprites.zip"
        )

    return redirect(url_for("home"))


@app.errorhandler(404)
def not_found(error):
    return redirect(url_for("home"))
