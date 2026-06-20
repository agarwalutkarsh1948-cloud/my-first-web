from flask import Flask, request, jsonify, render_template, send_from_directory
import os, uuid, json
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit
app.config['DATA_FILE'] = 'notes_data.json'

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'txt', 'ppt', 'pptx'}

SUBJECT_COLORS = {
    'C Programming': ('icon-blue', 'ti-code'),
    'MySQL': ('icon-pink', 'ti-database'),
    'MATLAB': ('icon-amber', 'ti-chart-line'),
    'Data Structures': ('icon-green', 'ti-binary-tree'),
    'Operating Systems': ('icon-teal', 'ti-cpu'),
    'Discrete Maths': ('icon-purple', 'ti-math-function'),
    'Python': ('icon-blue', 'ti-brand-python'),
    'Other': ('icon-pink', 'ti-file'),
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_notes():
    if os.path.exists(app.config['DATA_FILE']):
        with open(app.config['DATA_FILE'], 'r') as f:
            return json.load(f)
    return []

def save_notes(notes):
    with open(app.config['DATA_FILE'], 'w') as f:
        json.dump(notes, f, indent=2)

@app.route('/')
def index():
    notes = load_notes()
    return render_template('index.html', notes=notes, subject_colors=SUBJECT_COLORS)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    title = request.form.get('title', '').strip()
    subject = request.form.get('subject', 'Other').strip()
    description = request.form.get('description', '').strip()
    uploader = request.form.get('uploader', 'Anonymous').strip()

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    # Save file with unique name
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    file.save(save_path)

    file_size = os.path.getsize(save_path)
    size_str = f"{file_size // 1024} KB" if file_size < 1024*1024 else f"{file_size // (1024*1024)} MB"

    note = {
        'id': uuid.uuid4().hex,
        'title': title or secure_filename(file.filename),
        'subject': subject,
        'description': description or f"Notes on {subject}",
        'uploader': uploader,
        'filename': unique_name,
        'original_name': file.filename,
        'ext': ext,
        'size': size_str,
        'uploaded_at': datetime.now().strftime('%d %b %Y, %I:%M %p'),
        'downloads': 0,
    }

    notes = load_notes()
    notes.insert(0, note)  # newest first
    save_notes(notes)

    colors = SUBJECT_COLORS.get(subject, SUBJECT_COLORS['Other'])
    note['icon_class'] = colors[0]
    note['icon_name'] = colors[1]

    return jsonify({'success': True, 'note': note})

@app.route('/download/<filename>')
def download_file(filename):
    # Increment download count
    notes = load_notes()
    for note in notes:
        if note['filename'] == filename:
            note['downloads'] = note.get('downloads', 0) + 1
            break
    save_notes(notes)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/api/notes')
def api_notes():
    subject = request.args.get('subject', '')
    notes = load_notes()
    if subject and subject != 'All':
        notes = [n for n in notes if n['subject'] == subject]
    return jsonify(notes)

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True, port=5000)
