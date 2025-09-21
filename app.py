from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import uuid
import random
import string
from datetime import datetime, timedelta
import re
from decimal import Decimal
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import make_response
from io import BytesIO



app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "cargo_secret_key")

# ---------- DB CONFIG ----------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "cargo_db"
}


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


# ---------- AUTH DECORATORS ----------
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                flash("Please login first.", "warning")
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                flash("Access denied.", "danger")
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return wrapped
    return decorator


# ---------- UTILITIES ----------
def generate_tracking_id():
    return str(uuid.uuid4()).split("-")[0].upper()


# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")


# ---------- AUTH ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role", "customer")  # default role

        if not all([fullname, username, email, password]):
            flash("Please fill all required fields", "warning")
            return redirect(url_for("signup"))

        hashed_pw = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
            existing = cursor.fetchone()
            if existing:
                if existing["username"] == username:
                    flash("Username already exists.", "danger")
                elif existing["email"] == email:
                    flash("Email already registered.", "danger")
                return redirect(url_for("signup"))

            cursor.execute(
                "INSERT INTO users (fullname, username, email, password_hash, role, status) VALUES (%s,%s,%s,%s,%s,%s)",
                (fullname, username, email, hashed_pw, role, "active")
            )
            user_id = cursor.lastrowid

            if role == "customer":
                cursor.execute("INSERT INTO customers (user_id) VALUES (%s)", (user_id,))
            elif role == "employee":
                cursor.execute("INSERT INTO employees (user_id) VALUES (%s)", (user_id,))

            conn.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))

        except Error as e:
            conn.rollback()
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("userType")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users WHERE username=%s AND role=%s", (username, role))
            user = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            flash("Logged in successfully", "success")

            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            elif user["role"] == "employee":
                return redirect(url_for("employee_dashboard"))
            else:
                return redirect(url_for("customer_dashboard"))
        else:
            flash("Invalid credentials or role", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("login"))


# --- helper function ---
def get_customer_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM customers WHERE user_id=%s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result["id"] if result else None


