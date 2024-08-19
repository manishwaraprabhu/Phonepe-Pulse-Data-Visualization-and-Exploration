import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Path to SQLite database
db_path = 'C:/Users/manis/SecondProject/phonepe_pulse.db'

# Connect to SQLite database
conn = sqlite3.connect(db_path)

# Load DataFrames from SQLite database
agg_trans_df = pd.read_sql_query("SELECT * FROM Aggregated_Transactions", conn)
agg_users_df = pd.read_sql_query("SELECT * FROM Aggregated_Users", conn)

# Close the database connection
conn.close()

# Load Map_Trans.csv, Top_Trans.csv, and Map_User.csv files
map_trans_df = pd.read_csv('C:/Users/manis/SecondProject/Map_Trans.csv')
top_trans_df = pd.read_csv('C:/Users/manis/SecondProject/Top_Trans.csv')
map_user_df = pd.read_csv('C:/Users/manis/SecondProject/Map_User.csv')
top_user_df = pd.read_csv('C:/Users/manis/SecondProject/Top_User.csv')

# Function to format numbers as Crores or Lakhs
def format_transaction_amount(amount):
    if amount >= 1e7:
        return f"{amount / 1e7:.2f} Cr"  # Crores
    elif amount >= 1e5:
        return f"{amount / 1e5:.2f} Lakh"  # Lakhs
    else:
        return f"{amount:.2f}"  # Less than 1 Lakh

# Streamlit app layout
st.set_page_config(page_title="PhonePe Pulse Dashboard", layout="wide")
st.title("PhonePe Pulse Data Visualization")

# Page selection
page = st.sidebar.selectbox("Select Page", ["Dashboard", "Query Data"])

