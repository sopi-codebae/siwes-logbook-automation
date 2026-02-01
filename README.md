# SIWES Logbook Automation System

A comprehensive, offline-first digital logbook system designed to automate the Student Industrial Work Experience Scheme (SIWES). Built with **FastHTML**, **Python**, and **PostgreSQL**, this system bridges the gap between students in the field and supervisors at the institution.

## 🚀 Key Features

*   **Offline-First Architecture**: Students can create logs without an internet connection. Data is stored locally (IndexedDB) and automatically synced when back online.
*   **Geolocation Verification**: Every log entry captures GPS coordinates to ensure students are physically present at their placement location.
*   **Geofencing**: Supervisors can define valid work zones; logs created outside these zones are flagged.
*   **Role-Based Access**: Specialized dashboards for Students and Institutional Supervisors.
*   **Interactive Logbook**: Weekly view of activities with status indicators (Verified, Pending, Flagged).

---

## 🛠️ Setup Guide

Follow these steps to set up the development environment from scratch.

### 1. Prerequisites (Download & Install)

*   **Python (v3.10+)**: [Download Here](https://www.python.org/downloads/)
    *   *Important*: Check "Add Python to PATH" during installation.
*   **PostgreSQL (Database)**: [Download Here](https://www.postgresql.org/download/)
    *   Remember the password you set for the `postgres` user.
*   **VS Code (Editor)**: [Download Here](https://code.visualstudio.com/download)

### 2. Configure Database

1.  Open **pgAdmin 4** (installed with PostgreSQL) or a terminal.
2.  Create a new database named `siwes_db`.

### 3. Project Setup

1.  **Clone/Download** this repository.
2.  Open the folder in **VS Code**.
3.  Open a Terminal in VS Code (`Ctrl + ~`).

### 4. Create Virtual Environment

Isolate dependencies by creating a virtual environment:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Environment Configuration

1.  Create a file named `.env` in the root directory.
2.  Add your database credentials:

```ini
# .env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/siwes_db
SECRET_KEY=your-super-secret-key-change-this
DEBUG=True
```

### 7. Initialize Database

Run the provided script to create tables and seed test data:

```bash
python reset_db.py
```
*This creates a Supervisor (`supervisor@example.com`) and a Student (`student@example.com`) with the password `password`.*

### 8. Run the Application

```bash
python main.py
```
Visit `http://localhost:5001` in your browser.

---

## 📸 Screenshots

### Login Screen
![Login Screen](docs/screenshots/login.png)
*(Place screenshot here)*

### Student Dashboard
![Student Dashboard](docs/screenshots/student_dashboard.png)
*(Place screenshot here)*

### Daily Logbook & Offline Mode
![Logbook Interface](docs/screenshots/logbook.png)
*(Place screenshot here)*

### Supervisor Dashboard
![Supervisor Dashboard](docs/screenshots/supervisor_dashboard.png)
*(Place screenshot here)*

---

## 📋 Project Status

### ✅ Completed
*   **Core Architecture**: FastHTML setup, Database models (User, Student, Supervisor, Log, Placement).
*   **Authentication**: Login/Logout flow with role-based redirection.
*   **Database**: SQLAlchemy ORM with async support via middleware.
*   **Student Logbook UI**:
    *   Weekly view card implementation.
    *   Real-time filtering (This Week, Pending, All).
    *   Modal-based log entry form.
*   **Offline Capability**:
    *   IndexedDB integration for local storage.
    *   Background synchronization queue.
    *   Status indicators (Online/Offline).
*   **Geolocation**:
    *   GPS capture on log creation.
    *   Geofence validation logic.

### 🚧 In Progress
*   **Supervisor Dashboard**:
    *   Student list view.
    *   Map view for geofencing.
*   **Communication Module**:
    *   Chat interface between student and supervisor.

### 📝 To Do
*   **Advanced Analytics**: Charts for student hours and performance.
*   **Push Notifications**: Alerting supervisors of new flagged logs.
*   **Reporting**: PDF export of logbooks for final submission.
*   **Admin Panel**: For managing school configuration and bulk uploads.

---

## 🧪 Testing

To run the test suite:

```bash
# Validate database connection
python seed_db.py
```

## 🐛 Known Issues / Notes
*   Ensure Location Services are enabled in your browser for GPS features to work.
*   The system is optimized for mobile view (PWA) but works fully on desktop.
