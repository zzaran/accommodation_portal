from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

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
    conn = psycopg2.connect(**DATABASE_CONFIG)
    return conn

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

# Route: Register User
@app.route('/register', methods=['POST'])
def register_user():
    return jsonify({"message": "User registration placeholder"})

# Route: Login User
@app.route('/login', methods=['POST'])
def login_user():
    return jsonify({"message": "User login placeholder"})

# Route: Get Accommodations
@app.route('/accommodations', methods=['GET'])
def get_accommodations():
    return jsonify({"message": "List of accommodations placeholder"})

# Route: Add Accommodation
@app.route('/add-accommodation', methods=['POST'])
def add_accommodation():
    return jsonify({"message": "Add accommodation placeholder"})

if __name__ == '__main__':
    app.run(debug=True)
