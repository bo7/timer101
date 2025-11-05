# Database Schema - Zeit Erfassung System

## ER Diagram

```
┌─────────────────┐
│     USERS       │
├─────────────────┤
│ id (PK)         │
│ username        │
│ password_hash   │
│ email           │
│ is_admin        │
│ created_at      │
└────────┬────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────┐       N:1      ┌──────────────────┐
│   WORKTIMES     │◄────────────────┤   CUSTOMERS      │
├─────────────────┤                 ├──────────────────┤
│ id (PK)         │                 │ id (PK)          │
│ user_id (FK)    │                 │ name             │
│ customer_id (FK)│                 │ customer_number  │
│ location_id (FK)│                 │ active           │
│ description     │                 │ created_at       │
│ start_time      │                 └────────┬─────────┘
│ end_time        │                          │
│ break_minutes   │                          │ 1:N
│ worked_minutes  │                          │
│ processed       │                          ▼
│ created_at      │         ┌─────────────────────────┐
│ updated_at      │         │      LOCATIONS          │
└─────────────────┘    N:1  ├─────────────────────────┤
         │                  │ id (PK)                 │
         └─────────────────►│ customer_id (FK)        │
                            │ name                    │
                            │ address                 │
                            │ active                  │
                            │ created_at              │
                            └─────────────────────────┘
```

## Tables

### 1. USERS
Stores employee and admin user information.

| Column         | Type         | Constraints                    | Description                          |
|---------------|--------------|--------------------------------|--------------------------------------|
| id            | INTEGER      | PRIMARY KEY, AUTOINCREMENT     | Unique user identifier               |
| username      | VARCHAR(50)  | UNIQUE, NOT NULL              | Login username                       |
| password_hash | VARCHAR(255) | NOT NULL                      | Hashed password                      |
| email         | VARCHAR(100) | UNIQUE, NOT NULL              | User email                           |
| is_admin      | BOOLEAN      | DEFAULT FALSE                 | Admin flag                           |
| created_at    | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP     | Account creation timestamp           |

**Indexes:**
- `idx_users_username` on `username`
- `idx_users_email` on `email`

### 2. CUSTOMERS
Stores customer/client information.

| Column          | Type         | Constraints                    | Description                          |
|----------------|--------------|--------------------------------|--------------------------------------|
| id             | INTEGER      | PRIMARY KEY, AUTOINCREMENT     | Unique customer identifier           |
| name           | VARCHAR(200) | NOT NULL                      | Customer name                        |
| customer_number| VARCHAR(50)  | UNIQUE, NOT NULL              | Customer reference number            |
| active         | BOOLEAN      | DEFAULT TRUE                  | Active status                        |
| created_at     | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP     | Record creation timestamp            |

**Indexes:**
- `idx_customers_name` on `name` (for AJAX search)
- `idx_customers_number` on `customer_number`
- `idx_customers_active` on `active`

### 3. LOCATIONS
Stores work location information linked to customers.

| Column       | Type         | Constraints                    | Description                          |
|-------------|--------------|--------------------------------|--------------------------------------|
| id          | INTEGER      | PRIMARY KEY, AUTOINCREMENT     | Unique location identifier           |
| customer_id | INTEGER      | FOREIGN KEY (customers.id)     | Reference to customer                |
| name        | VARCHAR(200) | NOT NULL                      | Location name                        |
| address     | TEXT         |                               | Full address                         |
| active      | BOOLEAN      | DEFAULT TRUE                  | Active status                        |
| created_at  | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP     | Record creation timestamp            |

**Foreign Keys:**
- `customer_id` references `customers(id)` ON DELETE CASCADE

**Indexes:**
- `idx_locations_customer` on `customer_id`
- `idx_locations_active` on `active`

### 4. WORKTIMES
Stores time tracking entries.

| Column         | Type         | Constraints                    | Description                          |
|---------------|--------------|--------------------------------|--------------------------------------|
| id            | INTEGER      | PRIMARY KEY, AUTOINCREMENT     | Unique worktime identifier           |
| user_id       | INTEGER      | FOREIGN KEY (users.id)         | Employee who worked                  |
| customer_id   | INTEGER      | FOREIGN KEY (customers.id)     | Customer worked for                  |
| location_id   | INTEGER      | FOREIGN KEY (locations.id)     | Work location                        |
| description   | TEXT         |                               | Work description (Tätigkeit)         |
| start_time    | TIMESTAMP    | NOT NULL                      | Start datetime                       |
| end_time      | TIMESTAMP    | NOT NULL                      | End datetime                         |
| break_minutes | INTEGER      | DEFAULT 0                     | Break duration in minutes            |
| worked_minutes| INTEGER      | NOT NULL                      | Calculated: (end - start) - break    |
| processed     | BOOLEAN      | DEFAULT FALSE                 | If TRUE, entry is locked             |
| created_at    | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP     | Record creation timestamp            |
| updated_at    | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP     | Last update timestamp                |

**Foreign Keys:**
- `user_id` references `users(id)` ON DELETE CASCADE
- `customer_id` references `customers(id)` ON DELETE RESTRICT
- `location_id` references `locations(id)` ON DELETE RESTRICT

**Indexes:**
- `idx_worktimes_user` on `user_id`
- `idx_worktimes_customer` on `customer_id`
- `idx_worktimes_location` on `location_id`
- `idx_worktimes_start_time` on `start_time`
- `idx_worktimes_processed` on `processed`
- `idx_worktimes_user_date` on `user_id, start_time` (for daily queries)

**Check Constraints:**
- `end_time` must be greater than `start_time`
- `break_minutes` must be >= 0
- `worked_minutes` must be > 0

## Business Rules

1. **User Management**
   - Username and email must be unique
   - Passwords must be hashed (bcrypt/argon2)
   - Admin users can process time entries

2. **Customer & Location Management**
   - Each location must belong to exactly one customer
   - Inactive customers/locations should not appear in new entries
   - Deletion of customers/locations restricted if worktimes exist

3. **Worktime Entries**
   - `worked_minutes` is automatically calculated: (end_time - start_time in minutes) - break_minutes
   - Once `processed` = TRUE, entry cannot be modified
   - Start time must be before end time
   - Break time cannot exceed total time

4. **Data Integrity**
   - Foreign key constraints ensure referential integrity
   - Cascading deletes for users (delete all their worktimes)
   - Restricted deletes for customers/locations (prevent deletion if worktimes exist)

## Migration Path to PostgreSQL

When migrating from SQLite to PostgreSQL:
1. Change AUTOINCREMENT to SERIAL/BIGSERIAL
2. Update BOOLEAN type handling
3. Add proper TIMEZONE support (TIMESTAMPTZ)
4. Consider partitioning worktimes table by date
5. Add full-text search indexes for customer search
