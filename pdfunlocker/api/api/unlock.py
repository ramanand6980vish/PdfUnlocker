from flask import Flask, request, send_file, jsonify, send_from_directory
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import os

app = Flask(__name__, static_folder="../public", static_url_path="")

# ---------- FRONTEND ROUTES ----------
@app.route("/")
def index():
    """Serve main index.html"""
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:filename>")
def public_files(filename):
    """Serve static assets like CSS, JS"""
    return send_from_directory(app.static_folder, filename)

# ---------- BACKEND ROUTE ----------
@app.route("/api/unlock", methods=["POST"])
def unlock_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    password = request.form.get("password", "")

    try:
        reader = PdfReader(file)
    except Exception:
        return jsonify({"error": "Invalid or corrupted PDF"}), 400

    if reader.is_encrypted:
        try:
            result = reader.decrypt(password)
            if result == 0 or result is False:
                return jsonify({"error": "Wrong password"}), 401
        except Exception:
            return jsonify({"error": "Wrong password"}), 401

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    output = BytesIO()
    writer.write(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name=f"unlocked_{file.filename}",
        mimetype="application/pdf"
    )

# ---------- MAIN ----------
if __name__ == "__main__":
    app.run(debug=True)
