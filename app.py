from flask import Flask, request, jsonify, render_template, send_from_directory, session, redirect, url_for
import os, uuid, json
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'super-secret-noteshare-key'  # Needed for session management
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit
app.config['DATA_FILE'] = 'notes_data.json'
app.config['SETTINGS_FILE'] = 'settings.json'

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

DEFAULT_SETTINGS = {
    "site_title": "NoteShare",
    "site_tagline": "Collaborative Learning Platform",
    "hero_heading": "Knowledge Grows When Shared",
    "hero_sub": "Upload, discover, and download lecture notes effortlessly.",
    "footer_text": "© 2026 NoteShare.",
    "primary_color": "#e0217a",
    "allow_uploads": True,
    "show_downloads": True,
    "admin_password": "admin",
    "contact_name": "Admin",
    "contact_role": "Admin",
    "contact_email": "admin@example.com",
    "contact_phone": "",
    "contact_linkedin": ""
}

def load_settings():
    if os.path.exists(app.config['SETTINGS_FILE']):
        try:
            with open(app.config['SETTINGS_FILE'], 'r') as f:
                return json.load(f)
        except Exception:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()

def save_settings(s):
    with open(app.config['SETTINGS_FILE'], 'w') as f:
        json.dump(s, f, indent=2)

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
    s = load_settings()
    return render_template('index.html', notes=notes, subject_colors=SUBJECT_COLORS, s=s)

@app.route('/upload', methods=['POST'])
def upload_file():
    s = load_settings()
    if not s.get('allow_uploads', True):
        return jsonify({'error': 'Uploads are currently disabled by the admin.'}), 403

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
    notes.insert(0, note)
    save_notes(notes)

    colors = SUBJECT_COLORS.get(subject, SUBJECT_COLORS['Other'])
    note['icon_class'] = colors[0]
    note['icon_name'] = colors[1]

    return jsonify({'success': True, 'note': note})

@app.route('/download/<filename>')
def download_file(filename):
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

# ---------------------------------------------
# ADMIN ROUTES
# ---------------------------------------------

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        s = load_settings()
        if password == s.get('admin_password', 'admin'):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid password')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    notes = load_notes()
    s = load_settings()
    return render_template('admin.html', notes=notes, s=s)

@app.route('/admin/settings/save', methods=['POST'])
def admin_settings_save():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    s = load_settings()
    for key, value in data.items():
        if key == 'new_password':
            s['admin_password'] = value
        elif key != 'current_password':
            s[key] = value
    save_settings(s)
    return jsonify({'success': True})

@app.route('/admin/note/edit/<note_id>', methods=['POST'])
def admin_note_edit(note_id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.json
    notes = load_notes()
    found = False
    for note in notes:
        if note['id'] == note_id:
            note['title'] = data.get('title', note['title'])
            note['subject'] = data.get('subject', note['subject'])
            note['description'] = data.get('description', note['description'])
            note['uploader'] = data.get('uploader', note['uploader'])
            found = True
            break
            
    if found:
        save_notes(notes)
        return jsonify({'success': True})
    return jsonify({'error': 'Note not found'}), 404

@app.route('/admin/note/delete/<note_id>', methods=['POST'])
def admin_note_delete(note_id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
        
    notes = load_notes()
    new_notes = [n for n in notes if n['id'] != note_id]
    
    if len(new_notes) != len(notes):
        deleted_note = next(n for n in notes if n['id'] == note_id)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], deleted_note['filename'])
        if os.path.exists(file_path):
            os.remove(file_path)
        
        save_notes(new_notes)
        return jsonify({'success': True})
    return jsonify({'error': 'Note not found'}), 404

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True, port=5000)
