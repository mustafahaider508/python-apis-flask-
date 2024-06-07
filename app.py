from flask import Flask, request, jsonify,send_from_directory
from flask_cors import CORS
import os
import json
from utils import allowed_file, count_characters_in_pdf, extract_text_from_pdf, extract_text_from_docx

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])  # Enable CORS for localhost:3000

UPLOAD_FOLDER = 'uploads'
JSON_FOLDER = 'jsonfiles'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(JSON_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['JSON_FOLDER'] = JSON_FOLDER

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'success': False, 'message': 'No files part in the request'}), 400
    
    files = request.files.getlist('files')
    
    if len(files) == 0:
        return jsonify({'success': False, 'message': 'No files selected for uploading'}), 400

    responses = []
    total_character_count = 0
    
    for file in files:
        if file and allowed_file(file.filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Count characters and extract content
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            if file_extension in {'txt', 'csv'}:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    character_count = len(content)
            elif file_extension == 'pdf':
                content = extract_text_from_pdf(file_path)
                character_count = count_characters_in_pdf(file_path)
            elif file_extension == 'docx':
                content = extract_text_from_docx(file_path)
                character_count = len(content)
            else:
                character_count = 'N/A'
                content = None

            json_content = {'content': content}
            json_file_name = os.path.splitext(file.filename)[0] + '.json'
            json_file_path = os.path.join(app.config['JSON_FOLDER'], json_file_name)
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_content, json_file)

            if content is not None:
                total_character_count += character_count

            responses.append({
                'file_name': file.filename,
                'file_path': file_path,
                'character_count': character_count,
                'json_file_path': json_file_path,
                'json_content': json_content  # This ensures the content is included as JSON, not a string
            })
        else:
            responses.append({
                'file_name': file.filename,
                'message': 'File type not allowed'
            })

    return jsonify({
        'success': True,
        'message': 'Files uploaded and processed successfully',
        'total_character_count': total_character_count,
        'files': responses
    }), 200

@app.route('/hello', methods=['GET'])
def hello_world():
    return jsonify({'message': 'Hello, World!'})

# Serve static files from the JSON_FOLDER
@app.route('/jsonfiles/<filename>', methods=['GET'])
def serve_json_file(filename):
    return send_from_directory(app.config['JSON_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
