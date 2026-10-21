from io import BytesIO

from PIL import Image

from app import MAX_DATA_LENGTH, app

client = app.test_client()
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert b"QR Code Generator" in response.data


def test_generate_text_qr():
    response = client.post("/generate", data={"data": "hello"})
    assert response.status_code == 200
    assert b"Your QR code" in response.data
    assert b"Download PNG" in response.data


def test_generate_url_qr():
    response = client.post("/generate", data={"data": "https://example.com"})
    assert response.status_code == 200
    assert b"data:image/png;base64," in response.data


def test_generated_image_is_valid_png():
    response = client.post("/download", data={"data": "hello"})
    assert response.status_code == 200
    assert response.data.startswith(PNG_MAGIC)
    image = Image.open(BytesIO(response.data))
    assert image.format == "PNG"


def test_download_headers():
    response = client.post("/download", data={"data": "download me"})
    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert "attachment" in response.headers["Content-Disposition"]
    assert "qr-code.png" in response.headers["Content-Disposition"]


def test_empty_and_whitespace_input_rejected():
    for value in ("", "   \t\n"):
        response = client.post("/generate", data={"data": value})
        assert response.status_code == 400
        assert b"Please enter" in response.data


def test_excessively_long_input_rejected():
    response = client.post("/generate", data={"data": "x" * (MAX_DATA_LENGTH + 1)})
    assert response.status_code == 400
    assert b"characters or fewer" in response.data


def test_invalid_download_rejected():
    response = client.post("/download", data={"data": " "})
    assert response.status_code == 400


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}
