import sys, os, sqlite3, hashlib
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMessageBox,
    QTableWidgetItem, QHeaderView, QListWidgetItem
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.uic import loadUi

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
resource = lambda f: os.path.join(BASE_DIR, f)
DB_PATH  = resource("symptom_checker.db")

# ── Disease Knowledge Base ─────────────────────────────────────────────────────
DISEASE_DATA = {
    "flu_covid": {
        "name": "Flu / COVID-like Illness", "confidence": 90,
        "description": "Based on your symptoms — fever, cough, and fatigue — this presentation closely matches Seasonal Influenza or a COVID-like respiratory illness.",
        "transmission": "Highly contagious via respiratory droplets and close contact.",
        "duration": "Typical recovery: 7–14 days with rest and proper care.",
        "common_symptoms": "Fever, dry cough, fatigue, chills, headache, sore throat, body aches.",
        "doctor_warning": "Seek immediate care if you have difficulty breathing, persistent chest pain, or oxygen level drops below 94%.",
        "medications": [
            ("💊 Paracetamol 500–1000 mg", "Every 6–8 hrs for fever/pain • After food"),
            ("🧪 Vitamin C 500 mg", "Once daily • Immune support"),
            ("💧 ORS (Oral Rehydration Salts)", "As needed to stay hydrated"),
        ],
        "home_care": [
            "✅ Drink 8–10 glasses of water daily", "✅ Take complete bed rest",
            "✅ Eat light, warm foods (soups, porridge)", "✅ Gargle with warm salt water twice a day",
            "✅ Use steam inhalation for congestion", "✅ Monitor temperature every 4 hours",
            "🚫 Avoid cold drinks, heavy meals, and strenuous activity",
        ],
    },
    "viral_infection": {
        "name": "Viral Infection", "confidence": 80,
        "description": "Your symptoms suggest a common viral infection, likely affecting the upper respiratory tract. This is very common and usually self-limiting.",
        "transmission": "Spread through respiratory droplets and contaminated surfaces.",
        "duration": "Usually resolves in 5–10 days with symptomatic treatment.",
        "common_symptoms": "Fever, headache, body aches, mild cough, fatigue, runny nose.",
        "doctor_warning": "Visit a doctor if fever exceeds 39°C (102°F) for more than 3 days.",
        "medications": [
            ("💊 Paracetamol 500 mg", "Every 6 hrs for headache/fever • After food"),
            ("🧴 Antihistamine (e.g. Cetirizine)", "Once at night for runny nose"),
            ("🧃 Multivitamin supplement", "Once daily for immune support"),
        ],
        "home_care": [
            "✅ Rest and sleep at least 8–9 hours", "✅ Keep yourself warm and hydrated",
            "✅ Eat vitamin C-rich fruits (oranges, lemons)", "✅ Use nasal saline drops if nose is blocked",
            "✅ Avoid sharing utensils with family members", "🚫 Do not take antibiotics without prescription",
        ],
    },
    "throat_infection": {
        "name": "Throat Infection (Pharyngitis)", "confidence": 85,
        "description": "Your sore throat and cough symptoms indicate Pharyngitis or Tonsillitis — an inflammation of the throat, often caused by bacteria or viruses.",
        "transmission": "Spread through saliva, coughing, and sneezing.",
        "duration": "Bacterial: 7–10 days with antibiotics. Viral: resolves in 5–7 days.",
        "common_symptoms": "Sore throat, difficulty swallowing, cough, mild fever, red tonsils.",
        "doctor_warning": "See a doctor if throat pain is severe, you have white patches on tonsils, or trouble swallowing.",
        "medications": [
            ("🧴 Throat Lozenges (e.g. Strepsils)", "Dissolve in mouth every 2–3 hrs"),
            ("💊 Paracetamol 500 mg", "For pain/fever • After meals"),
            ("🥄 Cough Syrup (e.g. Benadryl)", "5 ml twice daily after meals"),
        ],
        "home_care": [
            "✅ Gargle with warm salt water 3× daily", "✅ Drink warm herbal tea with honey and lemon",
            "✅ Eat soft, non-spicy foods", "✅ Avoid speaking loudly to rest your throat",
            "✅ Use a humidifier to keep air moist", "🚫 Avoid cold drinks, ice cream, and spicy food",
        ],
    },
    "stress_dehydration": {
        "name": "Stress / Dehydration", "confidence": 75,
        "description": "Your symptoms of fatigue and headache are commonly linked to dehydration, sleep deprivation, or chronic stress. No serious illness detected.",
        "transmission": "Not contagious — lifestyle and environmental factors.",
        "duration": "Improves within 24–48 hours with hydration and rest.",
        "common_symptoms": "Headache, fatigue, low energy, dizziness, dry mouth, irritability.",
        "doctor_warning": "Consult a doctor if headaches are severe, recurring daily, or accompanied by vision changes.",
        "medications": [
            ("💧 ORS Sachets", "1–2 sachets in water • As needed"),
            ("💊 Paracetamol 500 mg", "For headache relief • With food"),
            ("🍋 Electrolyte drink (e.g. Glucon-D)", "Once daily"),
        ],
        "home_care": [
            "✅ Drink at least 2–3 litres of water daily", "✅ Sleep 7–9 hours every night",
            "✅ Take regular breaks from screens every 30 min", "✅ Practice deep breathing or meditation (5 min/day)",
            "✅ Eat balanced meals with fruits and vegetables", "🚫 Reduce caffeine and sugary drinks",
        ],
    },
    "gastro": {
        "name": "Gastroenteritis (Stomach Flu)", "confidence": 82,
        "description": "Your symptoms of nausea, vomiting, and/or diarrhea suggest Gastroenteritis — inflammation of the stomach and intestines, often caused by a viral or bacterial infection.",
        "transmission": "Food/water contamination, poor hygiene, contact with infected person.",
        "duration": "Usually 1–3 days. See a doctor if persisting beyond 5 days.",
        "common_symptoms": "Nausea, vomiting, diarrhea, stomach cramps, mild fever, weakness.",
        "doctor_warning": "Seek urgent care if you see blood in stool/vomit, cannot keep fluids down, or become severely dehydrated.",
        "medications": [
            ("💊 ORS Sachets", "After every loose stool • Critical for rehydration"),
            ("🧪 Domperidone 10 mg", "For nausea/vomiting • Before meals"),
            ("💊 Probiotics (e.g. Lactobacillus)", "Once daily to restore gut flora"),
        ],
        "home_care": [
            "✅ Start BRAT diet: Bananas, Rice, Applesauce, Toast", "✅ Sip water/ORS frequently in small amounts",
            "✅ Avoid dairy, fatty foods, and raw vegetables", "✅ Wash hands thoroughly before eating",
            "✅ Rest and avoid strenuous activity", "🚫 Avoid anti-diarrheal medication unless prescribed",
        ],
    },
    "anxiety_disorder": {
        "name": "Anxiety / Panic Disorder", "confidence": 72,
        "description": "Your reported symptoms of anxiety, dizziness, and chest tightness may indicate an anxiety or panic disorder — a very common and treatable mental health condition.",
        "transmission": "Not contagious — psychological and physiological in nature.",
        "duration": "Manageable with therapy, lifestyle changes, and if needed, medication.",
        "common_symptoms": "Excessive worry, restlessness, palpitations, shortness of breath, dizziness, chest tightness.",
        "doctor_warning": "Please consult a psychologist or psychiatrist if symptoms significantly affect your daily life.",
        "medications": [
            ("🌿 Chamomile/Herbal Tea", "Before bed to promote relaxation"),
            ("💊 Magnesium supplement", "Once daily — may reduce anxiety"),
            ("Note", "Prescription medication (e.g. SSRIs) only under doctor supervision"),
        ],
        "home_care": [
            "✅ Practice deep breathing: 4-7-8 technique", "✅ Daily 20–30 min of walking or light exercise",
            "✅ Maintain a consistent sleep schedule", "✅ Journaling or mindfulness practice",
            "✅ Talk to someone you trust", "🚫 Limit caffeine, alcohol, and social media before sleep",
        ],
    },
    "unknown": {
        "name": "Symptoms Unclear", "confidence": 40,
        "description": "The selected symptoms don't match a specific pattern in our database. This could be an early presentation of illness or a combination of minor issues.",
        "transmission": "Unknown — further evaluation required.",
        "duration": "Monitor symptoms for 24–48 hours.",
        "common_symptoms": "Varies — please consult a doctor for proper assessment.",
        "doctor_warning": "Please consult a doctor if symptoms persist for more than 2 days or worsen.",
        "medications": [("💊 Paracetamol 500 mg", "For general pain/fever management")],
        "home_care": [
            "✅ Rest and stay hydrated", "✅ Monitor your temperature",
            "✅ Note down all symptoms and their timeline", "✅ Consult a licensed physician",
        ],
    },
}

