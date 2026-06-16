# CineBook - Movie Ticket Booking System

A modern web application for booking movie tickets using Flask and MySQL. Built as a DBMS learning project with proper database normalization and foreign key relationships.

## Features

- 🎬 Browse available movies
- 👤 User authentication (register/login)
- 🎫 Real-time seat booking with availability tracking
- 💾 Persistent data storage with MySQL
- 📱 Responsive, modern UI
- 🔒 Session-based user management

## Technology Stack

- **Frontend**: HTML5, CSS3 (modern responsive design)
- **Backend**: Flask (Python web framework)
- **Database**: MySQL (with normalized schema)
- **Architecture**: MVC pattern with proper data relationships

## Database Schema

### Tables
- **users**: User accounts and authentication
- **movies**: Movie catalog with metadata
- **seats**: Individual seats for each movie
- **bookings**: User bookings linking users, movies, and seats

### Key Features
- Foreign key relationships for data integrity
- Unique constraints on username and seat-movie combinations
- Automatic timestamps for audit trails

## Prerequisites

- Python 3.7+
- MySQL Server running locally
- pip (Python package manager)

## Setup Instructions

### 1. Create MySQL Database

```sql
CREATE DATABASE bms;
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables (PowerShell)

```powershell
$env:MYSQL_HOST = "localhost"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "root"
$env:MYSQL_DB = "bms"
```

### 4. Initialize Database with Sample Data

```bash
python setup.py
```

This will:
- Create all required tables
- Add 5 sample movies
- Generate 64 seats per movie (8×8 grid)

### 5. Run the Application

```bash
python app.py
```

The app will be available at: `http://127.0.0.1:5000`

## Usage

1. **Home Page**: Browse available movies
2. **Register**: Create a new account (username and optional email)
3. **Login**: Sign in with your credentials
4. **Book Seats**: Select a movie and available seats
5. **Confirmation**: Receive booking confirmation
6. **Logout**: End your session

## Project Structure

```
bms_clone/
├── app.py                 # Main Flask application
├── setup.py              # Database initialization script
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── static/
│   └── style.css        # Modern responsive styling
└── templates/
    ├── index.html       # Home page with movie list
    ├── login.html       # User login page
    ├── register.html    # User registration page
    ├── seats.html       # Seat selection interface
    └── success.html     # Booking confirmation page
```

## API Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Home page with movie list |
| `/register` | GET/POST | User registration |
| `/login` | GET/POST | User authentication |
| `/book/<movie_id>` | GET/POST | Seat booking interface |
| `/logout` | GET | End user session |

## Database Queries Examples

### View all bookings for a user
```sql
SELECT b.id, m.title, s.seat_number, b.booking_date 
FROM bookings b
JOIN movies m ON b.movie_id = m.id
JOIN seats s ON b.seat_id = s.id
WHERE b.user_id = 1
ORDER BY b.booking_date DESC;
```

### Find available seats for a movie
```sql
SELECT seat_number FROM seats 
WHERE movie_id = 1 AND is_booked = FALSE;
```

### Movie popularity report
```sql
SELECT m.title, COUNT(b.id) as total_bookings
FROM movies m
LEFT JOIN bookings b ON m.id = b.movie_id
GROUP BY m.id, m.title
ORDER BY total_bookings DESC;
```

## DBMS Concepts Demonstrated

- **Normalization**: Separate tables for users, movies, seats, and bookings
- **Foreign Keys**: Referential integrity across tables
- **Unique Constraints**: Prevent duplicate seat bookings
- **Transactions**: Atomic booking operations
- **Indexes**: Efficient queries on frequently searched columns
- **ACID Properties**: Data consistency and reliability

## Troubleshooting

### MySQL Connection Error
```
Error: Access denied for user 'root'@'localhost'
```
**Solution**: Verify MySQL is running and credentials are correct
```powershell
# Test connection
mysql -h localhost -u root -p
```

### Port Already in Use
```
Address already in use
```
**Solution**: Change Flask port or stop the existing process
```python
app.run(debug=True, port=5001)
```

### Database Not Found
```
Error: Unknown database 'bms'
```
**Solution**: Run setup steps again
```bash
mysql -u root -p -e "CREATE DATABASE bms;"
python setup.py
```

## Performance Optimization Ideas

1. Add indexes on frequently queried columns (movie_id, user_id)
2. Implement seat availability caching
3. Add query optimization for booking reports
4. Consider connection pooling for high traffic

## Future Enhancements

- [ ] Email notifications for bookings
- [ ] Payment gateway integration
- [ ] Seat categories (premium, standard, economy)
- [ ] Show timings and multiple theaters
- [ ] Booking cancellation and refunds
- [ ] Admin panel for movie management
- [ ] Advanced reporting and analytics
- [ ] API endpoints for mobile apps

## License

Educational project for DBMS learning.

## Author

Created as a DBMS open-ended experiment project.