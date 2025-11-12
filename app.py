from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from config import API_BASE_URL

app = Flask(__name__)
app.secret_key = "replace-with-a-secure-random-key"

# Helper to build full supplier endpoint
def suppliers_url(path=""):
    base = API_BASE_URL.rstrip("/") + "/suppliers"
    if path:
        return f"{base}/{path}"
    return base

@app.route("/")
def home():
    return render_template("home.html", title="Stationery Supplier Data Management")

@app.route("/about")
def about():
    return render_template("about.html", title="About - Stationery Supplier Data Management")

@app.route("/faq")
def faq():
    return render_template("faq.html", title="FAQ - Stationery Supplier Data Management")

# List suppliers
@app.route("/suppliers")
def suppliers():
    try:
        resp = requests.get(suppliers_url())
        resp.raise_for_status()
        suppliers = resp.json()
    except Exception as e:
        flash(f"Failed to fetch suppliers: {e}", "danger")
        suppliers = []
    return render_template("suppliers.html", suppliers=suppliers, title="Stationery Supplier Data Management")

# New supplier form
@app.route("/supplier/new", methods=["GET", "POST"])
def new_supplier():
    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "contact_person": request.form.get("contact_person"),
            "phone": request.form.get("phone"),
            "email": request.form.get("email"),
            "address": request.form.get("address")
        }
        try:
            r = requests.post(suppliers_url(), json=data)
            r.raise_for_status()
            flash("New stationery supplier added successfully.", "success")
            return redirect(url_for("suppliers"))
        except Exception as e:
            flash(f"Failed to create supplier: {e}", "danger")
    return render_template("supplier_form.html", action="Create", supplier={}, title="Add New Stationery Supplier")

# Edit supplier
@app.route("/supplier/<int:supplier_id>/edit", methods=["GET", "POST"])
def edit_supplier(supplier_id):
    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "contact_person": request.form.get("contact_person"),
            "phone": request.form.get("phone"),
            "email": request.form.get("email"),
            "address": request.form.get("address")
        }
        try:
            r = requests.put(suppliers_url(str(supplier_id)), json=data)
            r.raise_for_status()
            flash("Supplier information updated successfully.", "success")
            return redirect(url_for("suppliers"))
        except Exception as e:
            flash(f"Failed to update supplier: {e}", "danger")
    # GET -> fetch supplier to prefill form
    try:
        r = requests.get(suppliers_url(str(supplier_id)))
        r.raise_for_status()
        supplier = r.json()
    except Exception as e:
        flash(f"Failed to load supplier: {e}", "danger")
        return redirect(url_for("suppliers"))
    return render_template("supplier_form.html", action="Update", supplier=supplier, title="Edit Stationery Supplier Data")

# Delete supplier
@app.route("/supplier/<int:supplier_id>/delete", methods=["POST"])
def delete_supplier(supplier_id):
    try:
        r = requests.delete(suppliers_url(str(supplier_id)))
        r.raise_for_status()
        flash("Supplier deleted successfully from the stationery database.", "success")
    except Exception as e:
        flash(f"Failed to delete supplier: {e}", "danger")
    return redirect(url_for("suppliers"))

# Simple report page (example view report)
@app.route("/report")
def report():
    try:
        r = requests.get(suppliers_url())
        r.raise_for_status()
        suppliers = r.json()
    except Exception as e:
        flash(f"Failed to fetch suppliers for report: {e}", "danger")
        suppliers = []

    total_suppliers = len(suppliers)
    supplier_names = [s.get("name", "") for s in suppliers]
    return render_template(
        "report.html",
        total_suppliers=total_suppliers,
        supplier_names=supplier_names,
        title="Stationery Supplier Report"
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
