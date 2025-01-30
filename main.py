import streamlit as st
import pandas as pd
from pytz import timezone
from fpdf import FPDF
from datetime import date, datetime
import os
from PIL import Image


# Set the page configuration to wide layout
st.set_page_config(
    page_title="Daily Planner ",
    page_icon="📝",
    layout="wide",  # This makes the webpage use the full width
    initial_sidebar_state="expanded"  # Sidebar will start expanded
)


    # Directories for tasks and projects
TASKS_DIR = "tasks"
PROJECTS_FILE = "projects.csv"

    # Ensure the task directory exists
if not os.path.exists(TASKS_DIR):
    os.makedirs(TASKS_DIR)
   


user_data_file = "user.csv"

if not os.path.exists(user_data_file):
    pd.DataFrame(columns=["username", "password"]).to_csv(user_data_file, index=False)

    
# Initialize or load project list
def load_projects():
    if os.path.exists(PROJECTS_FILE):
        return pd.read_csv(PROJECTS_FILE)["Project"].tolist()
    return ["DUDP", "JAFURAH-II", "BULL HANINE", "IT", "ADMIN/HR"]

def save_projects(projects):
    pd.DataFrame({"Project": projects}).to_csv(PROJECTS_FILE, index=False)
    # Initialize projects in session state
    if "projects" not in st.session_state:
        st.session_state["projects"] = load_projects()

# Load tasks
def load_tasks(selected_date):
    file_path = os.path.join(TASKS_DIR, f"tasks_{selected_date}.csv")
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame(columns=["Date", "Project", "Task", "Status", "Responsible"])

# Save tasks
def save_tasks(tasks_df, selected_date):
    file_path = os.path.join(TASKS_DIR, f"tasks_{selected_date}.csv")
    tasks_df.to_csv(file_path, index=False)   

    
#load user file and save
def load_user_data():
    return pd.read_csv(user_data_file)
def save_user_data(df):
    df.to_csv(user_data_file, index=False)
def add_user(username, password):
    df = load_user_data()
    df = pd.concat([df, pd.DataFrame([{"username": username, "password": password}])], ignore_index=True)
    save_user_data(df)
def authenticate_user(username, password):
    df = load_user_data()
    user = df[(df["username"] == username) & (df["password"] == password)]
    return user if not user.empty else None

# Login Page
def login():
    st.title("Login")
    username = st.text_input("Enter Username")
    password = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        user = authenticate_user(username, password)
        if user is not None:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            
        else:
            st.error("Invalid credentials!")


