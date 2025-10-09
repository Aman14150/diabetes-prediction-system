from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import joblib
import pandas as pd
import io
import csv
import os
import mysql.connector

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# --- MySQL Connection (Aiven) ---
try:
    db = mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST'),
        user=os.environ.get('MYSQL_USER'),
        password=os.environ.get('MYSQL_PASSWORD'),
        database=os.environ.get('MYSQL_DB'),
        port=int(os.environ.get('MYSQL_PORT', 3306)),
        ssl_ca=None,  # Aiven uses SSL, you can set SSL CA if needed
        ssl_verify_cert=True
    )
    cursor = db.cursor()
    print("✅ DB connected!")
except Exception as e:
    db = None
    cursor = None
    print("⚠️ DB connection failed:", e)

# --- Load model & scaler ---
model = joblib.load("diabetes_model.pkl")
scaler = joblib.load("scaler.pkl")


@app.route('/')
def home():
    return render_template('index.html', prediction_text=None, show_patients=False)


# --- Patients Page ---
@app.route('/patients')
def patients():
    if not cursor:
        flash("⚠️ Database not connected. Showing frontend only.", "warning")
        return render_template('index.html', show_patients=False)

    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))
    offset = (page - 1) * per_page

    query = "SELECT * FROM patients"
    params = ()

    if search:
        query += " WHERE name LIKE %s OR prediction LIKE %s"
        params = (f"%{search}%", f"%{search}%")

    # Count total
    cursor.execute(f"SELECT COUNT(*) FROM ({query}) AS subquery", params)
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
    if not cursor:
        flash("⚠️ Database not connected. Cannot export CSV.", "warning")
        return redirect(url_for('home'))

    cursor.execute("SELECT * FROM patients ORDER BY id DESC")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    id_index = columns.index('id')
    columns.pop(id_index)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Sr. No.'] + columns)

    for i, row in enumerate(rows, start=1):
        row_list = list(row)
        row_list.pop(id_index)
        writer.writerow([i] + row_list)

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='patients.csv')


# --- Delete Patient ---
@app.route('/delete/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    if cursor:
        cursor.execute("DELETE FROM patients WHERE id=%s", (patient_id,))
        db.commit()
        flash("✅ Patient deleted successfully!", "success")
    else:
        flash("⚠️ Database not connected. Cannot delete patient.", "warning")
    return redirect(url_for('patients'))


# --- Predict ---
@app.route('/predict', methods=['POST'])
def predict():
    try:
        name = request.form['name']
        gender = request.form['gender']
        fields = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness", "Insulin",
                  "BMI", "DiabetesPedigreeFunction", "Age"]
        data = [float(request.form[key]) for key in fields]

        input_df = pd.DataFrame([data], columns=fields)
        scaled_input = scaler.transform(input_df)
        pred_idx = int(model.predict(scaled_input)[0])
        result = "Diabetic" if pred_idx == 1 else "Non-Diabetic"

        # Save to DB only if cursor exists
        if cursor:
            sql = """INSERT INTO patients 
                     (name, gender, age, pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, dpf, prediction)
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cursor.execute(sql, (name, gender, data[7], data[0], data[1], data[2], data[3], data[4], data[5], data[6], result))
            db.commit()

        # Optional probabilities & feature importance
        probs = model.predict_proba(scaled_input)[0].tolist() if hasattr(model, "predict_proba") else None
        confidence = round(probs[pred_idx] * 100, 2) if probs else None
        feature_importance = dict(zip(fields, model.feature_importances_.tolist())) if hasattr(model, 'feature_importances_') else None

        return jsonify({
            'status': 'success',
            'result': result,
            'confidence': confidence,
            'probabilities': probs,
            'feature_importance': feature_importance
        })

    except Exception as e:
        return jsonify({'status': 'error', 'messages': [str(e)]})


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
