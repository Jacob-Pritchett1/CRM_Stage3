from flask_app import app
from flask import render_template, redirect, request, session, flash, url_for
from flask_app.models.user import User
from flask_app.models.company import Company
from flask_app.models.notes import Note
import pandas as pd
import os
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/') #Route to landing page
def home():
    return render_template('landing.html')
@app.route('/dashboard') #Only accessed once a user is logged in.
def dash():
    return render_template('index.html')
@app.route('/login', methods=['GET', 'POST']) #Login Hidden Route
def login():
    if request.method == 'POST':
        data = { 'email' : request.form['email']}
        user_in_db = User.get_email(data)
        if not user_in_db:
            flash("Invalid Email/Password. Please try again.")
        elif not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
            flash("Invalid Email/Password. Please try again.")
        else:
            session['user_id'] = user_in_db.id
            session['first_name'] = user_in_db.first_name
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/create_user') #Route to create user form
def register():
    return render_template('create_user.html')

@app.route('/registration/process', methods=['POST']) #Create User Hidden Route
def registered():
    is_valid = User.validate_user(request.form)
    if not is_valid:
        return redirect('/')
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    data = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "role": request.form["role"],
        "email": request.form["email"],
        "password": pw_hash,
        "confirm_password": request.form["confirm_password"]
    }
    User.save(data)
    return redirect("/")

@app.route("/customers") #Route for "My Customers" page
def all_user_customers(): #This function gets all customers that were created by the user that is currently logged in via session.
    user_id = session.get('user_id')
    if user_id is not None:
        companies = Company.get_user_companies(user_id)
        return render_template('my-customers.html', companies=companies)
    else:
        return redirect('/login')
@app.route("/customer_report")
def create_customer_report():
    user_id = session.get('user_id')
    if user_id is not None:
        customers = Company.get_user_companies(user_id)
        return render_template('customer_report.html',customers=customers)
    else: 
        return redirect('login')
from flask import make_response
@app.route("/download_csv")
def download_csv():
    user_id = session.get('user_id')
    if user_id is not None:
        companies = Company.get_user_companies(user_id)
        csv_data = "Company Name, Company Details\n"
        for company in companies:
            csv_data += f'"{company.company_name}", "{company.physical_address}"\n'
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=my-customers.csv'
        return response
    else:
        return redirect('/login')
# @app.route('/csv', methods=['GET', 'POST']) #Route for CSV Upload and POST route for processing CSV
# def upload_csv():
#     if 'file' not in request.files:
#         return "No file part"
#     file = request.files['file']
#     if file.filename == '':
#         return "No selected file"
#     if file:
#         filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#         file.save(filename)
#         df = pd.read_csv(filename)
#         html_table = df.to_html(classes='table table-striped', escape=False, index=False)
#         return render_template('index.html', html_table=html_table)
@app.route("/new/company") #This displays a form for adding a company
def creating_company():
    return render_template("company_creation.html")
@app.route("/new/company/create", methods=['POST']) #Hidden Route
def company_submission(): #Function for creating a company
    if "user_id" not in session: #If user is not validated via session, they are redirected to login
        return redirect('/login')
    if not Company.validate_company(request.form):
        return redirect('/new/company')
    user_id=session["user_id"]
    session["company_name"]= request.form["company_name"]
    session["physical_address"]= request.form["physical_address"]
    session["phone_number"]= request.form["phone_number"]
    data = {
        "company_name": request.form["company_name"],
        "physical_address": request.form["physical_address"],
        "phone_number": request.form["phone_number"],
        "user_id": user_id
    }
    Company.create_company(data)
    return redirect("/dashboard")
@app.route('/edit/<int:id>') #Route to edit company 
def edit_company(id): #Function that will reroute user if not logged in, this will edit the company
    if "user_id" not in session:
        return redirect('/')
    single_company=Company.get_one(id)
    return render_template("edit_post.html", single_company= single_company,id=id)
@app.route('/edit/<int:id>/finalize', methods=["POST"]) #Hidden route for editing the company
def finalize_edit(id):
    if not Company.validate_post(request.form):
        return redirect('/edit/<int:id>')
    data = {
        "company_name": request.form["company_name"],
        "physical_address": request.form["physical_address"],
        "phone_number": request.form["phone_number"],
        "id": id
    }
    Company.edit_company(data)
    return redirect('/index')
@app.route('/company/delete/<int:id>') #Route for deleting company
def delete(id):
    if "user_id" not in session:
        return redirect(url_for('login'))
    Company.delete(id)
    return redirect('/')
@app.route('/notes/<int:user_id>')
def user_notes(user_id):
    print(user_id)
    user_notes = {"id": user_id}
    user= User.users_notes(user_notes)
    return render_template("user_notes.html", user=user, user_id=user_id, user_notes=user_notes)
@app.route('/new/note')
def note_form():
    company_id = request.args.get("company_id")
    company_name = request.args.get("company_name")
    return render_template('notes.html',company_id=company_id,company_name=company_name)
@app.route("/new/note/create", methods=['POST'])
def create_note():
    if not Note.validate_note(request.form):
        return redirect('/')
    if "user_id" not in session:
        return redirect(url_for('login'))
    company_id = request.form["company_id"]
    data = {
        "note": request.form["note"],
        "date": request.form["date"],
        "user_id": session["user_id"],
        "company_id": company_id,
    }
    Note.create_note(data)
    return redirect("/notes")

@app.route('/logout') #Will log the user out
def logging_out():
    session.clear()
    return redirect('/')
if __name__=="__main__":   # Ensure this file is being run directly and not from a different module    
    app.run(debug=True)    # Run the app in debug mode.

