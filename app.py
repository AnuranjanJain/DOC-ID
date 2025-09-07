
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os
import csv
from werkzeug.utils import secure_filename
from temp import create_id_card

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def check_registration(reg_no, name):
    reg_columns = [
        "Team leader registration number",
        "Team member 2 registration number ",
        "Team member 3 registration number",
        "Team member 4 registration number ",
        "Team member 5 registration number"
    ]
    name_columns = [
        "Team Leader Name (Team member 1)",
        "Team member 2 name",
        "Team member 3 name",
        "Team member 4 name",
        "Team member 5 name"
    ]
    with open('DOC(Responces).csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for reg_col, name_col in zip(reg_columns, name_columns):
                reg_val = str(row.get(reg_col, '')).strip()
                name_val = str(row.get(name_col, '')).strip()
                if reg_val.replace(' ', '') == reg_no.replace(' ', ''):
                    if name_val.lower().replace(' ', '') == name.lower().replace(' ', ''):
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
        is_valid = check_registration(reg_no, name)
        if not is_valid:
            flash('Registration number and name do not match!')
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
