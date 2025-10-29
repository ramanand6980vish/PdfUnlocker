
import os
from io import BytesIO
from flask import Flask, request, send_file, jsonify, send_from_directory
from PyPDF2 import PdfReader, PdfWriter

# Flask app instance
app = Flask(__name__)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")

# ---------- FRONTEND ROUTES ----------

@app.route("/")
def index():
    """Serve the main UI page"""
    return send_from_directory(PUBLIC_DIR, "index.html")

@app.route("/<path:filename>")
def public_files(filename):
    """Serve static frontend files (CSS, JS, etc.)"""
    return send_from_directory(PUBLIC_DIR, filename)

# ---------- BACKEND ROUTE ----------

@app.route("/api/unlock", methods=["POST"])
def unlock_pdf():
    if "file" not in request.files:
        return jsonify({"error": "no file uploaded"}), 400

    file = request.files["file"]
    password = request.form.get("password", "")

    in_bytes = file.read()
    if not in_bytes:
        return jsonify({"error": "empty file"}), 400

    try:
        reader = PdfReader(BytesIO(in_bytes))
    except Exception:
        return jsonify({"error": "invalid pdf"}), 400

    if reader.is_encrypted:
        try:
            res = reader.decrypt(password)
            if res in (0, False):
                return jsonify({"error": "wrong password"}), 401
        except Exception:
            return jsonify({"error": "wrong password"}), 401

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    out_io = BytesIO()
    writer.write(out_io)
    out_io.seek(0)

    return send_file(
        out_io,
        as_attachment=True,
        download_name=f"unprotected_{file.filename}",
        mimetype="application/pdf"
    )

# ---------- MAIN ENTRY ----------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
