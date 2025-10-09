from flask import Flask, render_template, request, redirect, url_for
import joblib
import pandas as pd
import mysql.connector

app = Flask(__name__)

# MySQL Connection
db = mysql.connector.connect(
    host="127.0.0.1",
    port=3307,
    user="amanR",
    password="Mysql@150",
    database="diabetes_db"
)
cursor = db.cursor()
print("Database Connected successfully ✅")

# Load model & scaler
model = joblib.load("diabetes_model.pkl")
scaler = joblib.load("scaler.pkl")

@app.route('/')
def home():
    return render_template('index.html', prediction_text=None, show_patients=False)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Personal info
        name = request.form['name']
        mobile = request.form['mobile']

        # Health data
        data = [float(request.form[key]) for key in [
            "Pregnancies","Glucose","BloodPressure","SkinThickness",
            "Insulin","BMI","DiabetesPedigreeFunction","Age"
        ]]
        input_df = pd.DataFrame([data], columns=[
            "Pregnancies","Glucose","BloodPressure","SkinThickness",
            "Insulin","BMI","DiabetesPedigreeFunction","Age"
        ])
        scaled_input = scaler.transform(input_df)
        prediction = model.predict(scaled_input)[0]
        result = "Diabetic" if prediction == 1 else "Non-Diabetic"

        # Save to MySQL
        sql = """INSERT INTO patients 
                 (name, mobile, pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, dpf, age, prediction)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cursor.execute(sql, (name, mobile, *data, result))
        db.commit()

        return render_template('index.html', prediction_text=f"Prediction: 🩺 {result}", show_patients=False)

    except Exception as e:
        return render_template('index.html', prediction_text=f"Error: {str(e)}", show_patients=False)

@app.route('/patients')
def patients():
    cursor.execute("SELECT * FROM patients")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return render_template('index.html', patient_data=rows, patient_columns=columns, show_patients=True)

@app.route('/delete/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    cursor.execute("DELETE FROM patients WHERE id=%s", (patient_id,))
    db.commit()
    return redirect(url_for('patients'))

if __name__ == '__main__':
    app.run(debug=True)