if page == "Dashboard":
    data_type = st.sidebar.radio("Select Data Type", ("Transactions", "Users"))

    years = sorted(agg_trans_df['Year'].unique())
    selected_year = st.sidebar.selectbox("Select Year", years)

    quarters = {'Q1 (Jan - Mar)': 1, 'Q2 (Apr - Jun)': 2, 'Q3 (Jul - Sep)': 3, 'Q4 (Oct - Dec)': 4}
    selected_quarter = st.sidebar.selectbox("Select Quarter", list(quarters.keys()))

    # Filter data based on user selections
    quarter_num = quarters[selected_quarter]
    if data_type == "Transactions":
        filtered_df = agg_trans_df[(agg_trans_df['Year'] == selected_year) &
                                   (agg_trans_df['Quarter'] == quarter_num)]
        map_df = filtered_df.groupby('State').sum().reset_index()
        color_col = 'Transaction_Amount'
        title = 'Transactions Amount by State'
        hover_data = {
            'State': True,
            'Transaction_Amount': True,
            'Transaction_Count': True
        }

        # Calculate total values
        total_transactions = filtered_df['Transaction_Count'].sum()
        total_payment_value = filtered_df['Transaction_Amount'].sum()
        avg_transaction_value = total_payment_value / total_transactions if total_transactions > 0 else 0

        # Format values
        total_payment_value_formatted = format_transaction_amount(total_payment_value)
        avg_transaction_value_formatted = format_transaction_amount(avg_transaction_value)

        # Calculate categories' total values
        categories_df = filtered_df.groupby('Transaction_Type')['Transaction_Amount'].sum().reset_index()
        categories = {
            "Merchant payments": format_transaction_amount(categories_df[categories_df['Transaction_Type'] == 'Merchant payments']['Transaction_Amount'].sum()),
            "Peer-to-peer payments": format_transaction_amount(categories_df[categories_df['Transaction_Type'] == 'Peer-to-peer payments']['Transaction_Amount'].sum()),
            "Recharge & bill payments": format_transaction_amount(categories_df[categories_df['Transaction_Type'] == 'Recharge & bill payments']['Transaction_Amount'].sum()),
            "Financial Services": format_transaction_amount(categories_df[categories_df['Transaction_Type'] == 'Financial Services']['Transaction_Amount'].sum()),
            "Others": format_transaction_amount(categories_df[categories_df['Transaction_Type'].isin(['Merchant payments', 'Peer-to-peer payments', 'Recharge & bill payments', 'Financial Services']) == False]['Transaction_Amount'].sum())
        }
    else:
        filtered_df = agg_users_df[(agg_users_df['Year'] == selected_year) &
                                   (agg_users_df['Quarter'] == quarter_num)]
        map_df = filtered_df.groupby('State').sum().reset_index()
        color_col = 'User_Count'
        title = 'Users Count by State'
        hover_data = {
            'State': True,
            'User_Count': True,
            'User_Percentage': True
        }

        # Calculate registered users till the selected quarter and year
        registered_users_till = agg_users_df[(agg_users_df['Year'] <= selected_year) &
                                             ((agg_users_df['Year'] < selected_year) |
                                              (agg_users_df['Quarter'] <= quarter_num))]['User_Count'].sum()

        # Calculate app opens for the selected quarter and year
        app_opens = int((filtered_df['User_Count'] * (filtered_df['User_Percentage'] / 100)).sum().round())

    # Display map
    fig = px.choropleth(
        map_df,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey='properties.ST_NM',
        locations='State',
        color=color_col,
        color_continuous_scale='Blues',
        title=title,
        hover_data=hover_data  # Customize hover data based on the selected data type
    )
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # Display total transactions, total payment value, and avg. transaction value
    if data_type == "Transactions":
        st.subheader("Transactions")
        summary_df = pd.DataFrame({
            "Total Transactions (Count)": [total_transactions],
            "Total Payment Value (Amount)": [total_payment_value_formatted],
            "Avg. Transaction Value": [avg_transaction_value_formatted]
        })
        st.table(summary_df)

        # Display categories
        st.subheader("Categories")
        categories_df = pd.DataFrame.from_dict(categories, orient='index', columns=["Total Value"])
        st.table(categories_df)

    elif data_type == "Users":
        st.subheader("Users")
        summary_df = pd.DataFrame({
            f"Registered PhonePe users till Q{quarter_num} {selected_year}": [registered_users_till],
            f"PhonePe app opens in Q{quarter_num} {selected_year}": [app_opens]
        })
        st.table(summary_df)

    # Error handling for data availability
    if filtered_df.empty:
        st.warning("No data available for the selected options. Please try different filters.")

    # Buttons for States, Districts, Postal Codes

    col1, col2, col3 = st.columns(3)

    if data_type == "Transactions":
        with col1:
            if st.button("States"):
                st.subheader("Top 10 States")
                top_states = map_df.nlargest(10, 'Transaction_Amount')[['State', 'Transaction_Amount']]
                top_states['Transaction_Amount'] = top_states['Transaction_Amount'].apply(format_transaction_amount)
                st.table(top_states)

        with col2:
            if st.button("Districts"):
                st.subheader("Top 10 Districts")

                # Filter map_trans_df based on selected year and quarter
                filtered_map_trans_df = map_trans_df[(map_trans_df['Year'] == selected_year) & (map_trans_df['Quarter'] == quarter_num)]

                # Clean and capitalize district names
                filtered_map_trans_df['State'] = filtered_map_trans_df['State'].str.replace("district", "", case=False).str.strip()
                filtered_map_trans_df['State'] = filtered_map_trans_df['State'].apply(lambda x: x.title())

                # Get top 10 districts by Transaction Amount
                top_districts = filtered_map_trans_df.nlargest(10, 'Transaction_amount')[['State', 'Transaction_amount']]

                # Rename the 'State' column to 'Districts'
                top_districts.rename(columns={'State': 'Districts'}, inplace=True)
                top_districts['Transaction_amount'] = top_districts['Transaction_amount'].apply(format_transaction_amount)
                st.table(top_districts)

        with col3:
            if st.button("Postal Codes"):
                st.subheader("Top 10 Postal Codes")

                # Filter top_trans_df based on selected year and quarter
                filtered_top_trans_df = top_trans_df[(top_trans_df['Year'] == selected_year) & (top_trans_df['Quarter'] == quarter_num)]

                # Clean and capitalize postal codes
                filtered_top_trans_df['EntityName'] = filtered_top_trans_df['EntityName'].str.title()

                # Get top 10 postal codes by Transaction Amount
                top_postal_codes = filtered_top_trans_df.nlargest(10, 'Transaction_amount')[['EntityName', 'Transaction_amount']]
                top_postal_codes['Transaction_amount'] = top_postal_codes['Transaction_amount'].apply(format_transaction_amount)
                top_postal_codes.rename(columns={'EntityName': 'Postal Codes'}, inplace=True)
                st.table(top_postal_codes)

    elif data_type == "Users":
        with col1:
            if st.button("States"):
                st.subheader("Top 10 States")
                top_states = map_df.nlargest(10, 'User_Count')[['State', 'User_Count']]
                st.table(top_states)

        with col2:
            if st.button("Districts"):
                st.subheader("Top 10 Districts")

                # Filter map_user_df based on selected year and quarter
                filtered_map_user_df = map_user_df[(map_user_df['Year'] == selected_year) & (map_user_df['Quarter'] == quarter_num)]

                # Clean and capitalize district names
                filtered_map_user_df['State'] = filtered_map_user_df['State'].str.replace("district", "", case=False).str.strip()
                filtered_map_user_df['State'] = filtered_map_user_df['State'].apply(lambda x: x.title())

                # Get top 10 districts by Registered Users
                top_districts = filtered_map_user_df.nlargest(10, 'RegisteredUsers')[['State', 'RegisteredUsers']]

                # Rename the 'State' column to 'Districts'
                top_districts.rename(columns={'State': 'Districts'}, inplace=True)
                st.table(top_districts)

        with col3:
            if st.button("Postal Codes"):
                st.subheader("Top 10 Postal Codes")

                # Filter top_user_df based on selected year and quarter
                filtered_top_user_df = top_user_df[(top_user_df['Year'] == selected_year) & (top_user_df['Quarter'] == quarter_num)]

                # Clean and capitalize postal codes
                filtered_top_user_df['EntityName'] = filtered_top_user_df['EntityName'].str.title()

                # Get top 10 postal codes by Registered Users
                top_postal_codes = filtered_top_user_df.nlargest(10, 'RegisteredUsers')[['EntityName', 'RegisteredUsers']]

                # Rename the 'EntityName' column to 'Postal Codes'
                top_postal_codes.rename(columns={'EntityName': 'Postal Codes'}, inplace=True)
                st.table(top_postal_codes)

