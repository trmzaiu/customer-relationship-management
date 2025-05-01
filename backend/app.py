from flask import Flask, render_template, request, redirect, url_for, flash, session
from db.mongo import db
import json
app = Flask(__name__, template_folder='../frontend/templates')
app.secret_key = 'your_secret_key_here'

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Verify credentials in MongoDB
    user = db.users.find_one({'username': username, 'password': password})
    
    if user:
        # Convert ObjectId to string to make it JSON serializable
        user_id = str(user.get('_id'))
        
        # Extract relevant user data 
        user_data = {
            'user_id': user_id,
            'username': user.get('username'),
            'is_admin': user.get('is_admin', False),
        }
        
        # Authentication successful
        response = app.response_class(
            response=json.dumps({
                "status": "success", 
                "message": "Login successful",
                "user_data": user_data
            }),
            status=200,
            mimetype='application/json'
        )
        return response
    else:
        # Authentication failed
        response = app.response_class(
            response=json.dumps({
                "status": "error", 
                "message": "Invalid credentials"
            }),
            status=401,
            mimetype='application/json'
        )
        return response

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        user_count = db.users.count_documents({})
        return render_template('dashboard.html', username=session['username'], user_count=user_count)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/users')
def list_users():
    if 'username' in session:
        users = list(db.users.find())
        return render_template('users.html', users=users)
    return redirect(url_for('login'))

@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = 'is_admin' in request.form
        if db.users.find_one({'username': username}):
            flash('Username already exists.')
        else:
            db.users.insert_one({
                'username': username,
                'password': password,
                'is_admin': is_admin
            })
            flash('User added successfully.')
        return redirect(url_for('list_users'))
    return render_template('add_user.html')

@app.route('/update-admin/<username>', methods=['POST'])
def update_admin(username):
    if 'username' not in session:
        return redirect(url_for('login'))
    is_admin = 'is_admin' in request.form
    db.users.update_one(
        {'username': username},
        {'$set': {'is_admin': is_admin}}
    )
    flash(f'Updated admin status for {username}.')
    return redirect(url_for('list_users'))

if __name__ == '__main__':
    app.run(debug=True)