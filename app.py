from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# =========================================================================
# DATABASE INITIALIZATION & STRUCTURE OPTIMIZATION
# =========================================================================
with app.app_context():
    try:
        import MySQLdb
        db = MySQLdb.connect(
            host=Config.MYSQL_HOST, 
            user=Config.MYSQL_USER, 
            passwd=Config.MYSQL_PASSWORD
        )
        cursor = db.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS cbit_career_hub")
        db.select_db('cbit_career_hub')
        
        # Enhanced Users Table with Career Profile Data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fullname VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                skills VARCHAR(255) DEFAULT 'Python, SQL, HTML, CSS, JavaScript, Git',
                college VARCHAR(150) DEFAULT 'Chaitanya Bharathi Institute of Technology (CBIT)',
                graduation_year VARCHAR(10) DEFAULT '2027',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.close()
        db.close()
        print("[SUCCESS] Database optimized and structured successfully!")
    except Exception as e:
        print("[DB INIT ERROR]:", e)

mysql = MySQL(app)

# =========================================================================
# DUMMY REPOSITORIES FOR EFFICIENCY (JOB HUB DATA)
# =========================================================================
MOCK_JOBS = [
    {"id": 1, "title": "Associate Software Engineer", "company": "TCS", "location": "Hyderabad", "type": "Full-time", "package": "7.5 LPA"},
    {"id": 2, "title": "Frontend Developer Intern", "company": "Cognizant", "location": "Bangalore (Remote)", "type": "Internship", "package": "35K/Month"},
    {"id": 3, "title": "Data Analyst Trainee", "company": "Deloitte", "location": "Hyderabad", "type": "Full-time", "package": "8.2 LPA"},
    {"id": 4, "title": "Python Backend Developer", "company": "Tech Mahindra", "location": "Chennai", "type": "Full-time", "package": "6.0 LPA"}
]

# =========================================================================
# CORE ROUTES & LOGIC
# =========================================================================

@app.route('/')
def index():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        fullname = request.form['fullname'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        
        hashed_password = generate_password_hash(password)
        
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            account = cursor.fetchone()
            
            if account:
                flash('This email is already registered!', 'danger')
            else:
                cursor.execute('INSERT INTO users (fullname, email, password) VALUES (%s, %s, %s)', 
                               (fullname, email, hashed_password))
                mysql.connection.commit()
                flash('Your account has been created! Please log in.', 'success')
                return redirect(url_for('index'))
            cursor.close()
        except Exception as e:
            flash('Registration failed. Database error occurred.', 'danger')
            print("[REG_ERROR]:", e)
            
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email'].strip()
    password = request.form['password']
    
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        
        if user and check_password_hash(user['password'], password):
            session['loggedin'] = True
            session['id'] = user['id']
            session['fullname'] = user['fullname']
            session['email'] = user['email']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email account or password configuration.', 'danger')
            return redirect(url_for('index'))
    except Exception as e:
        flash('Database authentication pipeline failed.', 'danger')
        print("[LOGIN_ERROR]:", e)
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        flash('Session timeout or restricted zone. Please authenticate.', 'danger')
        return redirect(url_for('index'))
        
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
        user_profile = cursor.fetchone()
        cursor.close()
        
        return render_template('dashboard.html', user=user_profile, jobs=MOCK_JOBS)
    except Exception as e:
        print("[DASHBOARD_PROFILE_ERROR]:", e)
        return render_template('dashboard.html', user={"fullname": session['fullname'], "email": session['email'], "skills": "Python, SQL", "college": "CBIT", "graduation_year": "2027"}, jobs=MOCK_JOBS)

@app.route('/resume')
def view_resume():
    if 'loggedin' not in session:
        return redirect(url_for('index'))
        
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
        user_profile = cursor.fetchone()
        cursor.close()
        return render_template('resume.html', user=user_profile)
    except Exception as e:
        return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out cleanly from your secure workspace.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)