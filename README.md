# 🍛 SMSV Restaurant – Smart Priority Based Booking System

A **full-stack restaurant reservation platform** that demonstrates **Operating System concepts** and **Algorithm Design (AOA)** in a real-world application. Built as a college capstone project.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-Database-orange?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🌟 Features

- **Customer Interface** – Book tables with VIP, Pre-Booking, or On-Spot reservations
- **Admin Dashboard** – Manage bookings, tables, and view statistics
- **Priority Scheduling (OS Concept)** – VIP gets highest priority, On-Spot gets lowest
- **Greedy Table Allocation (AOA)** – Assigns the smallest available table that fits the group
- **Backtracking Cancellation (AOA)** – Automatically finds replacement bookings on cancellation
- **Queue Management** – Priority-sorted booking queue
- **Indian Restaurant UI** – Premium dark theme with gold/saffron accents

---

## 🔬 Algorithms Implemented

### 1. Priority Scheduling (OS Concept)
| Booking Type | Priority Level | Time Limit |
|---|---|---|
| VIP | P1 (Highest) | Unlimited |
| Pre-Booking | P2 (Medium) | 2 Hours |
| On-Spot | P3 (Lowest) | 1 Hour |

### 2. Greedy Algorithm – Table Allocation
- Sorts waiting bookings by priority
- For each booking, assigns the **smallest available table** that fits the group
- Minimizes resource waste (greedy choice property)

### 3. Backtracking Algorithm – Cancellation Replacement
- When a booking is cancelled, recursively searches the waiting queue
- Checks constraints: table capacity, date match, time compatibility
- Assigns the freed table to the first valid replacement
- Notifies the upgraded customer

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python Flask |
| Database | SQLite |
| Fonts | Google Fonts (Playfair Display, Inter) |
| Icons | Font Awesome 6 |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.x installed

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/SMSV-Restaurant.git
cd SMSV-Restaurant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python app.py

# 4. Open in browser
# http://127.0.0.1:5000
```

### Admin Login
- **Username:** `admin`
- **Password:** `admin123`

---

## 📁 Project Structure

```
SMSV-Restaurant/
├── app.py              # Flask application (routes)
├── database.py         # SQLite setup & initialization
├── models.py           # Data operations & CRUD
├── services.py         # Algorithms (Greedy + Backtracking)
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
├── .gitignore          # Git ignore rules
├── templates/
│   ├── base.html           # Base layout template
│   ├── index.html          # Homepage
│   ├── book.html           # Booking form
│   ├── confirmation.html   # Booking confirmation
│   ├── admin_login.html    # Admin login
│   ├── dashboard.html      # Admin dashboard
│   ├── queue.html          # Priority queue view
│   ├── allocation.html     # Greedy allocation page
│   └── cancellation.html   # Backtracking cancellation
└── static/
    ├── css/style.css       # Premium Indian theme CSS
    └── images/             # Logo, hero, gallery images
```

---

## 📸 Screenshots

### Homepage
The landing page features a hero banner, Indian cuisine gallery, and reservation options.

### Booking Form
Customers select their booking type (VIP, Pre-Booking, On-Spot), date, and time.

### Admin Dashboard
Real-time statistics, booking management, and table administration.

---

## 📄 Pages

| Page | URL | Description |
|---|---|---|
| Home | `/` | Hero banner, menu, gallery, contact |
| Book Table | `/book` | Booking form with type selection |
| Confirmation | `/confirmation/<id>` | Booking details & cancel option |
| Admin Login | `/admin/login` | Secure admin authentication |
| Dashboard | `/admin/dashboard` | Stats, bookings, table management |
| Queue | `/admin/queue` | Priority-sorted booking queue |
| Allocation | `/admin/allocate` | Run greedy algorithm |
| Cancellation | `/admin/cancellation` | Cancel & backtrack replacement |

---

## 👥 Team

**SMSV Restaurant** – College Capstone Project

---

## 📜 License

This project is for educational purposes as part of a college capstone demonstration.
