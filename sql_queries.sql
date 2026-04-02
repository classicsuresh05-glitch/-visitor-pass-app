-- ═══════════════════════════════════════════════════════════
--  VISITORPASS PRO — SQL QUERY REFERENCE
--  SQLite database: visitor_pass.db
--  All queries are also handled via SQLAlchemy ORM in app.py
-- ═══════════════════════════════════════════════════════════

-- ── TABLE SCHEMAS ─────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          VARCHAR(100)  NOT NULL,
    email         VARCHAR(150)  NOT NULL UNIQUE,
    password_hash VARCHAR(200)  NOT NULL,
    phone         VARCHAR(20),
    role          VARCHAR(20)   DEFAULT 'visitor',
    created_at    DATETIME      DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS packages (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         VARCHAR(100) NOT NULL,
    description  TEXT,
    price        REAL         NOT NULL,
    duration     VARCHAR(50),
    max_visitors INTEGER      DEFAULT 1,
    features     TEXT,
    is_active    BOOLEAN      DEFAULT 1
);

CREATE TABLE IF NOT EXISTS bookings (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    pass_code    VARCHAR(12)  NOT NULL UNIQUE,
    user_id      INTEGER      NOT NULL REFERENCES users(id),
    package_id   INTEGER      NOT NULL REFERENCES packages(id),
    visit_date   DATE         NOT NULL,
    num_visitors INTEGER      DEFAULT 1,
    purpose      VARCHAR(200),
    host_name    VARCHAR(100),
    status       VARCHAR(20)  DEFAULT 'pending',
    total_amount REAL,
    created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contacts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(150) NOT NULL,
    subject    VARCHAR(200),
    message    TEXT         NOT NULL,
    created_at DATETIME     DEFAULT CURRENT_TIMESTAMP,
    is_read    BOOLEAN      DEFAULT 0
);

-- ── INDEXES ───────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_bookings_user    ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status  ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_date    ON bookings(visit_date);
CREATE INDEX IF NOT EXISTS idx_bookings_pass    ON bookings(pass_code);

-- ── SAMPLE QUERIES ────────────────────────────────────────

-- 1. All bookings for a specific user (with package info)
SELECT b.pass_code, p.name AS package, b.visit_date,
       b.num_visitors, b.total_amount, b.status
FROM bookings b
JOIN packages p ON b.package_id = p.id
WHERE b.user_id = 1
ORDER BY b.created_at DESC;

-- 2. Dashboard stats
SELECT
    (SELECT COUNT(*) FROM users      WHERE role = 'visitor')   AS total_visitors,
    (SELECT COUNT(*) FROM bookings)                             AS total_bookings,
    (SELECT COUNT(*) FROM bookings   WHERE status = 'approved') AS approved_passes,
    (SELECT SUM(total_amount) FROM bookings)                    AS total_revenue;

-- 3. Verify a pass code
SELECT b.pass_code, b.status, b.visit_date,
       u.name AS visitor_name, p.name AS package_name
FROM bookings b
JOIN users    u ON b.user_id    = u.id
JOIN packages p ON b.package_id = p.id
WHERE b.pass_code = 'VP-XXXXXXXX';

-- 4. Admin: today's visitors
SELECT b.pass_code, u.name, u.phone, p.name AS package, b.num_visitors, b.status
FROM bookings b
JOIN users    u ON b.user_id    = u.id
JOIN packages p ON b.package_id = p.id
WHERE b.visit_date = DATE('now')
ORDER BY b.created_at;

-- 5. Monthly revenue report
SELECT strftime('%Y-%m', visit_date) AS month,
       COUNT(*)           AS total_bookings,
       SUM(total_amount)  AS revenue
FROM bookings
WHERE status = 'approved'
GROUP BY month
ORDER BY month DESC;

-- 6. Top packages by bookings
SELECT p.name, COUNT(b.id) AS booking_count,
       SUM(b.total_amount) AS revenue
FROM packages p
LEFT JOIN bookings b ON p.id = b.package_id
GROUP BY p.id
ORDER BY booking_count DESC;

-- 7. Expire old passes
UPDATE bookings
SET status = 'expired'
WHERE visit_date < DATE('now')
  AND status = 'approved';

-- 8. Search visitors by name or email
SELECT u.id, u.name, u.email, u.phone, u.created_at,
       COUNT(b.id) AS total_bookings
FROM users u
LEFT JOIN bookings b ON u.id = b.user_id
WHERE u.role = 'visitor'
  AND (u.name LIKE '%search_term%' OR u.email LIKE '%search_term%')
GROUP BY u.id;

-- 9. Unread contact messages
SELECT name, email, subject, message, created_at
FROM contacts
WHERE is_read = 0
ORDER BY created_at DESC;

-- 10. Upcoming bookings (next 7 days)
SELECT b.pass_code, u.name, u.phone,
       p.name AS package, b.visit_date, b.num_visitors
FROM bookings b
JOIN users    u ON b.user_id    = u.id
JOIN packages p ON b.package_id = p.id
WHERE b.visit_date BETWEEN DATE('now') AND DATE('now', '+7 days')
  AND b.status = 'approved'
ORDER BY b.visit_date;
