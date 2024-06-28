import torch
from torchvision import models, transforms
from PIL import Image
import os
import time
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'Lymphoma'

mysql = MySQL(app)

# Directory for file uploads
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load the model
model = models.resnet18(weights=None)  # Use weights=None instead of pretrained=False
num_ftrs = model.fc.in_features
model.fc = torch.nn.Linear(num_ftrs, 2)  # Assuming you have 2 classes
model.load_state_dict(torch.load('model.pth'))
model.eval()

# Define data transforms for the test image
data_transforms = transforms.Compose([
    transforms.Resize((224, 224)),  # Resize to match the input size of the model
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Define class names for your dataset
class_names = ['FL', 'MCL']


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM doctors WHERE Email = %s AND Password = %s', (email, password))
        account = cursor.fetchone()

        if account:
            session['doctorID'] = account['DoctorID']
            session['doctorName'] = account['FirstName']
            return redirect(url_for('welcome'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')


@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    if 'doctorID' not in session:
        return redirect(url_for('login'))

    doctorName = session['doctorName']
    msg = ''
    patientMsg = ''

    if request.method == 'POST':
        # Handle patient information
        if 'firstName' in request.form and 'lastName' in request.form and 'patientAge' in request.form and 'gender' in request.form:
            firstName = request.form['firstName']
            lastName = request.form['lastName']
            patientAge = request.form['patientAge']
            gender = request.form['gender']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("INSERT INTO patients (firstName, lastName, age, gender) VALUES (%s, %s, %s, %s)",
                           (firstName, lastName, patientAge, gender))
            mysql.connection.commit()
            patient_id = cursor.lastrowid  # Get the last inserted patient ID
            cursor.close()
            patientMsg = "Patient information saved successfully."

        # Handle image upload
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '':
                timestamp = int(time.time())
                file_extension = os.path.splitext(image.filename)[1]
                new_file_name = f"{timestamp}{file_extension}"
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], new_file_name))

                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("INSERT INTO images (name, type, path) VALUES (%s, %s, %s)",
                               (image.filename, image.content_type, new_file_name))
                mysql.connection.commit()
                image_id = cursor.lastrowid  # Get the last inserted image ID
                cursor.close()
                msg = "Image uploaded successfully."

                # Save prediction results
                predicted_label = "FL"  # Placeholder, replace with actual prediction
                confidence_score = "0.95"  # Placeholder, replace with actual confidence score
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("INSERT INTO predictions (doctor_id, patient_id, image_id, predicted_label, confidence_score) VALUES (%s, %s, %s, %s, %s)",
                               (session['doctorID'], patient_id, image_id, predicted_label, confidence_score))
                mysql.connection.commit()
                cursor.close()
            else:
                msg = "Error moving the uploaded file."

    # Fetch prediction history
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT predictions.id, patients.firstName, patients.lastName, patients.age, patients.gender, images.path, predictions.predicted_label, predictions.confidence_score FROM predictions JOIN patients ON predictions.patient_id = patients.id JOIN images ON predictions.image_id = images.id WHERE predictions.doctor_id = %s", (session['doctorID'],))
    history = cursor.fetchall()
    cursor.close()

    return render_template('welcome.html', doctorName=doctorName, msg=msg, patientMsg=patientMsg, history=history)


@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('welcome'))

    image = request.files['image']
    if image.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('welcome'))

    try:
        # Save the uploaded image
        timestamp = int(time.time())
        file_extension = os.path.splitext(image.filename)[1]
        new_file_name = f"{timestamp}{file_extension}"
        image_path = os.path.join('static', 'uploads', new_file_name)
        image.save(image_path)

        # Preprocess the image
        test_image = Image.open(image_path)
        input_tensor = data_transforms(test_image).unsqueeze(0)

        # Make predictions
        with torch.no_grad():
            output = model(input_tensor)
        probabilities = torch.softmax(output, dim=1)[0]
        predicted_class = torch.argmax(probabilities).item()
        predicted_label = class_names[predicted_class]
        confidence_score = probabilities[predicted_class].item()

        # Format confidence score to 2 decimal places
        confidence_score = f"{confidence_score:.2f}"

        # Save prediction results
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO patients (firstName, lastName, age, gender) VALUES (%s, %s, %s, %s)",
                       (request.form['firstName'], request.form['lastName'], request.form['patientAge'], request.form['gender']))
        mysql.connection.commit()
        patient_id = cursor.lastrowid  # Get the last inserted patient ID

        cursor.execute("INSERT INTO images (name, type, path) VALUES (%s, %s, %s)",
                       (image.filename, image.content_type, new_file_name))
        mysql.connection.commit()
        image_id = cursor.lastrowid  # Get the last inserted image ID

        cursor.execute("INSERT INTO predictions (doctor_id, patient_id, image_id, predicted_label, confidence_score) VALUES (%s, %s, %s, %s, %s)",
                       (session['doctorID'], patient_id, image_id, predicted_label, confidence_score))
        mysql.connection.commit()
        cursor.close()

        # Redirect to the result page with image path
        return redirect(url_for('result', predicted_label=predicted_label, confidence_score=confidence_score, image_path=new_file_name))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('welcome'))


@app.route('/result')
def result():
    predicted_label = request.args.get('predicted_label')
    confidence_score = request.args.get('confidence_score')
    image_path = request.args.get('image_path')
    return render_template('result.html', predicted_label=predicted_label, confidence_score=confidence_score,
                           image_path=image_path)


@app.route('/prediction_detail/<int:prediction_id>')
def prediction_detail(prediction_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT patients.firstName, patients.lastName, patients.age, patients.gender,
               images.path, predictions.predicted_label, predictions.confidence_score
        FROM predictions
        JOIN patients ON predictions.patient_id = patients.id
        JOIN images ON predictions.image_id = images.id
        WHERE predictions.id = %s
    """, (prediction_id,))
    record = cursor.fetchone()
    cursor.close()

    if not record:
        flash('Prediction record not found', 'error')
        return redirect(url_for('welcome'))

    return render_template('prediction_detail.html', record=record)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM doctors WHERE Email = %s', (email,))
        account = cursor.fetchone()

        if account:
            cursor.execute('UPDATE doctors SET Password = %s WHERE Email = %s', (new_password, email))
            mysql.connection.commit()
            cursor.close()
            flash('Password updated successfully.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email not found.', 'error')
            cursor.close()

    return render_template('forgot_password.html')


if __name__ == '__main__':
    app.run(debug=True)
