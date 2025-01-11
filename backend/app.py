from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.errors import UniqueViolation
from utils import calculate_age_group
import uuid
from flask_mail import Mail, Message

app = Flask(__name__)

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'zayd.zaran@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'Newpfm2da@'  # Replace with your email password
mail = Mail(app)

# Database Configuration
DATABASE_CONFIG = {
    'dbname': 'accommodation_portal',
    'user': 'postgres',
    'password': 'Newpfm@2day',
    'host': 'localhost',
    'port': '5432',
}


def get_db_connection():
    """Establish a connection to the PostgreSQL database."""
    conn = psycopg2.connect(**DATABASE_CONFIG, cursor_factory=RealDictCursor)
    return conn


def create_tables():
    """Create tables for users, accommodations, and email_verifications."""
    commands = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            user_type VARCHAR(50) NOT NULL, -- 'student' or 'provider'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            photo_url VARCHAR(255),
            institution VARCHAR(255),
            course VARCHAR(255),
            about_me TEXT,
            gender VARCHAR(50),
            date_of_birth DATE,
            location_preferences TEXT,
            is_student BOOLEAN,
            is_verified BOOLEAN DEFAULT FALSE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS accommodations (
            id SERIAL PRIMARY KEY,
            provider_id INT NOT NULL REFERENCES users (id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            price NUMERIC(10, 2) NOT NULL,
            location VARCHAR(255),
            max_occupants INT,
            nearest_institution VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS email_verifications (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL REFERENCES users (id) ON DELETE CASCADE,
            verification_token VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        for command in commands:
            cursor.execute(command)
        conn.commit()
        cursor.close()
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
    finally:
        if conn is not None:
            conn.close()


# Route to initialize the database
@app.route('/init-db', methods=['GET'])
def init_db():
    try:
        create_tables()
        return jsonify({"message": "Database tables created successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Test Database Connection
@app.route('/test-db', methods=['GET'])
def test_db():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"message": "Database connection successful!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Homepage
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Accommodation Portal!"})


# Route: Register User with Email Verification

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert user into the database
        cursor.execute(
            """
            INSERT INTO users (name, email, password, photo_url, institution, course, about_me, gender, date_of_birth, location_preferences, is_student, user_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
            """,
            (
                data['name'], data['email'], data['password'], data.get('photo_url'),
                data.get('institution'), data.get('course'), data.get('about_me'),
                data.get('gender'), data.get('date_of_birth'), ','.join(data.get('location_preferences', [])),
                data['user_type'] == 'student', data['user_type']
            )
        )
        user_id = cursor.fetchone()['id']

        # Generate verification token
        verification_token = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO email_verifications (user_id, verification_token)
            VALUES (%s, %s)
            """,
            (user_id, verification_token)
        )
        conn.commit()

        # Send verification email
        verification_link = f"http://127.0.0.1:5000/verify-email?token={verification_token}"
        msg = Message(
            "Verify Your Email",
            sender="zayd.zaran@gmail.com",
            recipients=[data['email']]
        )
        msg.body = f"Hi {data['name']},\n\nClick the link below to verify your email address:\n\n{verification_link}\n\nThank you!"
        mail.send(msg)

        cursor.close()
        conn.close()
        return jsonify({"message": "Registration successful! Please verify your email."}), 200

    except UniqueViolation:
        # Handle duplicate email error
        return jsonify({"error": "The email address is already registered. Please use a different email."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route: Verify Email
@app.route('/verify-email', methods=['GET'])
def verify_email():
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Verification token is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if token exists
        cursor.execute(
            """
            SELECT user_id FROM email_verifications WHERE verification_token = %s
            """,
            (token,)
        )
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Invalid or expired token"}), 400

        user_id = result['user_id']

        # Mark user as verified and delete the token
        cursor.execute("UPDATE users SET is_verified = TRUE WHERE id = %s", (user_id,))
        cursor.execute("DELETE FROM email_verifications WHERE verification_token = %s", (token,))
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({"message": "Email verified successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route: Login User
@app.route('/login', methods=['POST'])
def login_user():
    # Existing login functionality unchanged
    ...


# Route: User Profile
@app.route('/user-profile', methods=['GET'])
def user_profile():
    # Existing user profile functionality unchanged
    ...


# Route: Get Accommodations
@app.route('/accommodations', methods=['GET'])
def get_accommodations():
    # Existing accommodations functionality unchanged
    ...


# Route: Add Accommodation
@app.route('/add-accommodation', methods=['POST'])
def add_accommodation():
    # Existing add accommodation functionality unchanged
    ...


if __name__ == '__main__':
    app.run(debug=True)
