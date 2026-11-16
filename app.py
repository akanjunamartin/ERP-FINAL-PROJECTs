
import streamlit as st
import sqlite3

st.set_page_config(
    page_title="IronTrack ERP",
    page_icon="⚙️",
    layout="wide"
)

# CONNECT TO DATABASE
conn = sqlite3.connect("irontrack.db")
cursor = conn.cursor()

# CREATE CUSTOMERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    address TEXT
)
""")

# CREATE EQUIPMENT TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_name TEXT NOT NULL,
    serial_number TEXT,
    operating_hours INTEGER,
    condition TEXT,
    problem TEXT
)
""")

# CREATE SPARE PARTS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS spare_parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_name TEXT NOT NULL,
    part_code TEXT,
    quantity INTEGER,
    supplier TEXT
)
""")

# CREATE MAINTENANCE RECORDS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS maintenance_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL,
    maintenance_date TEXT NOT NULL,
    work_done TEXT NOT NULL,
    technician TEXT NOT NULL,
    cost REAL DEFAULT 0,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id)
)
""")

# CREATE SPARE PARTS REQUESTS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS spare_parts_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER,
    part_id INTEGER,
    requested_quantity INTEGER NOT NULL,
    status TEXT NOT NULL,
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment(id),
    FOREIGN KEY (part_id) REFERENCES spare_parts(id)
)
""")

conn.commit()

# SYSTEM TITLE
st.title("IRONTRACK ERP SYSTEM")
st.subheader("IronTrack Equipment Solutions Ltd")

# MODULE NAVIGATION


# USER ROLES AND ACCESS CONTROL

st.sidebar.subheader("Employee Login")

role = st.sidebar.selectbox(
    "Select Employee Role",
    [
        "Manager",
        "Customer Service",
        "Inventory Manager",
        "Technician"
    ]
)

# Assign modules according to employee role
if role == "Manager":
    modules = [
        "Home",
        "Customer Service",
        "Equipment Maintenance",
        "Inventory Management",
        "Spare Parts Requests"
    ]

elif role == "Customer Service":
    modules = [
        "Home",
        "Customer Service"
    ]

elif role == "Inventory Manager":
    modules = [
        "Home",
        "Inventory Management"
    ]

elif role == "Technician":
    modules = [
        "Home",
        "Equipment Maintenance",
        "Spare Parts Requests"
    ]

menu = st.sidebar.selectbox(
    "Select Module",
    modules
)



# HOME MODULE
if menu == "Home":
    st.success("Welcome to IronTrack ERP!")
    st.write("Integrated Equipment Management System")
    st.write(
        "Modules: Customer Service | Equipment Maintenance | Inventory Management"
    )

# CUSTOMER SERVICE MODULE
elif menu == "Customer Service":
    st.header("Customer Service")
    st.subheader("Register a New Customer")

    with st.form("customer_form"):
        name = st.text_input("Customer Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email Address")
        address = st.text_input("Customer Address")

        submitted = st.form_submit_button("Save Customer")

        if submitted:
            if name.strip() and phone.strip():
                cursor.execute(
                    """INSERT INTO customers
                    (name, phone, email, address)
                    VALUES (?, ?, ?, ?)""",
                    (name, phone, email, address)
                )
                conn.commit()
                st.success("Customer registered successfully!")
            else:
                st.error("Enter customer name and phone number.")

    st.divider()
    st.subheader("Registered Customers")

    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    st.dataframe(
        customers,
        column_config={
            0: "Customer ID",
            1: "Customer Name",
            2: "Phone Number",
            3: "Email",
            4: "Address"
        },
        hide_index=True
    )

    st.divider()
    st.subheader("Update Customer Details")

    cursor.execute("SELECT * FROM customers")
    customer_records = cursor.fetchall()

    if customer_records:

        customer_options = {
            f"{c[1]} (ID: {c[0]})": c[0]
            for c in customer_records
        }

        selected_customer = st.selectbox(
            "Select Customer to Update",
            list(customer_options.keys())
        )

        customer_id = customer_options[selected_customer]

        customer = next(
            c for c in customer_records if c[0] == customer_id
        )

        with st.form("update_customer_form"):

            updated_name = st.text_input(
                "Customer Name",
                value=customer[1]
            )

            updated_phone = st.text_input(
                "Phone Number",
                value=customer[2]
            )

            updated_email = st.text_input(
                "Email Address",
                value=customer[3] or ""
            )

            updated_address = st.text_input(
                "Customer Address",
                value=customer[4] or ""
            )

            update_submitted = st.form_submit_button(
                "Update Customer"
            )

            if update_submitted:

                if updated_name.strip() and updated_phone.strip():

                    cursor.execute("""
                        UPDATE customers
                        SET name = ?, phone = ?, email = ?, address = ?
                        WHERE id = ?
                    """, (
                        updated_name,
                        updated_phone,
                        updated_email,
                        updated_address,
                        customer_id
                    ))

                    conn.commit()

                    st.success("Customer details updated successfully!")
                    st.rerun()

                else:
                    st.error("Customer name and phone are required.")

    else:
        st.info("No customers available to update.")

    st.divider()
    st.subheader("Delete Customer Record")

    cursor.execute("SELECT id, name FROM customers")
    delete_customers = cursor.fetchall()

    if delete_customers:

        delete_options = {
            f"{c[1]} (ID: {c[0]})": c[0]
            for c in delete_customers
        }

        with st.form("delete_customer_form"):

            selected_delete_customer = st.selectbox(
                "Select Customer to Delete",
                list(delete_options.keys())
            )

            confirm_delete = st.checkbox(
                "I confirm that I want to delete this customer."
            )

            delete_submitted = st.form_submit_button(
                "Delete Customer"
            )

            if delete_submitted:

                if confirm_delete:

                    customer_id = delete_options[
                        selected_delete_customer
                    ]

                    cursor.execute(
                        "DELETE FROM customers WHERE id = ?",
                        (customer_id,)
                    )

                    conn.commit()

                    st.success("Customer deleted successfully!")
                    st.rerun()

                else:
                    st.error("Please confirm before deleting.")

    else:
        st.info("No customer records available to delete.")

# EQUIPMENT MAINTENANCE MODULE
elif menu == "Equipment Maintenance":
    st.header("Equipment Maintenance")
    st.subheader("Register Equipment")

    with st.form("equipment_form"):
        equipment_name = st.text_input("Equipment Name")
        serial_number = st.text_input("Serial Number")

        operating_hours = st.number_input(
            "Operating Hours",
            min_value=0,
            step=1
        )

        condition = st.selectbox(
            "Equipment Condition",
            ["Good", "Fair", "Poor"]
        )

        problem = st.text_area("Describe Equipment Problem")

        submitted = st.form_submit_button("Save Equipment")

        if submitted:
            if equipment_name.strip():
                cursor.execute(
                    """INSERT INTO equipment
                    (equipment_name, serial_number, operating_hours, condition, problem)
                    VALUES (?, ?, ?, ?, ?)""",
                    (
                        equipment_name,
                        serial_number,
                        operating_hours,
                        condition,
                        problem
                    )
                )
                conn.commit()
                st.success("Equipment registered successfully!")
            else:
                st.error("Please enter the equipment name.")

    st.divider()
    st.subheader("Equipment Records")

    cursor.execute("SELECT * FROM equipment")
    records = cursor.fetchall()

    equipment_data = []

    for record in records:
        service_status = (
            "SERVICE DUE"
            if record[3] >= 500 or record[4] == "Poor"
            else "Normal"
        )

        equipment_data.append({
            "ID": record[0],
            "Equipment": record[1],
            "Serial Number": record[2],
            "Operating Hours": record[3],
            "Condition": record[4],
            "Problem": record[5],
            "Service Status": service_status
        })

    if equipment_data:
        st.dataframe(equipment_data, hide_index=True)
    else:
        st.info("No equipment registered yet.")

    # UPDATE EQUIPMENT DETAILS
    st.divider()
    st.subheader("Update Equipment Details")

    cursor.execute("SELECT * FROM equipment")
    equipment_records = cursor.fetchall()

    if equipment_records:

        equipment_options = {
            f"{e[1]} (ID: {e[0]})": e[0]
            for e in equipment_records
        }

        selected_equipment = st.selectbox(
            "Select Equipment to Update",
            list(equipment_options.keys())
        )

        equipment_id = equipment_options[selected_equipment]

        equipment = next(
            e for e in equipment_records if e[0] == equipment_id
        )

        with st.form("update_equipment_form"):

            updated_name = st.text_input(
                "Equipment Name",
                value=equipment[1]
            )

            updated_serial = st.text_input(
                "Serial Number",
                value=equipment[2] or ""
            )

            updated_hours = st.number_input(
                "Operating Hours",
                min_value=0,
                value=int(equipment[3] or 0),
                step=1
            )

            updated_condition = st.selectbox(
                "Equipment Condition",
                ["Good", "Fair", "Poor"],
                index=["Good", "Fair", "Poor"].index(
                    equipment[4] if equipment[4] in
                    ["Good", "Fair", "Poor"] else "Good"
                )
            )

            updated_problem = st.text_area(
                "Equipment Problem",
                value=equipment[5] or ""
            )

            update_equipment = st.form_submit_button(
                "Update Equipment"
            )

            if update_equipment:

                if updated_name.strip():

                    cursor.execute("""
                        UPDATE equipment
                        SET equipment_name = ?,
                            serial_number = ?,
                            operating_hours = ?,
                            condition = ?,
                            problem = ?
                        WHERE id = ?
                    """, (
                        updated_name,
                        updated_serial,
                        updated_hours,
                        updated_condition,
                        updated_problem,
                        equipment_id
                    ))

                    conn.commit()

                    st.success("Equipment updated successfully!")
                    st.rerun()

                else:
                    st.error("Equipment name is required.")

    else:
        st.info("No equipment available to update.")

   

# DELETE EQUIPMENT
    st.divider()
    st.subheader("Delete Equipment")

    cursor.execute("SELECT * FROM equipment")
    equipment_records = cursor.fetchall()

    if equipment_records:

        equipment_options = {
            f"{e[1]} - {e[2]} (ID: {e[0]})": e[0]
            for e in equipment_records
        }

        with st.form("delete_equipment_form"):

            selected_equipment = st.selectbox(
                "Select Equipment to Delete",
                list(equipment_options.keys())
            )

            equipment_id = equipment_options[selected_equipment]

            confirm_delete = st.checkbox(
                "I confirm that I want to delete this equipment."
            )

            delete_equipment = st.form_submit_button(
                "Delete Equipment"
            )

            if delete_equipment:

                if confirm_delete:

                    # CHECK SPARE PARTS REQUEST HISTORY
                    cursor.execute("""
                        SELECT COUNT(*)
                        FROM spare_parts_requests
                        WHERE equipment_id = ?
                    """, (equipment_id,))

                    request_count = cursor.fetchone()[0]

                    # CHECK MAINTENANCE RECORDS
                    cursor.execute("""
                        SELECT COUNT(*)
                        FROM maintenance_records
                        WHERE equipment_id = ?
                    """, (equipment_id,))

                    maintenance_count = cursor.fetchone()[0]

                    if request_count > 0 or maintenance_count > 0:

                        st.warning(
                            "This equipment has maintenance records "
                            "or spare-parts request history and cannot be deleted."
                        )

                    else:

                        cursor.execute("""
                            DELETE FROM equipment
                            WHERE id = ?
                        """, (equipment_id,))

                        conn.commit()

                        st.success(
                            "Equipment deleted successfully!"
                        )

                        st.rerun()

                else:
                    st.error(
                        "Please confirm before deleting equipment."
                    )

    else:
        st.info("No equipment available to delete.")


# RECORD EQUIPMENT MAINTENANCE
    st.divider()
    st.subheader("Record Equipment Maintenance")

    cursor.execute("SELECT id, equipment_name FROM equipment")
    maintenance_equipment = cursor.fetchall()

    if maintenance_equipment:

        equipment_options = {
            f"{e[1]} (ID: {e[0]})": e[0]
            for e in maintenance_equipment
        }

        with st.form("maintenance_record_form"):

            selected_equipment = st.selectbox(
                "Select Equipment",
                list(equipment_options.keys())
            )

            maintenance_date = st.date_input(
                "Maintenance Date"
            )

            work_done = st.text_area(
                "Describe Work Done"
            )

            technician = st.text_input(
                "Technician Name"
            )

            cost = st.number_input(
                "Maintenance Cost",
                min_value=0.0,
                step=1000.0
            )

            submitted = st.form_submit_button(
                "Save Maintenance Record"
            )

            if submitted:

                if work_done.strip() and technician.strip():

                    equipment_id = equipment_options[selected_equipment]

                    cursor.execute("""
                        INSERT INTO maintenance_records
                        (equipment_id, maintenance_date, work_done, technician, cost)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        equipment_id,
                        str(maintenance_date),
                        work_done,
                        technician,
                        cost
                    ))

                    conn.commit()

                    st.success("Maintenance record saved successfully!")
                    st.rerun()

                else:
                    st.error("Enter the work done and technician name.")

    else:
        st.info("Register equipment before recording maintenance.")

    st.divider()
    st.subheader("Maintenance History")

    cursor.execute("""
        SELECT
            maintenance_records.id,
            equipment.equipment_name,
            maintenance_records.maintenance_date,
            maintenance_records.work_done,
            maintenance_records.technician,
            maintenance_records.cost
        FROM maintenance_records
        JOIN equipment
            ON maintenance_records.equipment_id = equipment.id
        ORDER BY maintenance_records.id DESC
    """)

    maintenance_records = cursor.fetchall()

    if maintenance_records:
        st.dataframe(
            maintenance_records,
            column_config={
                0: "Record ID",
                1: "Equipment",
                2: "Date",
                3: "Work Done",
                4: "Technician",
                5: "Cost"
            },
            hide_index=True
        )
    else:
        st.info("No maintenance records available yet.")

