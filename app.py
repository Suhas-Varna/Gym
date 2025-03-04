import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd

# Function to create a database connection
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='suhasvarna',  # Replace with your database name
            user='root',            # Replace with your MySQL username
            password='#goku@2003'   # Replace with your MySQL password
        )
        if connection.is_connected():
            db_info = connection.get_server_info()
            st.sidebar.success(f"Connected to MySQL Server version {db_info}")
            return connection
    except Error as e:
        st.sidebar.error(f"Error while connecting to MySQL: {e}")
        return None

# Function to execute a read query and return results as DataFrame
def execute_read_query(query):
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return pd.DataFrame(result)

# Function to execute a write query
def execute_write_query(query):
    connection = create_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        st.success("Query executed successfully")
    except Error as e:
        st.error(f"Error: {e}")
    cursor.close()
    connection.close()

# Function to check if a record exists
def record_exists(table, id_column, record_id):
    query = f"SELECT EXISTS(SELECT 1 FROM {table} WHERE {id_column} = {record_id})"
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    exists = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return exists

# Function to execute an update query
def execute_update_query(query, table, id_column, record_id):
    if record_exists(table, id_column, record_id):
        connection = create_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            connection.commit()
            st.success("Update successful")
        except Error as e:
            st.error(f"Error: {e}")
        cursor.close()
        connection.close()
    else:
        st.error(f"Error: Record with {id_column} {record_id} does not exist.")

# Function to execute a delete query
def execute_delete_query(query, table, id_column, record_id):
    if record_exists(table, id_column, record_id):
        connection = create_connection()
        cursor = connection.cursor()
        try:
            # Check for and delete related records if needed
            if table == 'member':
                related_query = f"DELETE FROM gym_membership WHERE {id_column} = {record_id}"
                cursor.execute(related_query)
                connection.commit()

            # Now delete the main record
            cursor.execute(query)
            connection.commit()
            st.success("Deletion successful")
        except Error as e:
            st.error(f"Error: {e}")
        cursor.close()
        connection.close()
    else:
        st.error(f"Error: Record with {id_column} {record_id} does not exist.")

# Function to check login credentials
def check_login(username, password):
    return username == "dbms" and password == "1234"

# Streamlit app layout
st.title("Gym Database Management")

# Test the image path
st.image('static/images/gymphoto.jpg')  # Test image loading