def main_app():
    
    # App Header
    col1, col2, col3 = st.columns([1.6, 1, 1])
    with col2:
        logo = Image.open("logo/sketch.png")
        st.image(logo, width=100)


    # Centered title with custom font sizes using HTML
    st.markdown("<h1 style='text-align: center; font-size: 30px; color:blue;'>SKETCHCOM Engineering & Design</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; font-size: 25px;'>Daily Planner</h2>", unsafe_allow_html=True)



    # Step 2: Date Selection (Non-editable, automatically updating)
    selected_date = datetime.now(timezone("Asia/Kolkata")).date()  # Get current date in IST
    tasks_df = load_tasks(selected_date)

    # Display the current date (read-only, fixed)
    st.write(f" Date: {selected_date.strftime('%d %B %Y')}")

    # Step 3: Manage Projects (Add & Remove)
    st.subheader("Manage Projects")
    col1, col2 = st.columns(2)

    # Add Project
    with col1:
        new_project = st.text_input("Add New Project", key="new_project_input")
        if st.button("Add Project"):
            if new_project and new_project not in st.session_state["projects"]:
                st.session_state["projects"].append(new_project)
                save_projects(st.session_state["projects"])  # Save to file
                st.success(f"Project '{new_project}' added successfully!")
            elif new_project in st.session_state["projects"]:
                st.warning(f"Project '{new_project}' already exists!")
            else:
                st.error("Please enter a valid project name.")

    # Remove Project
    with col2:
        project_to_remove = st.selectbox("Remove Project", st.session_state["projects"])
        if st.button("Remove Project"):
            if project_to_remove in st.session_state["projects"]:
                if tasks_df["Project"].eq(project_to_remove).any():
                    st.error(f"Cannot remove '{project_to_remove}' as it has associated tasks!")
                else:
                    st.session_state["projects"].remove(project_to_remove)
                    save_projects(st.session_state["projects"])  # Save to file
                    st.success(f"Project '{project_to_remove}' removed successfully!")

    # Step 4: Task Management
    st.subheader("Task Management")

    # Select Project
    selected_project = st.selectbox("Select Project", st.session_state["projects"], key="selected_project")

    if selected_project:
        # Select Task
        task_names = tasks_df[tasks_df["Project"] == selected_project]["Task"].tolist()
        selected_task = st.selectbox(
            "Select Task",
            options=["Add New Task"] + task_names,
            key="selected_task",
        )

        # Responsible Person
        responsible_names = tasks_df[tasks_df["Project"] == selected_project]["Responsible"].dropna().unique().tolist()
        selected_responsible = st.selectbox(
            "Select Responsible Person",
            options=["Add New Person"] + responsible_names,
            key="selected_responsible",
        )

        if selected_task == "Add New Task":
            task_name = st.text_input("Task Name", value="")
        else:
            task_name = selected_task

        if selected_responsible == "Add New Person":
            responsible_person = st.text_input("Responsible Person", value="")
        else:
            responsible_person = selected_responsible

        # Task Status
        task_status = st.selectbox("Task Status", ["Pending", "In Progress", "Completed"])

        col1, col2, col3 = st.columns(3)

        # Add Task Button
        with col1:
            if st.button("Add Task"):
                if selected_task == "Add New Task" or selected_responsible == "Add New Person":
                    if not tasks_df[
                        (tasks_df["Project"] == selected_project)
                        & (tasks_df["Task"] == task_name)
                        & (tasks_df["Responsible"] == responsible_person)
                        & (tasks_df["Status"] == task_status)
                    ].empty:
                        st.warning("This task already exists!")
                    else:
                        new_task = pd.DataFrame(
                            [{
                                "Date": selected_date,
                                "Project": selected_project,
                                "Task": task_name,
                                "Status": task_status,
                                "Responsible": responsible_person,
                            }]
                        )
                        tasks_df = pd.concat([tasks_df, new_task], ignore_index=True)
                        save_tasks(tasks_df, selected_date)
                        st.success("Task added successfully!")
                else:
                    st.warning("Task already exists or selected for edit.")

        # Save Task After Edit Button
        with col2:
            if st.button("Update Task") and selected_task != "Add New Task":
                tasks_df.loc[
                    (tasks_df["Project"] == selected_project) & (tasks_df["Task"] == selected_task),
                    ["Task", "Status", "Responsible"]
                ] = [task_name, task_status, responsible_person]
                save_tasks(tasks_df, selected_date)
                st.success("Task updated successfully!")

        # Remove Task Button
        with col3:
            if st.button("Remove Task") and selected_task != "Add New Task":
                tasks_df = tasks_df[
                    ~((tasks_df["Project"] == selected_project) & (tasks_df["Task"] == selected_task))
                ]
                save_tasks(tasks_df, selected_date)
                st.success("Task removed successfully!")



    # Step 5: Generate PDF (with IST timezone)
    if not tasks_df.empty:
        if st.button("Generate PDF"):
            class PDF(FPDF):
                def header(self):
                    logo_path = "logo/sketch.png"
                    self.image(logo_path, 5, 4, 16)
                    self.set_font("Arial", style="B", size=14)

                    # Get the current time in IST
                    ist = timezone("Asia/Kolkata")
                    current_time_ist = datetime.now(ist).strftime('%d %B %Y, %I:%M %p')  # Date and Time in IST
                    
                    self.set_font("Arial", style="B", size=14)  # Bold and larger size for "SKETCHCOM"
                    self.cell(180, 8, "SKETCHCOM Engineering and Design", ln=True, align="C")

                    # Second line: Regular font size
                    self.set_font("Arial", style="B", size=12)  # Regular font size for "DAILY DASHBOARD"
                    self.cell(180, 8, "DAILY Planner", ln=True, align="C")
                    self.set_font("Arial", style="B", size=10)
                    self.cell(180, 8, f"{current_time_ist}", ln=True, align="R")  # Display date and time in IST
                    self.ln(5)

                def add_project_section(self, project, tasks):
                    self.set_fill_color(255, 0, 0)
                    self.set_text_color(255, 255, 255)
                    self.set_font("Arial", style="B", size=10)
                    self.cell(180, 8, f"Project: {project}", ln=True, align="L", fill=True)

                    self.set_fill_color(200, 200, 200)
                    self.set_text_color(0, 0, 0)
                    self.set_font("Arial", size=8)
                    self.cell(110, 8, "Assigned Task", border=1, align="C", fill=True)
                    self.cell(30, 8, "Status", border=1, align="C", fill=True)
                    self.cell(40, 8, "Responsible Person", border=1, align="C", fill=True)
                    self.ln()

                    for _, row in tasks.iterrows():
                        self.cell(110, 8, row["Task"], border=1, align="l")
                        if row["Status"] == "Pending":
                            self.set_fill_color(255, 0, 0)
                        elif row["Status"] == "In Progress":
                            self.set_fill_color(255, 255, 0)
                        elif row["Status"] == "Completed":
                            self.set_fill_color(0, 255, 0)
                        self.cell(30, 8, row["Status"], border=1, align="C", fill=True)
                        responsible = str(row["Responsible"]) if not pd.isna(row["Responsible"]) else "N/A"
                        self.cell(40, 8, responsible, border=1, align="C")
                        self.ln()

                    self.ln(5)

                def generate_pdf(self, data, date):
                    self.add_page()
                    grouped = data.groupby("Project")
                    for project, tasks in grouped:
                        self.add_project_section(project, tasks)
                    return self.output(dest="S").encode("latin1")

            pdf = PDF()
            pdf_data = pdf.generate_pdf(tasks_df, selected_date)
            formatted_date = selected_date.strftime('%d-%m-%Y')
            filename = f"dashboard-{formatted_date}.pdf"
            st.download_button("Download PDF", data=pdf_data, file_name=filename, mime="application/pdf")
    else:
        st.info("No tasks available to generate a PDF.")

    st.markdown("")
    st.markdown("")
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["admin_logged_in"] = False
        st.session_state["role"] = None
        st.session_state["username"] = None
        st.query_params["page"] = "login"

        
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("<h2 style='text-align: center; font-size: 15px;'>Terms of Use | Privacy and Security Copyright 2025, SKETCHCOM Engineering & Design Pvt. Ltd. | All Rights Reserved</h2>", unsafe_allow_html=True)



# App Entry Point
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "projects" not in st.session_state:
    st.session_state["projects"] = load_projects()

if st.session_state["logged_in"]:
    main_app()

else:
    page = st.sidebar.selectbox("Choose Action", ["Login"])
    if page == "Login":
        login()
    

    
   
