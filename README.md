# Vehicle-parking-system

It is a multi-user web app (one requires an administrator and other users) that manages 4-Wheeler parking for different parking lots, parking spots and parked vehicles.

---

##  Technologies Used

- **Flask** – Python web framework for backend logic.
- **SQLAlchemy** – ORM for managing database relationships and queries.
- **Bootstrap** – Frontend framework for styling and responsive design.
- **SQLite** – Database for data persistence.
- **Jinja2** – Templating engine for rendering HTML with dynamic data.

## Steps to Run `app.py`


# 1. Create a virtual environment
python3 -m venv .venv

# 2. Activate the virtual environment
# For Linux / Mac
source .venv/bin/activate

# For Windows (Command Prompt)
.venv\Scripts\activate

# For Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# 3. Install the dependencies from requirements.txt
pip install -r requirements.txt

# 4. Run the application
python app.py
