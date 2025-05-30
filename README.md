
# 🧠 CRM System

A customer relationship management (CRM) web application built with **Streamlit**, **Flask**, and **MongoDB**, designed to help businesses manage customer data and analyze interactions over time.

---

## 📌 Features

- 🔐 **User Authentication**: Secure login and registration
- 👤 **Customer Management**: Add, view, update, and delete customer records
- 📈 **Data Visualization**:
  - Customer growth over time
  - Interaction types (calls, emails, meetings, etc.)
- 🔍 **Filtering & Searching**: Quickly find customer data
- 🧪 **API Integration**: Backend Flask API to handle data operations

---

## 🛠️ Tech Stack

| Layer       | Technology        |
|-------------|-------------------|
| Frontend    | Streamlit         |
| Backend     | Flask (REST API)  |
| Database    | MongoDB           |
| Authentication | Flask-Login / Custom session |
| Charts      | Matplotlib / Plotly / Seaborn |

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/trmzaiu/customer-relationship-management.git
cd customer-relationship-management
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

Start the backend API:

```bash
cd backend
python app.py
```

Start the frontend (Streamlit):

```bash
cd frontend
streamlit run main.py
```

---
