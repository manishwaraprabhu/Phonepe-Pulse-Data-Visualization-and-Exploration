# 📊 PhonePe Pulse Data Visualization and Exploration

This project aims to extract, process, and visualize large-scale data related to digital transactions and user statistics from the [PhonePe Pulse GitHub repository](https://github.com/PhonePe/pulse). The data is transformed and presented through an interactive and user-friendly web dashboard built using **Streamlit** and **Plotly**.

## 🚀 Project Overview

- 📁 The project was developed locally in **VSCode**, within a newly created virtual environment.
- 🔗 I cloned the PhonePe Pulse repository from the GitHub link provided by the GUVI team to extract and download the required dataset.
- 🛠️ A new database named **`phonepe_pulse.db`** was created, and the extracted data was structured into appropriate tables and inserted using custom scripts.
- 📊 A two-page **Streamlit** dashboard was designed and developed based on the core requirements of the project.

## 🧱 Streamlit App Structure

The app consists of **two main pages**:

### 1. Dashboard Page

Provides an intuitive interface for exploring digital transaction and user data across India.

#### Sidebar Navigation Includes:
- 📄 Select Page dropdown: `Dashboard` or `Query Data`
- 🔘 Radio Buttons: `Transactions` and `Users`
- 🗓️ Select Year dropdown
- 📆 Select Quarter dropdown

#### When `Transactions` is selected:
- 🗺️ Interactive 2D India map
- Hovering over any state shows:
  - State name
  - Total Transaction Amount
  - Total Transaction Count
- 📉 Transactions Table:
  - Total Transactions (Count)
  - Total Payment Value (Amount)
  - Average Transaction Value
- 📊 Categories Table:
  - Merchant payments
  - Peer-to-peer payments
  - Recharge & bill payments
  - Financial Services
  - Others
- 🔘 Top 10 insights: `States`, `Districts`, `Postal Codes`

#### When `Users` is selected:
- 🗺️ Map showing:
  - State name
  - User Count
  - User Percentage
- 📉 Users Table:
  - Registered PhonePe Users
  - PhonePe App Opens
- 🔘 Top 10 insights: `States`, `Districts`, `Postal Codes`

### 2. Query Data Page

Provides analytical insights derived from SQL queries on the underlying database.

- 🧠 Includes 10 predefined analytical questions
- 🧾 SQL queries display insights based on user selection

## 🧠 Learning Outcomes

- ✅ GitHub data extraction
- ✅ Data cleaning with Pandas
- ✅ SQL database integration
- ✅ Streamlit + Plotly dashboard creation
- ✅ Geo-visualization with maps
- ✅ Writing and integrating SQL queries

## 📂 Technologies Used

- Python
- Pandas
- Streamlit
- Plotly
- MySQL / SQLite
- mysql-connector-python
- Git / GitHub

## 📌 Dataset

- Source: [PhonePe Pulse GitHub Repository](https://github.com/PhonePe/pulse)
- Type: Digital Payments & User Statistics
- Inspired by: PhonePe Pulse

## 🏁 How to Run Locally

1. Clone the repository  
2. Install dependencies  
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the app  
   ```bash
   streamlit run phonepe_app.py
   ```
