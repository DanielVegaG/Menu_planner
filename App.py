import streamlit as st

# Title of the app
st.title("My First Streamlit App")

# Input from the user
name = st.text_input("Enter your name:")

# Display a message
if name:
    st.write(f"Hello, {name}! Welcome to Streamlit!")