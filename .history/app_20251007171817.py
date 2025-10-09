from flask import Flask, render_template, request
import joblib
import numpy as np
import pandas as pd
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="diabetes_db"
)
cursor = db.cursor()

# Load trained model & scaler
model = joblib.load("diabetes_model.pkl")
scaler = joblib.load("scaler.pkl")

@app.route('/')
def home():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True)
