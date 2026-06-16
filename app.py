from flask import Flask, render_template, request, redirect, session, jsonify
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# MySQL Configuration
db_config = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', 'root'),
    'database': os.environ.get('MYSQL_DB', 'bms')
}


def get_db():
    """Get MySQL connection"""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        raise


def init_db():
    """Initialize database tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Movies table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            duration INT,
            genre VARCHAR(100),
            rating FLOAT DEFAULT 0,
            poster_url VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Seats table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS seats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            movie_id INT NOT NULL,
            seat_number VARCHAR(10) NOT NULL,
            is_booked BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
            UNIQUE KEY unique_seat (movie_id, seat_number)
        )
        ''')
        
        # Bookings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            movie_id INT NOT NULL,
            seat_id INT NOT NULL,
            booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'confirmed',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
            FOREIGN KEY (seat_id) REFERENCES seats(id) ON DELETE CASCADE
        )
        ''')
        
        conn.commit()
        print("Database initialized successfully")
    except Error as e:
        print(f"Error creating tables: {e}")
    finally:
        cursor.close()
        conn.close()


# Initialize database on startup
try:
    init_db()
except Exception as e:
    print(f"Warning: Could not initialize database: {e}")


# HOME PAGE
@app.route('/')
def home():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM movies')
    movies = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('index.html', movies=movies)


# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form.get('email', '')
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO users (username, password, email) VALUES (%s, %s, %s)',
                (username, password, email)
            )
            conn.commit()
            return redirect('/login')
        except Error as e:
            if 'Duplicate' in str(e):
                return render_template('register.html', error='Username already exists')
            return render_template('register.html', error=str(e))
        finally:
            cursor.close()
            conn.close()
    
    return render_template('register.html')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            'SELECT id, username FROM users WHERE username=%s AND password=%s',
            (username, password)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/')
        
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')


# MOVIE DETAILS & SEAT BOOKING
@app.route('/book/<int:movie_id>', methods=['GET', 'POST'])
def book(movie_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Get movie details
    cursor.execute('SELECT * FROM movies WHERE id=%s', (movie_id,))
    movie = cursor.fetchone()
    
    if not movie:
        cursor.close()
        conn.close()
        return redirect('/')
    
    if request.method == 'POST':
        # Get all selected seat IDs
        seat_ids = request.form.getlist('seat_ids')
        
        if not seat_ids:
            cursor.close()
            conn.close()
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT id, seat_number, is_booked FROM seats WHERE movie_id=%s ORDER BY seat_number', (movie_id,))
            seats = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('seats.html', movie=movie, seats=seats, error='Please select at least one seat')
        
        try:
            booked_seats = []
            
            # Check all seats are available
            for seat_id in seat_ids:
                cursor.execute('SELECT id, seat_number, is_booked FROM seats WHERE id=%s AND movie_id=%s', (seat_id, movie_id))
                seat = cursor.fetchone()
                
                if not seat or seat['is_booked']:
                    conn.rollback()
                    cursor.close()
                    conn.close()
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute('SELECT id, seat_number, is_booked FROM seats WHERE movie_id=%s ORDER BY seat_number', (movie_id,))
                    seats = cursor.fetchall()
                    cursor.close()
                    conn.close()
                    return render_template('seats.html', movie=movie, seats=seats, error=f'Seat {seat["seat_number"]} is already booked')
                
                booked_seats.append(seat['seat_number'])
            
            # Book all seats in transaction
            for seat_id in seat_ids:
                cursor.execute('UPDATE seats SET is_booked=TRUE WHERE id=%s', (seat_id,))
                cursor.execute(
                    'INSERT INTO bookings (user_id, movie_id, seat_id) VALUES (%s, %s, %s)',
                    (session['user_id'], movie_id, seat_id)
                )
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return render_template('success.html', movie=movie, seats=booked_seats)
        except Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT id, seat_number, is_booked FROM seats WHERE movie_id=%s ORDER BY seat_number', (movie_id,))
            seats = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('seats.html', movie=movie, seats=seats, error=f'Booking failed: {str(e)}')
    
    # Get all seats for this movie
    cursor.execute('SELECT id, seat_number, is_booked FROM seats WHERE movie_id=%s ORDER BY seat_number', (movie_id,))
    seats = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('seats.html', movie=movie, seats=seats)


# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)