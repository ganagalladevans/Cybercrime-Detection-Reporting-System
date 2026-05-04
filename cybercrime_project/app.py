from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secretkey"

# ---------------- DATABASE SETUP ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT UNIQUE,
                    password TEXT
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS complaints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT,
                    type TEXT,
                    description TEXT,
                    risk TEXT,
                    status TEXT
                )''')

    conn.commit()
    conn.close()

init_db()

# ---------------- DETECTION LOGIC ----------------
def detect_threat(text):
    suspicious_words = ["bank", "otp", "password", "urgent", "click", "link"]
    for word in suspicious_words:
        if word in text.lower():
            return "High Risk"
    return "Low Risk"

# ---------------- HOME ----------------
@app.route('/')
def home():
    return redirect('/login')

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        try:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                      (name, email, password))
            conn.commit()
            conn.close()
            return redirect('/login')
        except:
            return "User already exists"

    return render_template('register.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session['user'] = user[1]

            # Simple admin check
            if email == "admin@gmail.com":
                session['admin'] = True
                return redirect('/admin')

            return redirect('/dashboard')
        else:
            return "Invalid login"

    return render_template('login.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- USER DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM complaints WHERE user=?", (session['user'],))
    complaints = c.fetchall()
    conn.close()

    return render_template('dashboard.html', complaints=complaints, user=session['user'])

# ---------------- ADD COMPLAINT ----------------
@app.route('/complaint', methods=['GET', 'POST'])
def complaint():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        type_ = request.form['type']
        description = request.form['description']

        risk = detect_threat(description)

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO complaints (user, type, description, risk, status) VALUES (?, ?, ?, ?, ?)",
                  (session['user'], type_, description, risk, "Pending"))
        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template('complaint.html')

# ---------------- ADMIN DASHBOARD ----------------
@app.route('/admin')
def admin():
    if 'admin' not in session:
        return redirect('/login')

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM complaints")
    complaints = c.fetchall()
    conn.close()

    return render_template('admin.html', complaints=complaints)

# ---------------- UPDATE STATUS ----------------
@app.route('/update/<int:id>/<status>')
def update(id, status):
    if 'admin' not in session:
        return redirect('/login')

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("UPDATE complaints SET status=? WHERE id=?", (status, id))
    conn.commit()
    conn.close()

    return redirect('/admin')

# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=10000)