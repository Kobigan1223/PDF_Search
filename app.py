from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from werkzeug.utils import secure_filename
from search_logic import search_in_folder

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'
app.config['PDF_FOLDER'] = 'Dataset'
app.config['SUMMARY_FOLDER'] = 'summary_files'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search', methods=['GET', 'POST'])
def search_page():
    if request.method == 'POST':
        word = request.form['word']
        exact_match = request.form.get('exact_match') == 'on'  # Check if checkbox is checked
        folder = app.config['PDF_FOLDER']

        if not os.path.exists(folder):
            return f"Folder {folder} does not exist."

        search_results = search_in_folder(folder, word, exact_match)

        for pdf_name, data in search_results.items():
            modified_pdf_path, _ = data
            new_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(modified_pdf_path))
            if os.path.exists(new_path):
                os.remove(new_path)
            os.rename(modified_pdf_path, new_path)
            search_results[pdf_name] = (os.path.basename(new_path), data[1])

        return render_template('search_results.html', word=word, search_results=search_results)

    return render_template('search_results.html', search_results=None, word=None)

@app.route('/static/<path:filename>')
def view_pdf(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/list_documents')
def list_documents():
    folder = app.config['PDF_FOLDER']
    if not os.path.exists(folder):
        return f"Folder {folder} does not exist."
    
    pdf_files = [f for f in os.listdir(folder) if f.lower().endswith('.pdf')]
    return render_template('list_documents.html', pdf_files=pdf_files)

@app.route('/delete_document/<filename>', methods=['POST'])
def delete_document(filename):
    folder = app.config['PDF_FOLDER']
    file_path = os.path.join(folder, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('list_documents'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['PDF_FOLDER'], filename))
            return redirect(url_for('list_documents'))
    return render_template('upload.html')

@app.route('/summary', methods=['GET', 'POST'])
def summary_page():
    show_summary = False
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        start_page = request.form['start_page']
        end_page = request.form['end_page']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['SUMMARY_FOLDER'], filename))
            # You can add your summary generation logic here
            print(f"How can I help with the PDF? Start Page: {start_page}, End Page: {end_page}")
            show_summary = True
    return render_template('summary.html', show_summary=show_summary)

if __name__ == '__main__':
    os.makedirs(app.config['SUMMARY_FOLDER'], exist_ok=True)
    app.run(debug=True)