# Custom CSS to set background image
def set_background_image():
    st.markdown(
        r"""
        <style>
        .reportview-container {
            background: url('/static/images/gymphoto.jpg');
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    set_background_image()  # Set the background image for the login page

    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_login(username, password):
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.session_state.login_success = True  # Indicate that login was successful
        else:
            st.error("Invalid username or password")
else:
    # Sidebar menu
    menu = [
        "View Members", "View Memberships", "View Gym",
        "View Trainers", "View Workout Classes",
        "Add Member", "Update Member", "Delete Member",
        "Add Membership", "Update Membership", "Delete Membership",
        "Add Trainer", "Update Trainer", "Delete Trainer",
        "Add Workout Class", "Update Workout Class", "Delete Workout Class"
    ]
    choice = st.sidebar.selectbox("Menu", menu)

    # View Members
    if choice == "View Members":
        st.subheader("Members")
        members = execute_read_query("SELECT * FROM member")
        st.dataframe(members)

    # View Memberships
    elif choice == "View Memberships":
        st.subheader("Memberships")
        memberships = execute_read_query("SELECT * FROM gym_membership")
        st.dataframe(memberships)

    # View Gyms
    elif choice == "View Gym":
        st.subheader("Gym")
        gyms = execute_read_query("SELECT * FROM gym")
        st.dataframe(gyms)

    # View Trainers
    elif choice == "View Trainers":
        st.subheader("Trainers")
        trainers = execute_read_query("SELECT * FROM trainer")
        st.dataframe(trainers)

    # View Workout Classes
    elif choice == "View Workout Classes":
        st.subheader("Workout Classes")
        workout_classes = execute_read_query("SELECT * FROM workout_class")
        st.dataframe(workout_classes)

    # Add Member
    elif choice == "Add Member":
        st.subheader("Add New Member")
        member_id = st.number_input("Member ID", min_value=1, step=1)
        name = st.text_input("Name")
        gender = st.selectbox("Gender", ["M", "F"])
        age = st.number_input("Age", min_value=0, step=1)
        phone_no = st.text_input("Phone Number")
        address = st.text_input("Address")
        if st.button("Add Member"):
            if not name or not gender or not age or not phone_no or not address:
                st.error("All fields must be filled out")
            else:
                query = f"INSERT INTO member (member_id, name, gender, age, phone_no, address) VALUES ({member_id}, '{name}', '{gender}', {age}, '{phone_no}', '{address}')"
                execute_write_query(query)

    # Update Member
    elif choice == "Update Member":
        st.subheader("Update Member")
        member_id = st.number_input("Member ID", min_value=1, step=1)
        new_name = st.text_input("New Name")
        new_gender = st.selectbox("New Gender", ["M", "F"])
        new_age = st.number_input("New Age", min_value=0, step=1)
        new_phone_no = st.text_input("New Phone Number")
        new_address = st.text_input("New Address")
        if st.button("Update Member"):
            if not new_name or not new_gender or not new_age or not new_phone_no or not new_address:
                st.error("All fields must be filled out")
            else:
                query = f"""
                UPDATE member
                SET name = '{new_name}', gender = '{new_gender}', age = {new_age}, phone_no = '{new_phone_no}', address = '{new_address}'
                WHERE member_id = {member_id}
                """
                execute_update_query(query, 'member', 'member_id', member_id)

    # Delete Member
    elif choice == "Delete Member":
        st.subheader("Delete Member")
        member_id = st.number_input("Member ID to Delete", min_value=1, step=1)
        if st.button("Delete Member"):
            query = f"DELETE FROM member WHERE member_id = {member_id}"
            execute_delete_query(query, 'member', 'member_id', member_id)

    # Add Trainer
    elif choice == "Add Trainer":
        st.subheader("Add New Trainer")
        trainer_id = st.number_input("Trainer ID", min_value=1, step=1)
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0, step=1)
        phone_no = st.text_input("Phone Number")
        if st.button("Add Trainer"):
            if not name or not age or not phone_no:
                st.error("All fields must be filled out")
            else:
                query = f"INSERT INTO trainer (trainer_id, name, age, phone_no) VALUES ({trainer_id}, '{name}', {age}, '{phone_no}')"
                execute_write_query(query)

    # Update Trainer
    elif choice == "Update Trainer":
        st.subheader("Update Trainer")
        trainer_id = st.number_input("Trainer ID", min_value=1, step=1)
        new_name = st.text_input("New Name")
        new_age = st.number_input("New Age", min_value=0, step=1)
        new_phone_no = st.text_input("New Phone Number")
        if st.button("Update Trainer"):
            if not new_name or not new_age or not new_phone_no:
                st.error("All fields must be filled out")
            else:
                query = f"""
                UPDATE trainer
                SET name = '{new_name}', age = {new_age}, phone_no = '{new_phone_no}'
                WHERE trainer_id = {trainer_id}
                """
                execute_update_query(query, 'trainer', 'trainer_id', trainer_id)

    # Delete Trainer
    elif choice == "Delete Trainer":
        st.subheader("Delete Trainer")
        trainer_id = st.number_input("Trainer ID to Delete", min_value=1, step=1)
        if st.button("Delete Trainer"):
            query = f"DELETE FROM trainer WHERE trainer_id = {trainer_id}"
            execute_delete_query(query, 'trainer', 'trainer_id', trainer_id)

    # Add Workout Class
    elif choice == "Add Workout Class":
        st.subheader("Add New Workout Class")
        workout_id = st.number_input("Workout ID", min_value=1, step=1)
        workout_name = st.text_input("Workout Name")
        if st.button("Add Workout Class"):
            if not workout_name:
                st.error("Workout Name must be filled out")
            else:
                query = f"INSERT INTO workout_class (workout_id, workout_name) VALUES ({workout_id}, '{workout_name}')"
                execute_write_query(query)

    # Update Workout Class
    elif choice == "Update Workout Class":
        st.subheader("Update Workout Class")
        workout_id = st.number_input("Workout ID", min_value=1, step=1)
        new_workout_name = st.text_input("New Workout Name")
        if st.button("Update Workout Class"):
            if not new_workout_name:
                st.error("New Workout Name must be filled out")
            else:
                query = f"""
                UPDATE workout_class
                SET workout_name = '{new_workout_name}'
                WHERE workout_id = {workout_id}
                """
                execute_update_query(query, 'workout_class', 'workout_id', workout_id)

    # Delete Workout Class
    elif choice == "Delete Workout Class":
        st.subheader("Delete Workout Class")
        workout_id = st.number_input("Workout ID to Delete", min_value=1, step=1)
        if st.button("Delete Workout Class"):
            query = f"DELETE FROM workout_class WHERE workout_id = {workout_id}"
            execute_delete_query(query, 'workout_class', 'workout_id', workout_id)

        # Add Membership
    elif choice == "Add Membership":
        st.subheader("Add New Membership")
        membership_id = st.number_input("Membership ID", min_value=1, step=1)
        member_id = st.number_input("Member ID", min_value=1, step=1)
        price = st.number_input("Price", min_value=0.0, step=0.01)
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        gym_name = st.text_input("Gym", value="FitZone", disabled=True)  # Default gym name and non-editable
        
        if st.button("Add Membership"):
            connection = create_connection()
            cursor = connection.cursor()
            
            # Check if the member exists
            query_check_member = f"SELECT COUNT(*) FROM member WHERE member_id = {member_id}"
            cursor.execute(query_check_member)
            member_exists = cursor.fetchone()[0]
            
            if not member_exists:
                st.error("Member ID does not exist.")
            else:
                # Check if the member already has a membership
                query_check_membership = f"SELECT COUNT(*) FROM gym_membership WHERE member_id = {member_id}"
                cursor.execute(query_check_membership)
                membership_exists = cursor.fetchone()[0]

                if membership_exists > 0:
                    st.error("This member already has a membership.")
                else:
                    if not start_date or not end_date:
                        st.error("All fields must be filled out")
                    else:
                        query = f"""
                        INSERT INTO gym_membership (membership_id, member_id, price, start_date, end_date, gym_name)
                        VALUES ({membership_id}, {member_id}, {price}, '{start_date}', '{end_date}', '{gym_name}')
                        """
                        execute_write_query(query)

            cursor.close()
            connection.close()



    # Update Membership
    elif choice == "Update Membership":
        st.subheader("Update Membership")
        membership_id = st.number_input("Membership ID", min_value=1, step=1)
        new_price = st.number_input("New Price", min_value=0.0, step=0.01)
        new_start_date = st.date_input("New Start Date")
        new_end_date = st.date_input("New End Date")
        if st.button("Update Membership"):
            if not new_start_date or not new_end_date:
                st.error("All fields must be filled out")
            else:
                query = f"""
                UPDATE gym_membership
                SET price = {new_price}, start_date = '{new_start_date}', end_date = '{new_end_date}'
                WHERE membership_id = {membership_id}
                """
                execute_update_query(query, 'gym_membership', 'membership_id', membership_id)

    # Delete Membership
    elif choice == "Delete Membership":
        st.subheader("Delete Membership")
        membership_id = st.number_input("Membership ID to Delete", min_value=1, step=1)
        if st.button("Delete Membership"):
            query = f"DELETE FROM gym_membership WHERE membership_id = {membership_id}"
            execute_delete_query(query, 'gym_membership', 'membership_id', membership_id)
