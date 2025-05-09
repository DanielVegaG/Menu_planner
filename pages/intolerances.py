import streamlit as st
import pandas as pd

# Title of the page
st.title("Intolerances and Diets")

# Load the CSV file
csv_file_path = "Intoleranssit & Ruokavaliot.csv"
data = pd.read_csv(csv_file_path)

# Function to highlight intolerances
def highlight_intolerances(val):
    if val == 1:
        return 'background-color: lightcoral; color: white;'
    elif val == 0:
        return 'background-color: lightgreen; color: black;'
    return ''

# Apply styling to the DataFrame
styled_data = data.style.applymap(highlight_intolerances, subset=data.columns[4:])

# Display the styled table
st.subheader("Intolerances and Diets Table")
st.dataframe(styled_data, use_container_width=True)