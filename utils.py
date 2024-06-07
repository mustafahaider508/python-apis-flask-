import os
from PyPDF2 import PdfReader
from docx import Document
import json

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'csv', 'pdf', 'docx'}

def count_characters_in_pdf(file_path):
    reader = PdfReader(file_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text() or ''
    return len(text)

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ''
    for page in reader.pages:
        text += page.extract_text() or ''
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text
    return text

def save_json(content, filename, json_folder):
    json_content = {'content': content}
    json_file_name = os.path.splitext(filename)[0] + '.json'
    json_file_path = os.path.join(json_folder, json_file_name)
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_content, json_file)
    return json_file_path
