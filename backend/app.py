from flask import Flask, render_template, request, redirect, url_for, flash, session
from db.mongo import db

app = Flask(__name__, template_folder='../frontend/templates')
app.secret_key = 'your_secret_key_here'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username, password)
        user = db.users.find_one({'username': username, 'password': password, 'is_admin': True})
        print(user)
        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials or not an admin.')
            return render_template('login.html')
    return render_template('login.html')

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