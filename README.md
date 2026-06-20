# 📚 NoteShare — Collaborative Learning Platform

Made with ❤️ by Utkarsh, Sachin, Rohit & Naitik

---

## 🚀 Setup & Run (Step by Step)

### Step 1 — Install Python
Make sure Python 3.8+ is installed.
Download from: https://python.org

### Step 2 — Install dependencies
Open terminal in this folder and run:
```
pip install -r requirements.txt
```

### Step 3 — Run the app
```
python app.py
```

### Step 4 — Open in browser
Go to: http://localhost:5000

---

## 📁 Project Structure
```
noteshare/
├── app.py              ← Flask backend (main server)
├── requirements.txt    ← Python dependencies
├── notes_data.json     ← Auto-created, stores all note metadata
├── uploads/            ← Auto-created, stores uploaded files
└── templates/
    └── index.html      ← Frontend (HTML + CSS + JS)
```

---

## ✅ Features
- Upload any file (PDF, images, Word, PPT, TXT)
- Files saved to `/uploads` folder on server
- Note metadata saved to `notes_data.json`
- Homepage shows all uploaded notes
- Filter by subject (C, MySQL, MATLAB, DSA, etc.)
- Search by title or description
- Download any note
- Download counter per note
- Drag & drop upload support
- Fully responsive UI

---

## 🛠 Tech Stack
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python + Flask
- **Database**: JSON file (notes_data.json)
- **Storage**: Local /uploads folder