# ── Diagnosis logic ────────────────────────────────────────────────────────────
def diagnose(s: dict) -> str:
    g = s.get
    f, c, ft = g("fever"), g("cough"), g("fatigue")
    h, st    = g("headache"), g("sorethroat")
    n, v, d  = g("nausea"), g("vomiting"), g("diarrhea")
    cp, dz   = g("chestpain"), g("dizziness")
    sb, bp   = g("shortbreath"), g("bodypain")
    ax, ab   = g("anxiety"), g("abdominalpain")

    if f and c and (ft or bp):          return "flu_covid"
    if (n or v) and (d or ab):          return "gastro"
    if v and d:                         return "gastro"
    if st and (c or f):                 return "throat_infection"
    if f and (h or bp or dz):           return "viral_infection"
    if ax and (cp or dz or sb or h):    return "anxiety_disorder"
    if ft and h:                        return "stress_dehydration"
    if dz and h and not f:              return "stress_dehydration"
    return "unknown"

# ── Database ───────────────────────────────────────────────────────────────────
def get_connection():
    return sqlite3.connect(DB_PATH)

def _query(sql, params=(), fetchone=False, commit=False):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(sql, params)
    if commit:
        conn.commit(); conn.close(); return None
    result = cur.fetchone() if fetchone else cur.fetchall()
    conn.close()
    return result

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def init_db():
    conn = get_connection()
    cur  = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL, age INTEGER NOT NULL, gender TEXT NOT NULL,
            phone TEXT, username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, patient_name TEXT NOT NULL,
            age INTEGER, gender TEXT, condition TEXT NOT NULL,
            symptoms TEXT NOT NULL, checked_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS doctors_auth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE, password TEXT NOT NULL, full_name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS available_doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, specialization TEXT NOT NULL,
            contact TEXT, available TEXT NOT NULL DEFAULT 'Yes'
        );
        CREATE TABLE IF NOT EXISTS custom_symptoms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE, label TEXT NOT NULL
        );
    """)
    if cur.execute("SELECT COUNT(*) FROM doctors_auth").fetchone()[0] == 0:
        cur.execute("INSERT INTO doctors_auth (username,password,full_name) VALUES (?,?,?)",
                    ("doctor", hash_password("doctor123"), "Dr. Admin"))
    if cur.execute("SELECT COUNT(*) FROM available_doctors").fetchone()[0] == 0:
        cur.executemany("INSERT INTO available_doctors (name,specialization,contact,available) VALUES (?,?,?,?)", [
            ("Dr. Ayesha Khan",  "General Physician",           "0300-1111111", "Yes"),
            ("Dr. Bilal Ahmed",  "Pulmonologist",               "0311-2222222", "Yes"),
            ("Dr. Sara Malik",   "Gastroenterologist",          "0321-3333333", "Yes"),
            ("Dr. Usman Tariq",  "Psychiatrist / Psychologist", "0333-4444444", "No"),
        ])
    conn.commit(); conn.close()

# Auth helpers
def register_user(full_name, age, gender, phone, username, password):
    try:
        _query(
            "INSERT INTO users (full_name,age,gender,phone,username,password,created_at) VALUES (?,?,?,?,?,?,?)",
            (full_name, age, gender, phone, username, hash_password(password),
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")), commit=True
        )
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose another."

def login_user(username, password):
    row = _query("SELECT id,full_name,age,gender FROM users WHERE username=? AND password=?",
                 (username, hash_password(password)), fetchone=True)
    return {"id": row[0], "name": row[1], "age": row[2], "gender": row[3]} if row else None

def login_doctor(username, password):
    row = _query("SELECT id,full_name FROM doctors_auth WHERE username=? AND password=?",
                 (username, hash_password(password)), fetchone=True)
    return {"id": row[0], "name": row[1]} if row else None

# Record helpers
def save_record(user_id, patient_name, age, gender, condition_key, symptoms_list):
    _query(
        "INSERT INTO records (user_id,patient_name,age,gender,condition,symptoms,checked_at) VALUES (?,?,?,?,?,?,?)",
        (user_id, patient_name, age, gender, DISEASE_DATA[condition_key]["name"],
         ", ".join(symptoms_list), datetime.now().strftime("%Y-%m-%d %H:%M:%S")), commit=True
    )

def load_all_records_with_user():
    return _query(
        "SELECT r.id,r.patient_name,r.age,r.gender,r.condition,r.symptoms,r.checked_at,u.username "
        "FROM records r JOIN users u ON r.user_id=u.id ORDER BY r.checked_at DESC"
    )

def clear_all_records():
    _query("DELETE FROM records", commit=True)

# Symptom helpers
def load_custom_symptoms():
    return _query("SELECT key,label FROM custom_symptoms ORDER BY id")

def add_custom_symptom(key, label):
    try:
        _query("INSERT INTO custom_symptoms (key,label) VALUES (?,?)", (key, label), commit=True)
        return True, "Symptom added."
    except sqlite3.IntegrityError:
        return False, "Symptom key already exists."

def delete_custom_symptom(key):
    _query("DELETE FROM custom_symptoms WHERE key=?", (key,), commit=True)

# Doctor helpers
def load_available_doctors():
    return _query("SELECT id,name,specialization,contact,available FROM available_doctors ORDER BY id")

def add_or_update_doctor(doc_id, name, spec, contact, available):
    if doc_id:
        _query("UPDATE available_doctors SET name=?,specialization=?,contact=?,available=? WHERE id=?",
               (name, spec, contact, available, doc_id), commit=True)
    else:
        _query("INSERT INTO available_doctors (name,specialization,contact,available) VALUES (?,?,?,?)",
               (name, spec, contact, available), commit=True)

def delete_doctor(doc_id):
    _query("DELETE FROM available_doctors WHERE id=?", (doc_id,), commit=True)

# ── Shared UI helpers ──────────────────────────────────────────────────────────
def centered_item(text):
    item = QTableWidgetItem(str(text))
    item.setTextAlignment(Qt.AlignCenter)
    return item

def confirm(parent, title, msg):
    return QMessageBox.question(parent, title, msg,
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes

# ── Window Classes ─────────────────────────────────────────────────────────────
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi(resource("login.ui"), self)
        self.setWindowTitle("Smart Symptom Checker – Login")
        self.signinButton.clicked.connect(self.handle_login)
        self.registerButton.clicked.connect(self.open_register)
        self.doctorLoginButton.clicked.connect(self.open_doctor_login)
        self.passwordEdit.returnPressed.connect(self.handle_login)

    def handle_login(self):
        username, password = self.emailEdit.text().strip(), self.passwordEdit.text().strip()
        if not username or not password:
            self.statusLabel.setText("⚠ Please fill in all fields."); return
        user = login_user(username, password)
        if user:
            self.symptoms_win = SymptomsWindow(user); self.symptoms_win.show(); self.close()
        else:
            self.statusLabel.setText("✖ Invalid username or password. Please try again.")
            self.passwordEdit.clear()

    def open_register(self):
        self.reg_win = RegisterWindow(self); self.reg_win.show(); self.hide()

    def open_doctor_login(self):
        self.doc_login_win = DoctorLoginWindow(self); self.doc_login_win.show(); self.hide()


class DoctorLoginWindow(QMainWindow):
    def __init__(self, login_window):
        super().__init__()
        loadUi(resource("doctor_login.ui"), self)
        self.login_window = login_window
        self.setWindowTitle("Smart Symptom Checker – Doctor Login")
        self.loginButton.clicked.connect(self.handle_login)
        self.backButton.clicked.connect(self.go_back)
        self.passwordEdit.returnPressed.connect(self.handle_login)

    def handle_login(self):
        username, password = self.usernameEdit.text().strip(), self.passwordEdit.text().strip()
        if not username or not password:
            self.statusLabel.setText("⚠ Please fill in all fields."); return
        doctor = login_doctor(username, password)
        if doctor:
            self.dashboard = DoctorDashboard(doctor); self.dashboard.show(); self.close()
        else:
            self.statusLabel.setText("✖ Invalid doctor credentials.")
            self.passwordEdit.clear()

    def go_back(self):
        self.login_window.show(); self.close()


class RegisterWindow(QMainWindow):
    def __init__(self, login_window):
        super().__init__()
        loadUi(resource("register.ui"), self)
        self.login_window = login_window
        self.setWindowTitle("Smart Symptom Checker – Register")
        self.registerButton.clicked.connect(self.handle_register)
        self.backLoginButton.clicked.connect(self.go_back)

    def handle_register(self):
        full_name = self.nameEdit.text().strip()
        username  = self.usernameEdit.text().strip()
        password  = self.passwordEdit.text().strip()
        if not full_name or not username or not password:
            self.statusLabel.setText("⚠ Please fill in all required fields (marked *)."); return
        if len(password) < 6:
            self.statusLabel.setText("⚠ Password must be at least 6 characters long."); return
        ok, msg = register_user(full_name, self.ageSpinBox.value(),
                                self.genderCombo.currentText(),
                                self.phoneEdit.text().strip(), username, password)
        if ok:
            QMessageBox.information(self, "Success", f"✅ Account created for {full_name}!\nYou can now sign in.")
            self.go_back()
        else:
            self.statusLabel.setText(f"✖ {msg}")

    def go_back(self):
        self.login_window.show(); self.close()


# ── Doctor Dashboard ───────────────────────────────────────────────────────────
class DoctorDashboard(QMainWindow):
    def __init__(self, doctor):
        super().__init__()
        loadUi(resource("doctor_dashboard.ui"), self)
        self.doctor = doctor
        self.setWindowTitle("Smart Symptom Checker – Doctor Dashboard")
        self.doctorGreetLabel.setText(f"Welcome, {doctor['name']} 👋")

        hdr = self.recordsTable.horizontalHeader()
        for col, mode in [(0, QHeaderView.ResizeToContents), (1, QHeaderView.Stretch),
                          (2, QHeaderView.ResizeToContents), (3, QHeaderView.Stretch),
                          (4, QHeaderView.Stretch), (5, QHeaderView.ResizeToContents),
                          (6, QHeaderView.ResizeToContents)]:
            hdr.setSectionResizeMode(col, mode)

        self.load_records()
        self.searchRecordsEdit.textChanged.connect(lambda t: self.load_records(t))
        self.clearAllButton.clicked.connect(self.confirm_clear)
        self.manageSymptomsButton.clicked.connect(self.open_manage_symptoms)
        self.manageDoctorsButton.clicked.connect(self.open_manage_doctors)
        self.logoutButton.clicked.connect(self.logout)

    def load_records(self, filter_text=""):
        rows = load_all_records_with_user()
        today_str = datetime.now().strftime("%Y-%m-%d")
        self.totalCount.setText(str(len(rows)))
        self.todayCount.setText(str(sum(1 for r in rows if r[6].startswith(today_str))))
        if filter_text:
            rows = [r for r in rows if filter_text.lower() in r[1].lower()]
        self.recordsTable.setRowCount(0)
        empty = not rows
        self.emptyLabel.setVisible(empty)
        self.recordsTable.setVisible(not empty)
        for r in rows:
            i = self.recordsTable.rowCount()
            self.recordsTable.insertRow(i)
            age_gen = f"{r[2]} yrs / {r[3]}" if r[2] else str(r[3])
            for col, item in enumerate([
                centered_item(r[0]), QTableWidgetItem(r[1]),
                centered_item(age_gen), QTableWidgetItem(r[4]),
                QTableWidgetItem(r[5]), centered_item(r[6]), centered_item(r[7])
            ]):
                self.recordsTable.setItem(i, col, item)
        self.recordsTable.resizeRowsToContents()

    def confirm_clear(self):
        if confirm(self, "Confirm Delete",
                   "⚠ Are you sure you want to permanently delete ALL patient records?\nThis action cannot be undone."):
            clear_all_records(); self.load_records()
            QMessageBox.information(self, "Done", "All records have been cleared.")

    def open_manage_symptoms(self):
        self.symp_win = ManageSymptomsWindow(self); self.symp_win.show(); self.hide()

    def open_manage_doctors(self):
        self.doc_win = ManageDoctorsWindow(self); self.doc_win.show(); self.hide()

    def logout(self):
        self.login_win = LoginWindow(); self.login_win.show(); self.close()


class ManageSymptomsWindow(QMainWindow):
    BUILTIN = [
        ("fever","🌡️  Fever"), ("cough","😷  Cough"), ("fatigue","😴  Fatigue"),
        ("headache","🤕  Headache"), ("sorethroat","🤒  Sore Throat"),
        ("nausea","🤢  Nausea"), ("vomiting","🤮  Vomiting"),
        ("chestpain","💔  Chest Pain"), ("dizziness","😵  Dizziness"),
        ("abdominalpain","🤲  Abdominal Pain"), ("shortbreath","🫁  Shortness of Breath"),
        ("bodypain","🦴  Body Pain"), ("anxiety","😰  Anxiety"),
        ("rash","🔴  Skin Rash"), ("diarrhea","🚽  Diarrhea"),
    ]

    def __init__(self, dashboard):
        super().__init__()
        loadUi(resource("manage_symptoms.ui"), self)
        self.dashboard = dashboard
        self.setWindowTitle("Doctor Panel – Manage Symptoms")
        self.load_symptoms()
        self.addSymptomButton.clicked.connect(self.handle_add)
        self.deleteSymptomButton.clicked.connect(self.handle_delete)
        self.backButton.clicked.connect(self.go_back)

    def load_symptoms(self):
        self.symptomsList.clear()
        for key, label in self.BUILTIN:
            item = QListWidgetItem(f"[built-in] {label}  ({key})")
            item.setData(Qt.UserRole, None); item.setForeground(Qt.darkGray)
            self.symptomsList.addItem(item)
        for key, label in load_custom_symptoms():
            item = QListWidgetItem(f"[custom]   {label}  ({key})")
            item.setData(Qt.UserRole, key)
            self.symptomsList.addItem(item)

    def handle_add(self):
        key   = self.symptomKeyEdit.text().strip().lower().replace(" ", "")
        label = self.symptomLabelEdit.text().strip()
        if not key or not label:
            self.addStatusLabel.setText("⚠ Both key and label are required."); return
        ok, msg = add_custom_symptom(key, label)
        self.addStatusLabel.setStyleSheet(f"font-size:12px; color:{'#2e7d32' if ok else '#e53935'};")
        self.addStatusLabel.setText(f"{'✅' if ok else '✖'} {msg}")
        if ok:
            self.symptomKeyEdit.clear(); self.symptomLabelEdit.clear(); self.load_symptoms()

    def handle_delete(self):
        item = self.symptomsList.currentItem()
        if not item:
            QMessageBox.warning(self, "No Selection", "Please select a symptom to delete."); return
        key = item.data(Qt.UserRole)
        if key is None:
            QMessageBox.warning(self, "Cannot Delete", "Built-in symptoms cannot be deleted."); return
        if confirm(self, "Confirm", f"Delete symptom '{key}'?"):
            delete_custom_symptom(key); self.load_symptoms()

    def go_back(self):
        self.dashboard.show(); self.close()


class ManageDoctorsWindow(QMainWindow):
    def __init__(self, dashboard):
        super().__init__()
        loadUi(resource("manage_doctors.ui"), self)
        self.dashboard = dashboard
        self.setWindowTitle("Doctor Panel – Manage Doctors")
        hdr = self.doctorsTable.horizontalHeader()
        for col, mode in [(0, QHeaderView.ResizeToContents), (1, QHeaderView.Stretch),
                          (2, QHeaderView.Stretch), (3, QHeaderView.ResizeToContents),
                          (4, QHeaderView.ResizeToContents)]:
            hdr.setSectionResizeMode(col, mode)
        self.load_doctors()
        self.saveDocButton.clicked.connect(self.handle_save)
        self.editDocButton.clicked.connect(self.handle_load_edit)
        self.deleteDocButton.clicked.connect(self.handle_delete)
        self.backButton.clicked.connect(self.go_back)

    def load_doctors(self):
        self.doctorsTable.setRowCount(0)
        for r in load_available_doctors():
            i = self.doctorsTable.rowCount()
            self.doctorsTable.insertRow(i)
            self.doctorsTable.setItem(i, 0, centered_item(r[0]))
            self.doctorsTable.setItem(i, 1, QTableWidgetItem(r[1]))
            self.doctorsTable.setItem(i, 2, QTableWidgetItem(r[2]))
            self.doctorsTable.setItem(i, 3, centered_item(r[3] or "—"))
            self.doctorsTable.setItem(i, 4, centered_item(r[4]))
        self.doctorsTable.resizeRowsToContents()

    def handle_load_edit(self):
        row = self.doctorsTable.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a doctor row to edit."); return
        self.editIdEdit.setText(self.doctorsTable.item(row, 0).text())
        self.docNameEdit.setText(self.doctorsTable.item(row, 1).text())
        self.docSpecEdit.setText(self.doctorsTable.item(row, 2).text())
        contact = self.doctorsTable.item(row, 3).text()
        self.docContactEdit.setText("" if contact == "—" else contact)
        idx = self.docAvailableCombo.findText(self.doctorsTable.item(row, 4).text())
        if idx >= 0: self.docAvailableCombo.setCurrentIndex(idx)
        self.formTitle.setText("Edit Doctor")
        self.formStatusLabel.setStyleSheet("font-size:12px; color:#1565C0;")
        self.formStatusLabel.setText("📝 Loaded for editing. Make changes and click Save.")

    def handle_save(self):
        name, spec = self.docNameEdit.text().strip(), self.docSpecEdit.text().strip()
        contact    = self.docContactEdit.text().strip()
        avail      = self.docAvailableCombo.currentText()
        doc_id_str = self.editIdEdit.text().strip()
        doc_id     = int(doc_id_str) if doc_id_str else None
        if not name or not spec:
            self.formStatusLabel.setStyleSheet("font-size:12px; color:#e53935;")
            self.formStatusLabel.setText("⚠ Name and Specialization are required."); return
        add_or_update_doctor(doc_id, name, spec, contact, avail)
        self.load_doctors()
        for w in (self.docNameEdit, self.docSpecEdit, self.docContactEdit, self.editIdEdit):
            w.clear()
        self.formTitle.setText("Add / Edit Doctor")
        self.formStatusLabel.setStyleSheet("font-size:12px; color:#2e7d32;")
        self.formStatusLabel.setText(f"✅ Doctor {'updated' if doc_id else 'added'} successfully.")

    def handle_delete(self):
        row = self.doctorsTable.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a doctor to delete."); return
        doc_id = int(self.doctorsTable.item(row, 0).text())
        name   = self.doctorsTable.item(row, 1).text()
        if confirm(self, "Confirm Delete", f"Delete doctor '{name}'?"):
            delete_doctor(doc_id); self.load_doctors()

    def go_back(self):
        self.dashboard.show(); self.close()


# ── Patient Windows ────────────────────────────────────────────────────────────
class SymptomsWindow(QMainWindow):
    CHECKBOX_NAMES = [
        "fever", "cough", "fatigue", "headache", "sorethroat",
        "nausea", "vomiting", "chestpain", "dizziness",
        "abdominalpain", "shortbreath", "bodypain", "anxiety", "rash", "diarrhea"
    ]
    DISPLAY_NAMES = {
        "fever": "Fever", "cough": "Cough", "fatigue": "Fatigue",
        "headache": "Headache", "sorethroat": "Sore Throat",
        "nausea": "Nausea", "vomiting": "Vomiting", "chestpain": "Chest Pain",
        "dizziness": "Dizziness", "abdominalpain": "Abdominal Pain",
        "shortbreath": "Shortness of Breath", "bodypain": "Body Pain",
        "anxiety": "Anxiety", "rash": "Skin Rash", "diarrhea": "Diarrhea",
    }

    def __init__(self, user):
        super().__init__()
        loadUi(resource("symptoms.ui"), self)
        self.user = user
        self.setWindowTitle("Smart Symptom Checker – Select Symptoms")
        self.userGreetLabel.setText(f"Hello, {user['name'].split()[0]} 👋")
        self.patientNameDisplay.setText(f"👤  Patient: {user['name']}")
        self.dateLabel.setText(f"📅;  Date: {QDate.currentDate().toString('dd MMM yyyy')}")
        for name in self.CHECKBOX_NAMES:
            getattr(self, name).stateChanged.connect(self.update_count)
        self.predictButton.clicked.connect(self.handle_predict)
        self.clearButton.clicked.connect(self.clear_all)
        self.searchBar.textChanged.connect(self.filter_symptoms)
        self.logoutButton.clicked.connect(self.logout)

    def update_count(self):
        count = sum(1 for n in self.CHECKBOX_NAMES if getattr(self, n).isChecked())
        self.selectedCountLabel.setText(f"Selected: {count} symptom{'s' if count != 1 else ''}")

    def clear_all(self):
        for name in self.CHECKBOX_NAMES: getattr(self, name).setChecked(False)

    def filter_symptoms(self, text):
        text = text.lower()
        for name in self.CHECKBOX_NAMES:
            getattr(self, name).setVisible(not text or text in self.DISPLAY_NAMES[name].lower())

    def get_symptoms_dict(self):
        return {n: getattr(self, n).isChecked() for n in self.CHECKBOX_NAMES}

    def get_selected_list(self):
        return [self.DISPLAY_NAMES[n] for n in self.CHECKBOX_NAMES if getattr(self, n).isChecked()]

    def handle_predict(self):
        symptoms = self.get_symptoms_dict()
        if not any(symptoms.values()):
            QMessageBox.warning(self, "No Symptoms", "⚠ Please select at least one symptom before predicting.")
            return
        self.result_win = ResultWindow(self.user, symptoms, diagnose(symptoms), self.get_selected_list())
        self.result_win.show(); self.hide()

    def logout(self):
        if confirm(self, "Logout", "Are you sure you want to logout?"):
            self.login_win = LoginWindow(); self.login_win.show(); self.close()


class ResultWindow(QMainWindow):
    def __init__(self, user, symptoms, condition_key, selected_list):
        super().__init__()
        loadUi(resource("results.ui"), self)
        self.user, self.symptoms = user, symptoms
        self.condition_key, self.selected_list = condition_key, selected_list
        self.setWindowTitle("Smart Symptom Checker – Diagnosis Result")
        d = DISEASE_DATA[condition_key]
        self.diseaseName.setText(d["name"])
        self.matchLabel.setText(f"{d['confidence']}% Match")
        self.confidencePercent.setText(f"{d['confidence']}%")
        self.confidenceBar.setValue(d["confidence"])
        self.descriptionLabel.setText(d["description"])
        self.symptomsDetectedLabel.setText(f"Symptoms detected: {', '.join(selected_list)}")
        self.transmissionLabel.setText(f"🦠  Transmission\n{d['transmission']}")
        self.durationLabel.setText(f"⏱  Recovery Duration\n{d['duration']}")
        self.commonSymptomsLabel.setText(f"🤒  Common Symptoms\n{d['common_symptoms']}")
        self.warningLabel.setText(f"⚠️  When to See a Doctor\n{d['doctor_warning']}")
        self.treatmentButton.clicked.connect(self.open_treatment)
        self.saveRecordButton.clicked.connect(self.save_record)
        self.backMainButton.clicked.connect(self.go_back_main)

    def save_record(self):
        save_record(self.user["id"], self.user["name"], self.user["age"],
                    self.user["gender"], self.condition_key, self.selected_list)
        QMessageBox.information(self, "Saved", "✅ Patient record saved successfully!")
        self.saveRecordButton.setText("✔ Record Saved")
        self.saveRecordButton.setEnabled(False)

    def open_treatment(self):
        self.treatment_win = TreatmentWindow(self.user, self.condition_key, self)
        self.treatment_win.show(); self.hide()

    def go_back_main(self):
        self.symptoms_win = SymptomsWindow(self.user)
        self.symptoms_win.show(); self.close()


class TreatmentWindow(QMainWindow):
    def __init__(self, user, condition_key, result_win):
        super().__init__()
        loadUi(resource("treatment.ui"), self)
        self.user, self.condition_key, self.result_win = user, condition_key, result_win
        self.setWindowTitle("Smart Symptom Checker – Treatment Plan")
        d = DISEASE_DATA[condition_key]
        self.conditionName.setText(d["name"])
        self.patientTreatLabel.setText(f"Patient: {user['name']}")
        self.medicationsListLabel.setText(
            "\n\n".join(f"{i}. {med}\n   📝 {note}" for i, (med, note) in enumerate(d["medications"], 1))
            or "No specific medications required."
        )
        self.homeCareList.setText("\n".join(d["home_care"]))
        available = [doc for doc in load_available_doctors() if doc[4].lower() == "yes"]
        doc_text = (
            "👨‍⚕️ Available Doctors for Consultation:\n\n" +
            "".join(f"• {doc[1]}  —  {doc[2]}\n  📞 {doc[3] or 'Contact not listed'}\n\n" for doc in available)
        ) if available else "No doctors currently listed as available."
        self.warningBoxText.setText(
            "This is a preliminary assessment only. Always consult a licensed medical professional.\n\n"
            + doc_text
        )
        self.backMainButton.clicked.connect(self.go_back_main)
        self.checkAgainButton.clicked.connect(self.check_again)

    def go_back_main(self):
        self.result_win.show(); self.close()

    def check_again(self):
        self.new_symptoms = SymptomsWindow(self.user)
        self.new_symptoms.show(); self.close()


# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    init_db()
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QCheckBox { font-size:14px; padding:6px 4px; color:#333; spacing:8px; }
        QCheckBox::indicator { width:18px; height:18px; border:2px solid #B2DFDB;
            border-radius:4px; background:white; }
        QCheckBox::indicator:checked { background:#00796B; border:2px solid #00796B; }
        QToolTip { background:#00796B; color:white; border:none;
            font-size:12px; padding:4px 8px; border-radius:6px; }
    """)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()