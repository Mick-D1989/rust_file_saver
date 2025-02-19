from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import file_saver_rust
import os

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests for the frontend

BASE_DIRECTORY = os.path.abspath(".")
UPLOAD_FOLDER = "uploads"  # Base folder for saving files

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file_or_folder():
    # Handle folder uploads
    folder_path = request.form.get("folder_path")
    if folder_path:
        if not os.path.isdir(folder_path):
            return jsonify({"error": f"Provided folder path '{folder_path}' is not valid."}), 400

        files_to_save = []
        for root, _, files in os.walk(folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                with open(file_path, "rb") as f:
                    file_content = f.read()
                    files_to_save.append((file_name, file_content))

        try:
            file_saver_rust.save_files(UPLOAD_FOLDER, files_to_save)
            return jsonify({"message": f"Files from folder '{folder_path}' uploaded successfully!"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Handle file uploads
    if "files" not in request.files:
        return jsonify({"error": "No files provided"}), 400

    uploaded_files = request.files.getlist("files")
    files_to_save = []
    for file in uploaded_files:
        file_name = file.filename
        file_content = file.read()  # Keep content as bytes
        files_to_save.append((file_name, file_content))

    try:
        file_saver_rust.save_files(UPLOAD_FOLDER, files_to_save)
        return jsonify({"message": "Files uploaded successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
