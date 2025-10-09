from flask import Flask, render_template, request
import joblib
import numpy as np
import pandas as pd
import mysql.connector

app = Flask(__name__)

import mysql.connector

db = mysql.connector.connect(
    host="127.0.0.1",
    port=3307,
    user="amanR",
    password="Mysql@150",
    database="diabetes_db"
)
cursor = db.cursor()

print("Database Connected successfully ✅")


# Load trained model & scaler
model = joblib.load("diabetes_model.pkl")
scaler = joblib.load("scaler.pkl")

@app.route('/')
def home():
    return render_template('index.html' , prediction_text=None, show_patients=False)

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

        return render_template('index.html', prediction_text=f"Prediction: 🩺 {result}")

    except Exception as e:
        return render_template('index.html', prediction_text=f"Error: {str(e)}")
    
@app.route('/patients')
def patients():
    cursor.execute("SELECT * FROM patients")
    rows = cursor.fetchall()
    # Column names fetch karne ke liye
    columns = [desc[0] for desc in cursor.description]
    return render_template('index.html', patient_data=rows, patient_columns=columns, show_patients=True)


if __name__ == '__main__':
    app.run(debug=True)
