from flask import Flask, render_template, request, redirect, session, url_for
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Replace with a secure key in production

load_dotenv()

user_data = json.loads(os.getenv("USER_DATA"))

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        code = request.form.get('code')
        if code in user_data:
            session['script_url'] = user_data[code]
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid code')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'script_url' not in session:
        return redirect(url_for('login'))

    selected_date = request.args.get('date')
    if not selected_date:
        selected_date = datetime.now().strftime('%Y-%m-%d')

    try:
        response = requests.get(session['script_url'])
        data = response.json()

        # Correct date comparison (ignore 'Z' and parse to date)
        filtered_data = [
            d for d in data
            if (datetime.fromisoformat(d['Date'].replace('Z', '')) + timedelta(hours=5, minutes=30)).date().isoformat() == selected_date
        ]

        return render_template('dashboard.html', data=filtered_data, selected_date=selected_date)
    except Exception as e:
        return f"Error fetching data: {str(e)}"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5500)