elif page == "Query Data":
    st.header("Query Data")

    # Define the queries associated with each question
    queries = {
        "1. Which year has the highest number of transactions?": """
            SELECT Year, COUNT(*) AS Number_of_Transactions
            FROM Aggregated_Transactions
            GROUP BY Year
            ORDER BY Number_of_Transactions DESC
            LIMIT 1;
        """,
        "2. Which year has the highest number of User count?": """
            SELECT Year, SUM(User_Count) AS Total_Users
            FROM Aggregated_Users
            GROUP BY Year
            ORDER BY Total_Users DESC
            LIMIT 1;
        """,
        "3. Which state has the most number of transaction amount?": """
            SELECT State, SUM(Transaction_Amount) AS Total_Transaction_Amount
            FROM Aggregated_Transactions
            GROUP BY State
            ORDER BY Total_Transaction_Amount DESC
            LIMIT 1;
        """,
        "4. Which state has the highest number of User count?": """
            SELECT State, SUM(User_Count) AS Total_User_Count
            FROM Aggregated_Users
            GROUP BY State
            ORDER BY Total_User_Count DESC
            LIMIT 1;
        """,
        "5. Which district has the most number of transaction amount?": """
            SELECT State AS District, SUM(Transaction_amount) AS Total_Transaction_Amount
            FROM Map_Transactions
            GROUP BY State
            ORDER BY Total_Transaction_Amount DESC
            LIMIT 1;
        """,
        "6. Which district has the highest number of User count?": """
            SELECT State AS District, SUM(RegisteredUsers) AS Total_User_Count
            FROM Map_Users
            GROUP BY State
            ORDER BY Total_User_Count DESC
            LIMIT 1;
        """,
        "7. Which year has the most number of registered PhonePe users?": """
            SELECT Year, SUM(User_Count) AS Total_Users
            FROM Aggregated_Users
            GROUP BY Year
            ORDER BY Total_Users DESC
            LIMIT 1;
        """,
        "8. Which year has the most number of PhonePe app opens?": """
            SELECT Year, SUM(User_Count * (User_Percentage / 100)) AS Total_App_Opens
            FROM Aggregated_Users
            GROUP BY Year
            ORDER BY Total_App_Opens DESC
            LIMIT 1;
        """,
        "9. Which transaction category has the highest average amount?": """
            SELECT Transaction_Type, AVG(Transaction_Amount) AS Avg_Transaction_Amount
            FROM Aggregated_Transactions
            GROUP BY Transaction_Type
            ORDER BY Avg_Transaction_Amount DESC
            LIMIT 1;
        """,
        "10. Which Quarter and it's year has the Peak Transaction Period?": """
            SELECT Year, Quarter, SUM(Transaction_Amount) AS Total_Transaction_Amount
            FROM Aggregated_Transactions
            GROUP BY Year, Quarter
            ORDER BY Total_Transaction_Amount DESC
            LIMIT 1;
        """
    }

    # Display the questions and allow users to select one
    question = st.selectbox("Select a question to run the query:", list(queries.keys()))

    if question:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)

        # Execute the selected query
        query = queries[question]
        query_result = pd.read_sql_query(query, conn)

        # Close the database connection
        conn.close()

        if 'District' in query_result.columns:
            query_result['District'] = query_result['District'].str.title()

        # Display the query result in a table
        st.table(query_result)