# INVENTORY MANAGEMENT MODULE
elif menu == "Inventory Management":
    st.header("Inventory Management")
    st.subheader("Register Spare Parts")

    with st.form("parts_form"):
        part_name = st.text_input("Spare Part Name")
        part_code = st.text_input("Part Code")

        quantity = st.number_input(
            "Available Quantity",
            min_value=0,
            step=1
        )

        supplier = st.text_input("Supplier Name")

        submitted = st.form_submit_button("Save Spare Part")

        if submitted:
            if part_name.strip():
                cursor.execute(
                    """INSERT INTO spare_parts
                    (part_name, part_code, quantity, supplier)
                    VALUES (?, ?, ?, ?)""",
                    (part_name, part_code, quantity, supplier)
                )
                conn.commit()
                st.success("Spare part registered successfully!")
            else:
                st.error("Please enter the spare part name.")

    st.divider()
    st.subheader("Available Spare Parts")

    cursor.execute("SELECT * FROM spare_parts")
    parts = cursor.fetchall()

    if parts:
        parts_data = []

        for p in parts:
            parts_data.append({
                "ID": p[0],
                "Part Name": p[1],
                "Part Code": p[2],
                "Quantity": p[3],
                "Supplier": p[4],
                "Stock Status": (
                    "LOW STOCK" if p[3] <= 5 else "AVAILABLE"
                )
            })

        st.dataframe(parts_data, hide_index=True)

    else:
        st.info("No spare parts registered yet.")
   
    # RESTOCK EXISTING SPARE PARTS
    st.divider()
    st.subheader("Restock Existing Spare Parts")

    cursor.execute(
        "SELECT id, part_name, part_code, quantity FROM spare_parts"
    )
    restock_parts = cursor.fetchall()

    if restock_parts:
        part_options = {
            f"{p[1]} ({p[2]}) - Current Stock: {p[3]}": p[0]
            for p in restock_parts
        }

        with st.form("restock_form"):
            selected_part = st.selectbox(
                "Select Spare Part",
                list(part_options.keys())
            )

            additional_quantity = st.number_input(
                "Additional Quantity Received",
                min_value=1,
                step=1
            )

            restock_submitted = st.form_submit_button("Add Stock")

            if restock_submitted:
                part_id = part_options[selected_part]

                cursor.execute(
                    """UPDATE spare_parts
                    SET quantity = quantity + ?
                    WHERE id = ?""",
                    (additional_quantity, part_id)
                )

                conn.commit()

                st.success("Stock replenished successfully!")

    else:
        st.info("Register a spare part before restocking.")

    # UPDATE SPARE PARTS DETAILS
    st.divider()
    st.subheader("Update Spare Parts Details")

    cursor.execute("SELECT * FROM spare_parts")
    spare_records = cursor.fetchall()

    if spare_records:

        spare_options = {
            f"{p[1]} (ID: {p[0]})": p[0]
            for p in spare_records
        }

        selected_spare = st.selectbox(
            "Select Spare Part to Update",
            list(spare_options.keys())
        )

        spare_id = spare_options[selected_spare]

        spare = next(
            p for p in spare_records if p[0] == spare_id
        )

        with st.form("update_spare_form"):

            updated_part_name = st.text_input(
                "Spare Part Name",
                value=spare[1]
            )

            updated_part_code = st.text_input(
                "Part Code",
                value=spare[2] or ""
            )

            updated_quantity = st.number_input(
                "Available Quantity",
                min_value=0,
                value=int(spare[3] or 0),
                step=1
            )

            updated_supplier = st.text_input(
                "Supplier Name",
                value=spare[4] or ""
            )

            update_spare = st.form_submit_button(
                "Update Spare Part"
            )

            if update_spare:

                if updated_part_name.strip():

                    cursor.execute("""
                        UPDATE spare_parts
                        SET part_name = ?,
                            part_code = ?,
                            quantity = ?,
                            supplier = ?
                        WHERE id = ?
                    """, (
                        updated_part_name,
                        updated_part_code,
                        updated_quantity,
                        updated_supplier,
                        spare_id
                    ))

                    conn.commit()

                    st.success("Spare part updated successfully!")
                    st.rerun()

                else:
                    st.error("Spare part name is required.")

    else:
        st.info("No spare parts available to update.")

    # DELETE SPARE PART
    st.divider()
    st.subheader("Delete Spare Part")

    cursor.execute("SELECT * FROM spare_parts")
    spare_records = cursor.fetchall()

    if spare_records:

        spare_options = {
            f"{p[1]} (ID: {p[0]})": p[0]
            for p in spare_records
        }

        with st.form("delete_spare_form"):

            selected_spare = st.selectbox(
                "Select Spare Part to Delete",
                list(spare_options.keys())
            )

            spare_id = spare_options[selected_spare]

            confirm_delete = st.checkbox(
                "I confirm that I want to delete this spare part."
            )

            delete_spare = st.form_submit_button(
                "Delete Spare Part"
            )

            if delete_spare:

                if confirm_delete:

                    cursor.execute("""
                        SELECT COUNT(*)
                        FROM spare_parts_requests
                        WHERE part_id = ?
                    """, (spare_id,))

                    request_count = cursor.fetchone()[0]

                    if request_count > 0:
                        st.warning(
                            "This spare part has request history "
                            "and cannot be deleted."
                        )

                    else:
                        cursor.execute("""
                            DELETE FROM spare_parts
                            WHERE id = ?
                        """, (spare_id,))

                        conn.commit()

                        st.success(
                            "Spare part deleted successfully!"
                        )
                        st.rerun()

                else:
                    st.error(
                        "Please confirm before deleting the spare part."
                    )

    else:
        st.info("No spare parts available to delete.")

