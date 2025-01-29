import streamlit as st

# Login credentials (for demonstration purposes)
USER_CREDENTIALS = {"admin": "password123", "user1": "pass456"}

# Check if the user is already logged in using session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

def login_page():
    st.title("Login Page")
    st.markdown("Please enter your credentials to access the app.")

    # Username and password input
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Login button
    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state["logged_in"] = True
            st.success("Login successful! Redirecting to the dashboard...")
            st.session_state["redirect"] = True  # Flag to indicate redirect
            
        else:
            st.error("Invalid username or password.")

# Main logic of the app when logged in
if st.session_state["logged_in"]:
    # Import main app after login
    import main  # Import the main app file (main.py)
else:
    login_page()  # Display the login page when not logged in