# ---------- CUSTOMER ----------
@app.route("/customer/dashboard")
@login_required(role="customer")
def customer_dashboard():
    user_id = session.get("user_id")
    customer_id = get_customer_id(user_id)

    if not customer_id:
        flash("Customer profile not found!", "danger")
        return redirect(url_for("customer_profile"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM cargo_bookings 
        WHERE customer_id=%s ORDER BY booking_date DESC
    """, (customer_id,))
    shipments = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("customer_dashboard.html", shipments=shipments)

#----customer/book_cargo-----

@app.route("/customer/book_cargo", methods=["GET", "POST"])
@login_required(role="customer")
def customer_book_cargo():
    if request.method == "POST":
        sender_name = request.form.get("sender_name")
        sender_address = request.form.get("sender_address")
        sender_phone = request.form.get("sender_phone")
        recipient_name = request.form.get("recipient_name")
        recipient_address = request.form.get("recipient_address")
        recipient_phone = request.form.get("recipient_phone")
        cargo_description = request.form.get("cargo_description")
        weight = request.form.get("weight")
        package_value = request.form.get("cargo_value")   # renamed to match DB

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 1. Get customer_id from logged in user
            cursor.execute("SELECT id FROM customers WHERE user_id=%s", (session.get("user_id"),))
            result = cursor.fetchone()
            if not result:
                flash("Customer profile not found!", "danger")
                return redirect(url_for("customer_dashboard"))
            customer_id = result[0]

            # 2. Generate tracking ID
            tracking_id = generate_tracking_id()

            # 3. Insert cargo booking (fixed column names)
            cursor.execute("""
                INSERT INTO cargo_bookings 
                (tracking_id, customer_id, sender_name, sender_address, sender_phone, 
                 recipient_name, recipient_address, recipient_phone, cargo_description, 
                 weight, package_value, total_amount, status, expected_delivery_date)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                tracking_id, customer_id, sender_name, sender_address, sender_phone,
                recipient_name, recipient_address, recipient_phone, cargo_description,
                weight, package_value, package_value, "pending", datetime.now().date() + timedelta(days=5)
            ))

            booking_id = cursor.lastrowid

            # 4. Insert initial tracking update
            cursor.execute("""
                INSERT INTO tracking_updates (booking_id, status, location, notes) 
                VALUES (%s, %s, %s, %s)
            """, (booking_id, "pending", "Shipment Booked", "Shipment created by customer"))

            conn.commit()
            flash(f"Cargo booked successfully! Tracking ID: {tracking_id}", "success")
            return redirect(url_for("customer_dashboard"))

        except Exception as e:
            conn.rollback()
            flash(f"Error booking cargo: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("customer_book_cargo.html")


@app.route("/customer/view_invoices")
@login_required(role="customer")
def customer_view_invoices():
    user_id = session.get("user_id")
    customer_id = get_customer_id(user_id)

    if not customer_id:
        flash("Customer profile not found!", "danger")
        return redirect(url_for("customer_dashboard"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT i.*, c.destination_city 
        FROM invoices i 
        JOIN cargo_bookings c ON i.booking_id=c.id 
        WHERE c.customer_id=%s ORDER BY i.issued_at DESC
    """, (customer_id,))
    invoices = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("customer_view_invoices.html", invoices=invoices)        


# --- Download Invoice as PDF ---
@app.route("/customer/invoices/<int:invoice_id>/download")
@login_required(role="customer")
def customer_download_invoice(invoice_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT i.*, b.tracking_id, b.sender_name, b.recipient_name, u.fullname
        FROM invoices i
        JOIN cargo_bookings b ON i.booking_id=b.id
        JOIN customers c ON b.customer_id=c.id
        JOIN users u ON c.user_id=u.id
        WHERE i.id=%s AND u.id=%s
    """, (invoice_id, session.get("user_id")))
    invoice = cursor.fetchone()
    cursor.close()
    conn.close()

    if not invoice:
        flash("Invoice not found or unauthorized.", "danger")
        return redirect(url_for("customer_view_invoices"))

    # Generate PDF in memory
    response = make_response()
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename=invoice_{invoice_id}.pdf"

    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 750, f"Invoice ID: {invoice['id']}")
    pdf.drawString(50, 730, f"Tracking ID: {invoice['tracking_id']}")
    pdf.drawString(50, 710, f"Customer: {invoice['fullname']}")
    pdf.drawString(50, 690, f"Sender: {invoice['sender_name']}")
    pdf.drawString(50, 670, f"Recipient: {invoice['recipient_name']}")
    pdf.drawString(50, 650, f"Amount: ${invoice['amount']}")
    pdf.drawString(50, 630, f"Status: {invoice['status']}")
    pdf.drawString(50, 610, f"Issued At: {invoice['issued_at']}")
    pdf.showPage()
    pdf.save()

    return response


# --- Pay Invoice (mark as paid) ---
@app.route("/customer/invoices/<int:invoice_id>/pay")
@login_required(role="customer")
def customer_pay_invoice(invoice_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE invoices i
            JOIN cargo_bookings b ON i.booking_id=b.id
            JOIN customers c ON b.customer_id=c.id
            SET i.status='paid', i.paid_at=NOW()
            WHERE i.id=%s AND c.user_id=%s
        """, (invoice_id, session.get("user_id")))

        if cursor.rowcount == 0:
            flash("Invoice not found or unauthorized.", "danger")
        else:
            conn.commit()
            flash("Invoice paid successfully!", "success")

    except Exception as e:
        conn.rollback()
        flash(f"Error processing payment: {e}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("customer_view_invoices"))


@app.route("/customer/support", methods=["GET", "POST"])
@login_required(role="customer")
def customer_support():
    if request.method == "POST":
        subject = request.form.get("subject")
        description = request.form.get("description")
        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO support_tickets (user_id, subject, description, status) 
                VALUES (%s,%s,%s,%s)
            """, (user_id, subject, description, "open"))
            conn.commit()
            flash("Support ticket created", "success")
        except Error as e:
            conn.rollback()
            flash(f"Error creating ticket: {e}", "danger")
        finally:
            cursor.close()
            conn.close()
    return render_template("customer_support.html")


@app.route("/customer/profile")
@login_required(role="customer")
def customer_profile():
    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.*, c.* 
        FROM users u 
        LEFT JOIN customers c ON u.id=c.user_id 
        WHERE u.id=%s
    """, (user_id,))
    profile = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("customer_profile.html", profile=profile)

# ---------- EMPLOYEE ----------
@app.route("/employee/dashboard")
@login_required(role="employee")
def employee_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cargo_bookings ORDER BY booking_date DESC LIMIT 50")
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("employee_dashboard.html", bookings=bookings)

# ---------- EMPLOYEE: Shipment History ----------
@app.route("/employee/shipment_history")
@login_required(role="employee")
def employee_shipment_history():
    employee_id = session.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT b.id AS booking_id,
                   b.sender_name,
                   b.recipient_name,
                   b.origin_city,
                   b.destination_city,
                   b.status,
                   b.booking_date,
                   t.location,
                   t.status AS tracking_status,
                   t.updated_at
            FROM cargo_bookings b
            LEFT JOIN tracking_updates t ON b.id = t.booking_id
            WHERE b.assigned_employee_id = %s
            ORDER BY b.booking_date DESC, t.updated_at DESC
        """, (employee_id,))
        history = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template("employee_shipment_history.html", history=history)



