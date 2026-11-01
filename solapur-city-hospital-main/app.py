
import os
from flask import Flask, render_template
from db import get_db_connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("APP FILE:", __file__)
print("TEMPLATE PATH:", os.path.join(BASE_DIR, "templates"))
print("TEMPLATE EXISTS:", os.path.isfile(
    os.path.join(BASE_DIR, "templates", "dashboard.html")
))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates")
)

@app.route("/home")
def home():
    return render_template("home.html")




@app.route("/")
def dashboard():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        tables = [
            ("Cities", "City"),
            ("Hospitals", "Hospital"),
            ("Departments", "Department"),
            ("Specializations", "Specialization"),
            ("Facilities", "Facilities"),
            ("Branches", "Hospital_Branch"),
            ("Hospital Timings", "Hospital_Timings"),
            ("Ownership Records", "Hospital_Ownership"),
            ("Rating Records", "Hospital_Ratings"),
        ]

        counts = []

        for label, table in tables:
            cursor.execute(f"SELECT COUNT(*) AS total FROM `{table}`")
            counts.append({
                "label": label,
                "total": cursor.fetchone()["total"]
            })

        cursor.execute("""
            SELECT h.hospital_id, h.hospital_name,
                   h.address, h.contact, c.city_name
            FROM Hospital h
            JOIN City c ON c.city_id = h.city_id
            ORDER BY h.hospital_name
        """)
        hospitals = cursor.fetchall()

        return render_template(
            "dashboard.html",
            counts=counts,
            hospitals=hospitals
        )

    finally:
        cursor.close()
        connection.close()


@app.route("/add-hospital", methods=["GET", "POST"])
def add_hospital():
    from flask import request, redirect, url_for, flash

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT city_id, city_name, state FROM City ORDER BY city_name"
        )
        cities = cursor.fetchall()

        if request.method == "POST":
            hospital_name = request.form.get("hospital_name", "").strip()
            address = request.form.get("address", "").strip()
            contact = request.form.get("contact", "").strip()
            city_id = request.form.get("city_id", "").strip()

            if not hospital_name or not city_id:
                return render_template(
                    "add_hospital.html",
                    cities=cities,
                    error="Hospital name and city are required."
                )

            cursor.execute(
                "SELECT city_id FROM City WHERE city_id = %s",
                (city_id,)
            )
            if not cursor.fetchone():
                return render_template(
                    "add_hospital.html",
                    cities=cities,
                    error="Please select a valid city."
                )

            cursor.execute(
                """
                INSERT INTO Hospital
                    (hospital_name, address, contact, city_id)
                VALUES (%s, %s, %s, %s)
                """,
                (hospital_name, address or None, contact or None, city_id)
            )
            connection.commit()

            return redirect(url_for("dashboard"))

        return render_template("add_hospital.html", cities=cities)

    finally:
        cursor.close()
        connection.close()

@app.route("/cities")
def cities():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT city_id, city_name, state
            FROM City
            ORDER BY city_name
        """)

        cities = cursor.fetchall()

        return render_template(
            "cities.html",
            cities=cities
        )

    finally:
        cursor.close()
        connection.close()
@app.route("/hospitals")
def hospitals():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT h.hospital_id, h.hospital_name,
                   h.address, h.contact, c.city_name
            FROM Hospital h
            JOIN City c ON h.city_id = c.city_id
            ORDER BY h.hospital_name
        """)

        hospitals = cursor.fetchall()
        return render_template("hospitals.html", hospitals=hospitals)

    finally:
        cursor.close()
        connection.close()
def show_module(table_name, page_title):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"SELECT * FROM `{table_name}`")
        records = cursor.fetchall()

        columns = list(records[0].keys()) if records else []

        return render_template(
            "module_table.html",
            title=page_title,
            columns=columns,
            records=records
        )

    finally:
        cursor.close()
        connection.close()


@app.route("/departments")
def departments():
    return show_module("department", "Department Management")


@app.route("/specializations")
def specializations():
    return show_module("specialization", "Specialization Management")


@app.route("/facilities")
def facilities():
    return show_module("facilities", "Facilities Management")


@app.route("/branches")
def branches():
    return show_module("hospital_branch", "Hospital Branch Management")


@app.route("/timings")
def timings():
    return show_module("hospital_timings", "Hospital Timings Management")


@app.route("/ownership")
def ownership():
    return show_module("hospital_ownership", "Hospital Ownership Management")


@app.route("/ratings")
def ratings():
    return show_module("hospital_ratings", "Hospital Ratings Management")
        
if __name__ == "__main__":
    app.run(debug=True,  port=5002)
