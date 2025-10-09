from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import joblib
import pandas as pd
import mysql.connector
import io
import csv

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Flask flash messages

# MySQL Connection (unchanged)
db = mysql.connector.connect(
    host="127.0.0.1",
    port=3307,
    user="amanR",
    password="Mysql@150",
    database="diabetes_db"
)
cursor = db.cursor()
print("Database Connected successfully ✅")

# Load model & scaler (unchanged)
model = joblib.load("diabetes_model.pkl")
scaler = joblib.load("scaler.pkl")

# --- Patients list with pagination and search ---
@app.route('/patients')
def patients():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))  # default page limit
    search = request.args.get('search', '')

    # Count total matching patients
    if search:
        cursor.execute("SELECT COUNT(*) FROM patients WHERE name LIKE %s OR prediction LIKE %s", (f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("SELECT COUNT(*) FROM patients")
    total_count = cursor.fetchone()[0]

    # Calculate offset
    offset = (page - 1) * per_page

    # Fetch patients with limit and search
    if search:
        cursor.execute(
            "SELECT * FROM patients WHERE name LIKE %s OR prediction LIKE %s ORDER BY id DESC LIMIT %s OFFSET %s",
            (f"%{search}%", f"%{search}%", per_page, offset)
        )
    else:
        cursor.execute("SELECT * FROM patients ORDER BY id DESC LIMIT %s OFFSET %s", (per_page, offset))

    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    total_pages = (total_count + per_page - 1) // per_page

    return render_template(
        'index.html',
        patient_data=rows,
        patient_columns=columns,
        show_patients=True,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        search=search
    )

# --- Export CSV ---
@app.route('/export_csv')
def export_csv():
    cursor.execute("SELECT * FROM patients ORDER BY id DESC")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    writer.writerows(rows)
    output.seek(0)

    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name="patients.csv")

# --- Delete patient with confirmation (frontend) ---
@app.route('/delete/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    cursor.execute("DELETE FROM patients WHERE id=%s", (patient_id,))
    db.commit()
    flash("Patient deleted successfully!", "success")
    return redirect(url_for('patients'))

# --- Predict route remains unchanged ---
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Validate numeric inputs (backend check)
        name = request.form['name']
        mobile = request.form['mobile']
        data = []
        for key in ["Pregnancies","Glucose","BloodPressure","SkinThickness","Insulin","BMI","DiabetesPedigreeFunction","Age"]:
            val = float(request.form[key])
            if val < 0:
                flash(f"Invalid value for {key}", "error")
                return redirect(url_for('home'))
            data.append(val)

        input_df = pd.DataFrame([data], columns=["Pregnancies","Glucose","BloodPressure","SkinThickness","Insulin","BMI","DiabetesPedigreeFunction","Age"])
        scaled_input = scaler.transform(input_df)
        prediction = model.predict(scaled_input)[0]
        result = "Diabetic" if prediction == 1 else "Non-Diabetic"

        sql = """INSERT INTO patients 
                 (name, mobile, pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, dpf, age, prediction)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cursor.execute(sql, (name, mobile, *data, result))
        db.commit()
        flash(f"Prediction saved: {result}", "success")
        return redirect(url_for('home'))

    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('home'))
