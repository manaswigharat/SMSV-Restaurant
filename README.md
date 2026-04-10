## Reservation and Scheduling Management System for SMSV Restaurant 🍽️
A web-based restaurant reservation system built using Flask and SQLite that enables real-time table booking, admin-side reservation management, and intelligent table allocation.

🚀 Live Demo:
https://smsv-restaurant-3.onrender.com/

## 🔥 Key Features
- Real-time table booking system
- Admin dashboard for managing reservations
- Prevention of double bookings
- Efficient scheduling of tables
- User-friendly interface

## 🧠 Algorithms Used
- Priority Scheduling: Handles booking requests based on priority
- Greedy Allocation: Assigns best-fit available table quickly
- Backtracking: Reassigns tables efficiently after cancellations

## 🛠 Tech Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Flask (Python)
- Database: SQLite
- Deployment: Render

## 📊 System Workflow
1. User visits website
2. Selects preferred time slot
3. Enters booking details
4. Reservation stored in database
5. Confirmation displayed

## 📈 Project Impact
- Reduced chances of manual booking errors
- Eliminated double booking issues
- Improved table utilization using algorithm-based allocation

## 📁 Project Structure
```bash
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
## 📄 Pages

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Hero banner, menu, gallery, contact |
| Book Table | `/book` | Booking form with type selection |
| Confirmation | `/confirmation/<id>` | Booking details & cancel option |
| Admin Login | `/admin/login` | Secure admin authentication |
| Dashboard | `/admin/dashboard` | Stats, bookings, table management |
| Queue | `/admin/queue` | Priority-sorted booking queue |
| Allocation | `/admin/allocate` | Run greedy algorithm |
| Cancellation | `/admin/cancellation` | Cancel & backtrack replacement |

## ⚙️ Installation & Setup
```bash
git clone https://github.com/Sahas-2417/Reservation_Scheduling_Management_System_for_SMSV_Restaurant.git
cd Reservation_Scheduling_Management_System_for_SMSV_Restaurant
pip install -r requirements.txt
python app.py
```
