# How to Run and Preview the Project

## 1. Clone or Download the Project

Ensure all files are in the correct structure:

```
project-root/
│
├── Assets/
├── backend/
│   └── listings.json
│   └── app.py 
├── index.html
├── styles.css
├── script.js
└── README.md
```

## 2. Set Up the Backend (Flask API)

### Step 1: Install Python Dependencies

```bash
pip install flask flask-cors
```

### Step 2: Run the Flask App

In the project root directory:

```bash
python app.py
```

The backend will run at:  
`http://127.0.0.1:5000/api/listings`

## 3. Preview the Frontend

### Step 1: Open `index.html`

Open the file directly in your browser:

```
project-root/index.html
```

> Use your browser’s developer tools (F12) and enable mobile view (toggle device toolbar) for the best experience.

### Step 2: Ensure Flask is Running

Make sure `app.py` is running in the terminal before using the site so that listing data can be fetched.

---

You're now ready to use the application.
