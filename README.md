# MAD1 Vehicle Parking System

A multi-user application for managing 4-wheeler parking across different parking lots, spots, and vehicles. Includes administrator and user roles.

---

## 📁 Project Structure

```
vehicle-parking-system/
│
├── app.py
├── requirements.txt
├── README.md
│
├── /static
│   └── ... (static files: CSS, JS, images)
│
├── /templates
│   └── ... (HTML templates)
│
├── /application
│   ├── __init__.py
│   ├── models.py
│   ├── config.py
│   ├── controllers.py
│   └── database.py
│
└── ... (other modules/files)

```

---

## 🚀 Steps to Install & Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/alphaTejas/Vehicle-parking-system-management.git
   cd "MAD1 project"
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   ```

3. **Activate the virtual environment**
   - **Mac/Linux:**
     ```bash
     source .venv/bin/activate
     ```
   - **Windows (Command Prompt):**
     ```bash
     .venv\Scripts\activate
     ```
   - **Windows (PowerShell):**
     ```bash
     .\.venv\Scripts\Activate.ps1
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

---

## 🛠️ Technologies Used

- **Flask: Python web framework for backend logic.**
- **SQLAlchemy: ORM for managing database relationships and queries.**
- **Bootstrap: Frontend framework for styling and responsive design.**
- **SQLite: Database for data persistence.**
- **Jinja2: Templating engine for rendering HTML with dynamic data.**

---

## 📄 Notes

- Make sure to activate the virtual environment before running the app.
- All required Python packages are listed in `requirements.txt`.


---