@app.route("/employee/update_status", defaults={"booking_id": None}, methods=["GET", "POST"])
@app.route("/employee/update_status/<int:booking_id>", methods=["GET", "POST"])
@login_required(role="employee")
def employee_update_status(booking_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # --- Handle search by tracking_id ---
    tracking_id = request.args.get("tracking_id")
    if booking_id is None and tracking_id:
        cursor.execute("SELECT * FROM cargo_bookings WHERE tracking_id=%s", (tracking_id,))
        booking = cursor.fetchone()
        if booking:
            booking_id = booking["id"]

    if booking_id is None:
        cursor.close()
        conn.close()
        return render_template("employee_update_status.html", booking=None, updates=[])

    if request.method == "POST":
        status = request.form.get("status")
        location = request.form.get("location")
        notes = request.form.get("notes")

        # Update booking
        cursor.execute("UPDATE cargo_bookings SET status=%s WHERE id=%s", (status, booking_id))

        # Insert tracking update
        cursor.execute(
            "INSERT INTO tracking_updates (booking_id, location, status, notes) VALUES (%s,%s,%s,%s)",
            (booking_id, location, status, notes)
        )
        conn.commit()

        flash("Status updated successfully", "success")
        cursor.close()
        conn.close()
        return redirect(url_for("employee_update_status", booking_id=booking_id))

    # Fetch booking + updates
    cursor.execute("SELECT * FROM cargo_bookings WHERE id=%s", (booking_id,))
    booking = cursor.fetchone()
    cursor.execute("SELECT * FROM tracking_updates WHERE booking_id=%s ORDER BY updated_at DESC", (booking_id,))
    updates = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("employee_update_status.html", booking=booking, updates=updates)




# ---------- ADMIN ----------
@app.route("/admin/dashboard")
@login_required(role="admin")
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Stats
        cursor.execute("SELECT COUNT(*) AS total FROM users WHERE role='customer'")
        customers = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM users WHERE role='employee'")
        employees = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM cargo_bookings")
        bookings = cursor.fetchone()["total"]

        # Recent bookings (read-only, no actions)
        cursor.execute("""
            SELECT cb.id, cb.destination_city, cb.status, u.username
            FROM cargo_bookings cb
            JOIN customers c ON cb.customer_id = c.id
            JOIN users u ON c.user_id = u.id
            ORDER BY cb.created_at DESC
            LIMIT 10
        """)
        bookings_list = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template(
        "admin_dashboard.html",
        customers=customers,
        employees=employees,
        bookings=bookings,
        bookings_list=bookings_list
    )



# Manage Customers
@app.route("/admin/manage_customers")
@login_required(role="admin")
def admin_manage_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.*, c.phone, c.address 
        FROM users u 
        LEFT JOIN customers c ON u.id=c.user_id 
        WHERE u.role='customer'
    """)
    customers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin_manage_customers.html", customers=customers)

@app.route("/admin/customers/<int:id>/edit", methods=["GET", "POST"])
@login_required(role="admin")
def edit_customer(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        status = request.form.get("status")
        cursor.execute(
            "UPDATE users SET fullname=%s, email=%s, status=%s WHERE id=%s",
            (fullname, email, status, id)
        )
        conn.commit()
        flash("Customer updated successfully!", "success")
        return redirect(url_for("admin_manage_customers"))
    cursor.execute("SELECT * FROM users WHERE id=%s", (id,))
    customer = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("edit_customer.html", customer=customer)

@app.route("/admin/customers/<int:id>/view")
@login_required(role="admin")
def view_customer(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (id,))
    customer = cursor.fetchone()
    cursor.close()
    conn.close()

    if not customer:
        flash("Customer not found", "warning")
        return redirect(url_for("admin_manage_customers"))

    return render_template("view_customer.html", customer=customer)

@app.route("/admin/customers/<int:id>/activate")
@login_required(role="admin")
def activate_customer(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status='Active' WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Customer activated", "success")
    return redirect(url_for("admin_manage_customers"))


@app.route("/admin/customers/<int:id>/suspend")
@login_required(role="admin")
def suspend_customer(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status='Suspended' WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Customer suspended", "info")
    return redirect(url_for("admin_manage_customers"))



# Manage Employees
@app.route("/admin/manage_employees")
@login_required(role="admin")
def admin_manage_employees():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.*, e.department, e.position 
        FROM users u 
        LEFT JOIN employees e ON u.id=e.user_id 
        WHERE u.role='employee'
    """)
    employees = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin_manage_employees.html", employees=employees) 



