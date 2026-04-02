# 🪪 VisitorPass Pro — Digital Visitor Pass System

A full-stack digital visitor management system built with **Flask + SQLAlchemy + SQLite**.

---

## 📁 Project Structure

```
visitor_pass/
├── app.py                  # Flask application + all routes + models
├── requirements.txt        # Python dependencies
├── sql_queries.sql         # Raw SQL reference queries
├── static/
│   ├── css/main.css        # Advanced CSS (dark luxury theme)
│   └── js/main.js          # Navbar, animations, interactions
└── templates/
    ├── base.html           # Base layout (nav + footer)
    ├── index.html          # Home page (hero, stats, how it works)
    ├── about.html          # About page (team, timeline, mission)
    ├── packages.html       # Pass packages + comparison table
    ├── booking.html        # Booking form with live summary
    ├── contact.html        # Contact form
    ├── login.html          # Login page
    ├── register.html       # Registration page
    ├── dashboard.html      # Visitor dashboard
    └── admin.html          # Admin dashboard
```

---

## 🚀 Setup Instructions

### 1. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
python app.py
```

### 4. Open in browser
```
http://localhost:5000
```

---

## 🔑 Default Credentials

| Role    | Email                     | Password  |
|---------|---------------------------|-----------|
| Admin   | admin@visitorpass.com     | admin123  |

---

## 📄 Pages

| Page         | URL             | Description                              |
|--------------|-----------------|------------------------------------------|
| Home         | `/`             | Hero, stats, how-it-works, features, CTA |
| About        | `/about`        | Mission, team, timeline                  |
| Packages     | `/packages`     | 4 pass types + comparison table + FAQs   |
| Booking      | `/booking`      | Book a pass with live price summary      |
| Contact      | `/contact`      | Contact form saved to DB                 |
| Login        | `/login`        | Email + password auth                    |
| Register     | `/register`     | New visitor registration                 |
| Dashboard    | `/dashboard`    | Visitor: view/manage own passes          |
| Admin        | `/admin`        | Admin: all bookings, stats, messages     |

---

## 🗄️ Database Models

- **User** — name, email, password hash, phone, role (visitor/admin)
- **Package** — name, price, duration, max_visitors, features
- **Booking** — pass_code (unique), user, package, visit_date, status, amount
- **Contact** — name, email, subject, message

---

## 🔌 API Endpoint

**POST** `/api/verify-pass`
```json
{ "pass_code": "VP-ABC12345" }
```
Response:
```json
{
  "valid": true,
  "status": "approved",
  "visitor": "Arjun Krishnan",
  "package": "Corporate Pass",
  "visit_date": "26 Mar 2024",
  "pass_code": "VP-ABC12345"
}
```

---

## 🎨 Design Theme

- **Style**: Dark luxury with electric teal + amber accents  
- **Fonts**: Syne (headings) + DM Sans (body)  
- **Features**: Animated hero, floating pass card, scroll counters, pass verification widget

---

## 🔧 To Upgrade to PostgreSQL/MySQL

Change the `SQLALCHEMY_DATABASE_URI` in `app.py`:
```python
# PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/visitor_pass'

# MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:pass@localhost/visitor_pass'
```
