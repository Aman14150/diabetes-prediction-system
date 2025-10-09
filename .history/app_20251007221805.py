from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import joblib
import pandas as pd
import mysql.connector
import io
import csv

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# MySQL Connection
db = mysql.connector.connect(
    host="127.0.0.1",
    port=3307,
    user="amanR",
    password="Mysql@150",
    database="diabetes_db"
)
cursor = db.cursor()
print("✅ Database Connected successfully")

# Load model & scaler
model = joblib.load("diabetes_model.pkl")
scaler = joblib.load("scaler.pkl")

@app.route('/')
def home():
    return render_template('index.html', prediction_text=None, show_patients=False)

# --- Patients Page ---
@app.route('/patients')
def patients():
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))
    offset = (page - 1) * per_page

    query = "SELECT * FROM patients"
    params = ()

    if search:
        query += " WHERE name LIKE %s OR prediction LIKE %s"
        params = (f"%{search}%", f"%{search}%")

    cursor.execute(f"SELECT COUNT(*) FROM ({query}) as subquery", params)
    total_count = cursor.fetchone()[0]

    query += " ORDER BY id DESC LIMIT %s OFFSET %s"
    params += (per_page, offset)
    cursor.execute(query, params)

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

    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv',
                     as_attachment=True, download_name='patients.csv')

# --- Delete Patient ---
@app.route('/delete/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    cursor.execute("DELETE FROM patients WHERE id=%s", (patient_id,))
    db.commit()
    flash("Patient deleted successfully!", "success")
    return redirect(url_for('patients'))


# --- Predict Route ---
@app.route('/predict', methods=['POST'])
def predict():
    try:
        name = request.form['name']
        mobile = request.form['mobile']
        data = []
        fields = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin",
                  "BMI", "DiabetesPedigreeFunction", "Age"]

        # Ranges for validation
        valid_ranges = {
            "Pregnancies": (0, 20),
            "Glucose": (40, 300),
            "BloodPressure": (40, 200),
            "SkinThickness": (5, 100),
            "Insulin": (0, 900),
            "BMI": (10, 60),
            "DiabetesPedigreeFunction": (0, 3),
            "Age": (10, 100)
        }

        for key in fields:
            val = float(request.form[key])
            min_val, max_val = valid_ranges[key]
            if val < min_val or val > max_val:
                flash(f"❌ {key} value must be between {min_val} and {max_val}", "error")
                return redirect(url_for('home'))
            data.append(val)

        input_df = pd.DataFrame([data], columns=fields)
        scaled_input = scaler.transform(input_df)
        prediction = model.predict(scaled_input)[0]
        result = "Diabetic" if prediction == 1 else "Non-Diabetic"

        sql = """INSERT INTO patients 
                 (name, mobile, pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, dpf, age, prediction)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cursor.execute(sql, (name, mobile, *data, result))
        db.commit()

        return render_template('index.html', prediction_text=result, show_patients=False)

    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
