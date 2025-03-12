from flask import Flask, render_template, request, jsonify, send_from_directory
import os

app = Flask(__name__)

# Directory for static files and uploads
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# # Serve static files
# @app.route("/static/<path:filename>")
# def static_files(filename):
#     return send_from_directory("app/static", filename)

@app.route("/")
def index():
    return render_template("item.html")

@app.route("/upload-chunk", methods=["POST"])
def upload_chunk():
    # Get form data and the file chunk
    file = request.files["chunkData"]
    file_name = request.form["fileName"]
    offset = int(request.form["offset"])
    file_size = int(request.form["fileSize"])

    file_path = os.path.join(UPLOAD_DIR, file_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Read the uploaded chunk
    chunk_data = file.read()

    # Open the file in binary mode and write the chunk at the correct position
    mode = "r+b" if os.path.exists(file_path) else "wb"
    with open(file_path, mode) as f:
        f.seek(offset)
        f.write(chunk_data)

    # Check if all chunks have been uploaded
    file_stat = os.stat(file_path)
    if file_stat.st_size == file_size:
        return jsonify({"message": "File upload complete"})

    return jsonify({"message": "Chunk uploaded successfully"})

if __name__ == "__main__":
    app.run(debug=True)
