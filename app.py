from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os
import csv
import requests
from werkzeug.utils import secure_filename
from temp import create_id_card

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

GOOGLE_SHEET_CSV_URL = 'link'

def check_registration(reg_no):
    response = requests.get(GOOGLE_SHEET_CSV_URL)
    response.raise_for_status()
    lines = response.text.splitlines()
    # Debug: print the first row and column names
    print('--- Google Sheet CSV Debug ---')
    reader_debug = csv.DictReader(lines)
    debug_columns = reader_debug.fieldnames
    print('Columns:', debug_columns)
    first_row = next(reader_debug, None)
    print('First row:', first_row)
    # Actual check
    columns = [
        '''Leader's Registration Number''',
        'Member 2 Registration Number ',
        'Team member 3 registration number',
        'Team member 4 registration number',
        'Team member 5 registration number'
    ]
    reader = csv.DictReader(lines)
    for row in reader:
        for col in columns:
            if str(row.get(col, '')).strip() == str(reg_no).strip():
                return True
    return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        reg_no = request.form['reg_no']
        photo = request.files['photo']
        if not photo or not name or not reg_no:
            flash('All fields are required!')
            return redirect(url_for('index'))
        # Check registration
        is_valid = check_registration(reg_no)
        if not is_valid:
            flash('Registration number not found!')
            return redirect(url_for('index'))
        # Save photo
        filename = secure_filename(photo.filename)
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(photo_path)
        # Generate ID card
        create_id_card(photo_path, name)
        return send_file('id_card.png', as_attachment=True)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
