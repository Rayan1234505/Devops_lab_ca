"""Flask QR code generator web application."""

import io
import os
from base64 import b64encode

import qrcode
from flask import Flask, Response, render_template, request, send_file

MAX_DATA_LENGTH = int(os.getenv("QR_MAX_DATA_LENGTH", "1024"))

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
app.jinja_env.filters["b64encode"] = lambda value: b64encode(value).decode("ascii")


@app.get("/")
def index():
    return render_template("index.html", max_data_length=MAX_DATA_LENGTH)


@app.post("/generate")
def generate():
    data = request.form.get("data", "")
    if not data.strip():
        return render_template(
            "index.html",
            error="Please enter a URL or text to encode.",
            data=data,
            max_data_length=MAX_DATA_LENGTH,
        ), 400
    if len(data) > MAX_DATA_LENGTH:
        return render_template(
            "index.html",
            error=f"Input must be {MAX_DATA_LENGTH} characters or fewer.",
            data=data,
            max_data_length=MAX_DATA_LENGTH,
        ), 400

    image = qrcode.make(data)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return render_template(
        "index.html",
        data=data,
        qr_code=buffer.getvalue(),
        max_data_length=MAX_DATA_LENGTH,
    )


@app.post("/download")
def download():
    data = request.form.get("data", "")
    if not data.strip() or len(data) > MAX_DATA_LENGTH:
        return Response("Invalid QR data.", status=400, mimetype="text/plain")

    image = qrcode.make(data)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="image/png",
        as_attachment=True,
        download_name="qr-code.png",
    )


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.errorhandler(413)
def request_too_large(_error):
    return render_template(
        "error.html",
        error="The request is too large.",
    ), 413


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)  # noqa: S104