# ---------- ADMIN: Employee Registration ----------
@app.route("/admin/employee/register", methods=["GET", "POST"])
@login_required(role="admin")
def admin_employee_registration():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")
        department = request.form.get("department")
        role = request.form.get("role")  # job position
        employment_type = request.form.get("employmentType")
        join_date = request.form.get("joinDate")
        location = request.form.get("location")
        photo = request.files.get("photo")

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # ---------- Generate random password ----------
            raw_password = "".join(random.choices(string.ascii_letters + string.digits, k=10))
            password_hash = generate_password_hash(raw_password)

            # ---------- Insert into users ----------
            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash, role, status) 
                VALUES (%s, %s, %s, %s, %s)
                """,
                (name, email, password_hash, "employee", "active"),
            )
            user_id = cursor.lastrowid

            # ---------- Generate unique employee code ----------
            cursor.execute("SELECT COUNT(*) FROM employees")
            count = cursor.fetchone()[0] + 1
            employee_code = f"EMP{count:03d}"

            # ---------- Insert into employees ----------
            cursor.execute(
                """
                INSERT INTO employees 
                (user_id, employee_code, phone_number, address, department, position, employment_type, hire_date, location, photo) 
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    user_id,
                    employee_code,
                    phone,
                    address,
                    department.lower(),  # must match ENUM in DB
                    role,
                    employment_type,
                    join_date,
                    location,
                    None,  # updated if photo uploaded
                ),
            )
            employee_id = cursor.lastrowid

            # ---------- Handle photo upload ----------
            if photo and photo.filename.strip() != "":
                ext = os.path.splitext(photo.filename)[1]  # keep extension
                filename = f"{employee_code}{ext}"
                upload_folder = os.path.join("static", "uploads", "employees")
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                photo.save(filepath)

                # update employee photo field
                cursor.execute(
                    "UPDATE employees SET photo=%s WHERE employee_id=%s",
                    (filename, employee_id),
                )

            conn.commit()

            # ---------- Optional: send password by email ----------
            # send_email(email, f"Welcome {name}, your login password is: {raw_password}")

            flash(f"Employee registered successfully! Temporary password: {raw_password}", "success")
            return redirect(url_for("admin_employee_registration"))

        except Exception as e:
            conn.rollback()
            flash(f"Error registering employee: {e}", "danger")

        finally:
            cursor.close()
            conn.close()

    return render_template("admin_employee_registration.html")


