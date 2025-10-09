````markdown
# 🩺 Diabetes Prediction System  
An **AI/ML-based web application** that predicts whether a person is **Diabetic or Non-Diabetic** based on their health metrics.  
Built for healthcare professionals to quickly assess patient risk and manage patient records efficiently.
---

## 🚀 Features  
✅ **Machine Learning Model:** Random Forest trained on a diabetes dataset.  
✅ **User Input:** Enter patient details like Age, Glucose, BMI, Blood Pressure, etc.  
✅ **Real-Time Prediction:** Get instant prediction with confidence level.  
✅ **Patient Management:** View, search, delete, and export patient data as CSV.  
✅ **Interactive UI:** Clean and responsive interface with prediction tips & visual feedback.  
---

## 🧠 Tech Stack  
| Layer | Tools / Libraries |
| **Backend** | Python Flask |
| **Frontend** | HTML, CSS, JavaScript |
| **Machine Learning** | scikit-learn, pandas, numpy, seaborn, matplotlib |
| **Database** | MySQL (hosted on Aiven Cloud) |
| **Deployment** | Render (Web Service) + Aiven (DB Hosting) |
---

## ⚙️ How It Works  
1️⃣ User fills patient details in the form.  
2️⃣ Data is preprocessed and scaled.  
3️⃣ Random Forest model predicts **Diabetic / Non-Diabetic**.  
4️⃣ Result appears on the interface and is stored in MySQL (Aiven).  
5️⃣ Users can manage or export records as CSV.  
---

## 🌐 Live Demo  
🔗 **[https://diabetes-prediction-system-tbty.onrender.com](https://diabetes-prediction-system-tbty.onrender.com)**
---

## 💻 Run Instructions  
### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/Aman14150/diabetes-prediction-system.git
cd diabetes-prediction-system
````

### 2️⃣ Create Virtual Environment (optional but recommended)
```bash
python -m venv venv
# Activate environment
venv\Scripts\activate       # For Windows
source venv/bin/activate    # For Mac/Linux
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

If you don’t have `requirements.txt`, install manually:
```bash
pip install Flask==2.3.3 pandas==2.1.1 numpy==1.26.2 scikit-learn==1.3.3 matplotlib==3.8.1 seaborn==1.3.2 joblib==1.3.2 mysql-connector-python==8.1.1
```
---

## 🧩 4️⃣ Setup MySQL Database (Aiven Console)
### Step 1: Create MySQL Instance
* Go to 👉 [https://console.aiven.io](https://console.aiven.io)
* Click **Create Service → MySQL**
* Choose **Cloud Provider + Region**
* Once created, go to **Service Overview → Connection Information**

### Step 2: Copy these credentials
* **Host**
* **Port**
* **Database Name**
* **User**
* **Password**

### Step 3: Update `app.py` connection
```python
import mysql.connector

db = mysql.connector.connect(
    host="your-aiven-host",
    port=your_aiven_port,
    user="your_aiven_user",
    password="your_aiven_password",
    database="your_aiven_database",
    ssl_disabled=False
)
```

### Step 4: Create Table in MySQL
```sql
CREATE TABLE patients (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  gender VARCHAR(10),
  age INT,
  pregnancies INT,
  glucose FLOAT,
  blood_pressure FLOAT,
  skin_thickness FLOAT,
  insulin FLOAT,
  bmi FLOAT,
  dpf FLOAT,
  prediction VARCHAR(20)
);
```
---
## ▶️ 5️⃣ Run Flask App Locally
```bash
python app.py
```

Then open in browser → [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## ☁️ 6️⃣ Deploy on Render
1. Go to [https://render.com](https://render.com) → Create a **Web Service**
2. Connect your GitHub repo
3. Add Environment Variables under **Render → Environment → Add New Variables**

```env
DB_HOST=your-aiven-host
DB_PORT=your-aiven-port
DB_USER=your-aiven-user
DB_PASS=your-aiven-password
DB_NAME=your-aiven-database
```

4. Update your `app.py` to use environment variables:
```python
import os
import mysql.connector

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_NAME")
)
```

5. Render will automatically detect your Flask app and deploy it 🚀
---

## 🧪 7️⃣ (Optional) Train a New Model
Open `Diabetes_Prediction.ipynb` → Run all cells
New trained files will be saved as:
```
diabetes_model.pkl
scaler.pkl
```
Replace the old ones in your Flask directory to update predictions.
---

## 📸 Project Preview
| Page                  | Description                                               |
| --------------------- | --------------------------------------------------------- |
| **Home Page**         | Input form for patient details                            |
| **Prediction Result** | Displays "Diabetic" or "Non-Diabetic" with emoji feedback |
| **Patient Records**   | Shows all saved patient details                           |
| **Export CSV**        | Download records as CSV file                              |

---

## 🧑‍💻 Developer
👨‍💻 **Aman Rakhade**
📧 [LinkedIn](https://linkedin.com/in/amanrakhade) | [GitHub](https://github.com/Aman14150)
