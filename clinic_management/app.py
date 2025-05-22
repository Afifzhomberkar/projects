from flask import Flask, render_template, request, redirect, url_for,session
from flask_sqlalchemy  import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'afif'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


#  Database Instance 
db = SQLAlchemy(app)

# Defining model of patient Table 
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key =True, autoincrement=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    disease = db.Column(db.String(200))
    date = db.Column(db.Date,default =datetime.utcnow)

# Doctor Authentication
DOCTOR_USERNAME = 'doctor'
DOCTOR_PASSWORD = 'doctor123'

# Receptionist Authentication
RECEPTIONIST_USERNAME = 'receptionist'
RECEPTIONIST_PASSWORD = 'receptionist123'

# User Authentication
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['userType']

        if user_type == 'doctor':
            if username == DOCTOR_USERNAME and password == DOCTOR_PASSWORD:
                session['user'] = 'doctor'
                return redirect(url_for('patient'))
            else:
                return render_template('login.html', error='Invalid credentials')
        elif user_type == 'receptionist':
            if username == RECEPTIONIST_USERNAME and password == RECEPTIONIST_PASSWORD:
                session['user'] = 'receptionist'
                return redirect(url_for('receptionist_dashboard'))
            else:
                return render_template('login.html', error='Invalid credentials')
        else:
            return render_template('login.html', error='Invalid user type')
    else:
        return render_template('login.html')       



@app.route('/receptionist_dashboard')
def receptionist_dashboard():
    user = session.get('user')
    if user != 'receptionist':
        return redirect(url_for('login'))   
    else:
        return redirect(url_for('view_patients'))

@app.route('/add-patient', methods=['GET', 'POST'])
def add_patient():
    user = session.get('user')
    if user != 'receptionist':
        return redirect(url_for('login'))
    
    if request.method == 'GET':
       return render_template('add_patient.html')
    elif request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        contact = request.form['contact']
        disease = request.form['disease']
        new_patient = Patient(name=name, age=age, gender=gender, phone=contact, disease=disease)
        db.session.add(new_patient)
        db.session.commit()
        return redirect(url_for('view_patients'))

@app.route('/view-patients')
def view_patients():
    user = session.get('user')
    if user != 'receptionist':
        return redirect(url_for('login'))
    
    patients = Patient.query.all()
    return render_template('view_patient.html', patients=patients)

@app.route('/update-patient/<int:id>', methods=['GET', 'POST'])
def get_patient(id):

    user = session.get('user')
    if user != 'receptionist':
        return redirect(url_for('login'))

    patient = Patient.query.get_or_404(id)
    if request.method == 'GET':
        return render_template('update_patient.html', patient=patient)
    elif request.method == 'POST':
        patient.name = request.form['name']
        patient.age = request.form['age']
        patient.phone = request.form['contact']
        patient.disease = request.form['disease']
        patient.gender = request.form['gender']
        db.session.commit()
        return redirect(url_for('view_patients'))
        

@app.route('/delete-patient/<int:id>')
def delete_patient(id):
    user = session.get('user')
    if user != 'receptionist':
        return redirect(url_for('login'))
    
    patient = Patient.query.get_or_404(id)
    db.session.delete(patient)
    db.session.commit()
    return redirect(url_for('view_patients'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/patient')
def patient():
    user = session.get('user')
    if user != 'doctor':
        return redirect(url_for('login'))   
    
    patients = Patient.query.all()
    return render_template('patients.html', patients=patients)

@app.route('/doctor-delete-patient/<int:id>')
def doctor_delete_patient(id):
    user = session.get('user')
    if user != 'doctor':
        return redirect(url_for('login'))
    
    patient = Patient.query.get_or_404(id)
    db.session.delete(patient)
    db.session.commit()
    return redirect(url_for('patient'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)