@app.route("/admin/assign_employee/<int:booking_id>", methods=["GET", "POST"])
@login_required(role="admin")
def admin_assign_employee(booking_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        employee_id = request.form.get("employee_id")
        cursor.execute(
            "UPDATE cargo_bookings SET assigned_employee_id=%s WHERE id=%s",
            (employee_id, booking_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Employee assigned successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    # ✅ Get employees with names from `users`
    cursor.execute("""
        SELECT e.employee_id, u.fullname AS full_name, e.employee_code
        FROM employees e
        JOIN users u ON e.user_id = u.id
    """)
    employees = cursor.fetchall()

    # Get booking details
    cursor.execute("SELECT id, assigned_employee_id FROM cargo_bookings WHERE id=%s", (booking_id,))
    booking = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("admin_assign_employee.html", booking=booking, employees=employees)



@app.route("/admin/update_status/<int:booking_id>", methods=["GET", "POST"])
@login_required(role="admin")
def admin_update_status(booking_id):   
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        new_status = request.form.get("status")
        cursor.execute("UPDATE cargo_bookings SET status=%s WHERE id=%s", (new_status, booking_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Booking status updated successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    cursor.execute("SELECT id, status FROM cargo_bookings WHERE id=%s", (booking_id,))
    booking = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template("admin_update_status.html", booking=booking)



# --------------------------
# Download Invoice
# --------------------------
@app.route("/admin/download_invoice/<int:booking_id>")
@login_required(role="admin")
def admin_download_invoice(booking_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT cb.*, u.username, u.email
        FROM cargo_bookings cb
        JOIN customers c ON cb.customer_id = c.id
        JOIN users u ON c.user_id = u.id
        WHERE cb.id=%s
    """, (booking_id,))
    booking = cursor.fetchone()
    cursor.close()
    conn.close()

    if not booking:
        flash("Booking not found", "danger")
        return redirect(url_for("admin_dashboard"))

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.drawString(100, 750, f"Invoice for Booking #{booking['id']}")
    pdf.drawString(100, 730, f"Tracking ID: {booking['tracking_id']}")
    pdf.drawString(100, 710, f"Customer: {booking['username']} ({booking['email']})")
    pdf.drawString(100, 690, f"Destination: {booking['destination_city'] or 'N/A'}")
    pdf.drawString(100, 670, f"Status: {booking['status']}")
    pdf.drawString(100, 650, f"Total Amount: ₹{booking['total_amount'] or 0}")
    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename=invoice_{booking_id}.pdf"
    return response


@app.route("/admin/employee/<employee_code>/edit")
@login_required(role="admin")
def edit_employee(employee_code):
    # fetch employee details and render edit form
    return render_template("admin_edit_employee.html", employee_code=employee_code)

@app.route("/admin/employee/<employee_code>/activate")
@login_required(role="admin")
def activate_employee(employee_code):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users u 
        JOIN employees e ON u.user_id = e.user_id 
        SET u.status='active' 
        WHERE e.employee_code=%s
    """, (employee_code,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Employee activated successfully", "success")
    return redirect(url_for("admin_manage_employees"))

@app.route("/admin/employee/<employee_code>/deactivate")
@login_required(role="admin")
def deactivate_employee(employee_code):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users u 
        JOIN employees e ON u.user_id = e.user_id 
        SET u.status='inactive' 
        WHERE e.employee_code=%s
    """, (employee_code,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Employee deactivated successfully", "info")
    return redirect(url_for("admin_manage_employees"))



# Manage Cargo (was bookings)
@app.route("/admin/manage_cargo")
@login_required(role="admin")
def admin_manage_cargo():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.*, u.username 
        FROM cargo_bookings b
        JOIN customers c ON b.customer_id = c.id
        JOIN users u ON c.user_id = u.id
        ORDER BY b.booking_date DESC
    """)
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin_manage_cargo.html", bookings=bookings)


# Create Invoice
@app.route("/admin/create_invoice/<int:booking_id>", methods=["POST"])
@login_required(role="admin")
def admin_create_invoice(booking_id):
    amount = request.form.get("amount")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO invoices (booking_id, amount, status) VALUES (%s,%s,%s)",
            (booking_id, amount, "pending")
        )
        conn.commit()
        flash("Invoice created", "success")
    except Error as e:
        conn.rollback()
        flash(f"Error creating invoice: {e}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for("admin_manage_cargo"))

# Track Shipments
@app.route("/admin/track_shipments", methods=["GET", "POST"])
@login_required(role="admin")
def admin_track_shipments():
    tracking_info = None
    tracking_updates = []

    if request.method == "POST":
        tracking_id = request.form.get("tracking_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # 1. Get booking info by tracking_id
            cursor.execute("""
                SELECT b.id AS booking_id, b.tracking_id, b.sender_name, b.sender_address,
                       b.recipient_name, b.recipient_address, b.status,
                       u.fullname AS customer
                FROM cargo_bookings b
                JOIN customers c ON b.customer_id = c.id
                JOIN users u ON c.user_id = u.id
                WHERE b.tracking_id = %s
            """, (tracking_id,))
            tracking_info = cursor.fetchone()

            if tracking_info:
                # 2. Get tracking updates for that booking
                cursor.execute("""
                    SELECT status, location, notes, updated_at
                    FROM tracking_updates
                    WHERE booking_id = %s
                    ORDER BY updated_at DESC
                """, (tracking_info["booking_id"],))
                tracking_updates = cursor.fetchall()

        finally:
            cursor.close()
            conn.close()

    return render_template(
        "admin_track_shipments.html",
        tracking_info=tracking_info,
        tracking_updates=tracking_updates
    )



# Generate Reports
@app.route("/admin/generate_reports", methods=["GET", "POST"])
@login_required(role="admin")
def admin_generate_reports():
    report_type = request.form.get("reportType") if request.method == "POST" else "all"
    date_from = request.form.get("dateFrom") if request.method == "POST" else None
    date_to = request.form.get("dateTo") if request.method == "POST" else None

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # --- Base query ---
    query = """
        SELECT b.id, 
               b.tracking_id,
               b.sender_name, 
               b.recipient_name, 
               b.sender_address, 
               b.recipient_address, 
               b.status, 
               b.booking_date, 
               b.total_amount,
               u.username AS customer
        FROM cargo_bookings b
        JOIN customers c ON b.customer_id = c.id
        JOIN users u ON c.user_id = u.id
        WHERE 1=1
    """
    params = []

    # --- Apply date filter ---
    if date_from:
        query += " AND b.booking_date >= %s"
        params.append(date_from)
    if date_to:
        query += " AND b.booking_date <= %s"
        params.append(date_to)

    query += " ORDER BY b.booking_date DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # --- CSV Header depends on report type ---
    if report_type == "financial":
        lines = ["id,tracking_id,customer,total_amount,status,booking_date"]
        for r in rows:
            lines.append(",".join([
                str(r["id"]),
                r["tracking_id"],
                r["customer"] or "",
                str(r["total_amount"]),
                r["status"],
                str(r["booking_date"])
            ]))
    elif report_type == "shipment":
        lines = ["id,tracking_id,sender,recipient,status,booking_date"]
        for r in rows:
            lines.append(",".join([
                str(r["id"]),
                r["tracking_id"],
                r["sender_name"] or "",
                r["recipient_name"] or "",
                r["status"],
                str(r["booking_date"])
            ]))
    else:
        # default: full details
        lines = ["id,tracking_id,sender,recipient,sender_address,recipient_address,status,booking_date,customer"]
        for r in rows:
            lines.append(",".join([
                str(r["id"]),
                r["tracking_id"],
                r["sender_name"] or "",
                r["recipient_name"] or "",
                r["sender_address"] or "",
                r["recipient_address"] or "",
                r["status"],
                str(r["booking_date"]),
                r["customer"] or ""
            ]))

    resp = "\n".join(lines)
    return (resp, 200, {
        "Content-Type": "text/csv",
        "Content-Disposition": f"attachment; filename={report_type}_report.csv"
    })


# ---------- START ----------
if __name__ == "__main__":
    app.run(debug=True)
