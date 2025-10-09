Diabetes Prediction System:
A AI/ML-based web application that predicts whether a person is Diabetic or Non-Diabetic based on their health metrics. Built for healthcare professionals to quickly assess patient risk.

Features:
Machine Learning Model: Random Forest trained on a diabetes dataset.
User Input: Enter patient details like Age, Glucose, BMI, Blood Pressure, etc.
Real-Time Prediction: Get instant prediction with confidence.
Patient Management:
View saved patient records.
Search, delete, and export patient data as CSV.
Interactive UI: Clean interface with prediction tips and visual feedback.

Tech Stack:
Backend: Python Flask
Frontend: HTML, CSS, JavaScript
ML Libraries: scikit-learn, pandas, numpy, seaborn, matplotlib
Database: MySQL (stores patient records)

How It Works:
1.Users fill the patient data form.
2.Data is scaled and passed to the trained Random Forest model.
3.Model predicts Diabetic / Non-Diabetic.
4.Result is displayed on the interface and saved in the database.
5.Users can manage patient records or export them as CSV.

Live Demo: https://diabetes-prediction-system-tbty.onrender.com

💻 Run Instructions: 
```bash
1️⃣ **Clone the repository** 
git clone https://github.com/Aman14150/diabetes-prediction-system.git
cd diabetes-prediction-system

2️⃣ Create virtual environment (optional but recommended)
python -m venv venv
# Activate environment:
# Windows:
venv\Scripts\activate
# Linux / Mac:
source venv/bin/activate

3️⃣ Install dependencies
pip install Flask==2.3.3
pandas==2.1.1
numpy==1.26.2
scikit-learn==1.3.3
matplotlib==3.8.1
seaborn==1.3.2
joblib==1.3.2
mysql-connector-python==8.1.1

4️⃣ Set up MySQL database
Create database: diabetes_db
Create table patients with columns:
id, name, gender, age, pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, dpf, prediction

5️⃣ Run the Flask app
python app.py

6️⃣ Open in browser
Visit: http://127.0.0.1:5000
Fill form → Predict → Save patients → View / Export CSV

7️⃣ Optional: Train model
Open Diabetes_Prediction.ipynb to retrain the model
Trained model (diabetes_model.pkl) and scaler (scaler.pkl) will be saved automatically