# SPARE PARTS REQUESTS MODULE
elif menu == "Spare Parts Requests":
    st.header("Spare Parts Requests")
    st.write("Request spare parts for equipment maintenance.")

    # Get registered equipment
    cursor.execute(
        "SELECT id, equipment_name, serial_number FROM equipment"
    )
    equipment_records = cursor.fetchall()

    # Get registered spare parts
    cursor.execute(
        "SELECT id, part_name, part_code, quantity FROM spare_parts"
    )
    parts_records = cursor.fetchall()

    if equipment_records and parts_records:

        equipment_options = {
            f"{e[1]} - ID {e[0]}": e[0]
            for e in equipment_records
        }

        part_options = {
            f"{p[1]} - Stock: {p[3]} - ID {p[0]}": p[0]
            for p in parts_records
        }

        with st.form("spare_parts_request_form"):

            selected_equipment = st.selectbox(
                "Select Equipment",
                list(equipment_options.keys())
            )

            selected_part = st.selectbox(
                "Select Spare Part",
                list(part_options.keys())
            )

            requested_quantity = st.number_input(
                "Quantity Required",
                min_value=1,
                step=1
            )

            submitted = st.form_submit_button("Submit Request")

            if submitted:

                equipment_id = equipment_options[selected_equipment]
                part_id = part_options[selected_part]

                # Check available stock
                cursor.execute(
                    "SELECT quantity FROM spare_parts WHERE id = ?",
                    (part_id,)
                )

                stock_record = cursor.fetchone()

                if stock_record and stock_record[0] >= requested_quantity:

                    # Reduce inventory stock
                    cursor.execute(
                        """UPDATE spare_parts
                        SET quantity = quantity - ?
                        WHERE id = ?""",
                        (requested_quantity, part_id)
                    )

                    request_status = "Approved"

                else:
                    request_status = "Pending"

                # Save the request
                cursor.execute(
                    """INSERT INTO spare_parts_requests
                    (equipment_id, part_id, requested_quantity, status)
                    VALUES (?, ?, ?, ?)""",
                    (
                        equipment_id,
                        part_id,
                        requested_quantity,
                        request_status
                    )
                )

                conn.commit()

                if request_status == "Approved":
                    st.success(
                        "Request approved! Inventory stock has been reduced."
                    )
                else:
                    st.warning(
                        "Request pending. There is not enough stock available."
                    )

    else:
        st.info(
            "Register at least one equipment item and one spare part "
            "before submitting a request."
        )

    st.divider()
    st.subheader("Spare Parts Request History")

    cursor.execute("""
        SELECT
            spare_parts_requests.id,
            equipment.equipment_name,
            spare_parts.part_name,
            spare_parts_requests.requested_quantity,
            spare_parts_requests.status,
            spare_parts_requests.request_date
        FROM spare_parts_requests
        LEFT JOIN equipment
            ON spare_parts_requests.equipment_id = equipment.id
        LEFT JOIN spare_parts
            ON spare_parts_requests.part_id = spare_parts.id
        ORDER BY spare_parts_requests.id DESC
    """)

    request_records = cursor.fetchall()

    if request_records:
        st.dataframe(
            request_records,
            column_config={
                0: "Request ID",
                1: "Equipment",
                2: "Spare Part",
                3: "Quantity",
                4: "Status",
                5: "Request Date"
            },
            hide_index=True
        )
    else:
        st.info("No spare parts requests have been submitted yet.")

conn.close()
