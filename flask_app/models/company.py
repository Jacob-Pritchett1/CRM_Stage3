from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app import app
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class Company:
    DB = "crm_db"
    def __init__(self,data):
        self.id = data['id']
        self.company_name = data['company_name']
        self.physical_address = data['physical_address']
        self.phone_number = data['phone_number']
        self.user_id = []
    @classmethod
    def create_company(cls, data):
        query = "INSERT INTO company (company_name, physical_address, phone_number, user_id) VALUES (%(company_name)s, %(physical_address)s, %(phone_number)s, %(user_id)s);"
        result = connectToMySQL(cls.DB).query_db(query, data)
        return result 
    @staticmethod # Validate the user's input when adding a company.
    def validate_company(company):
        is_valid=True
        if len(company["company_name"]) < 1:
            flash("You must enter a Company Name. Please try again.")
            is_valid = False
        if len(company["physical_address"]) < 1:
            flash("You must enter the address of the company. Please try again.")
            is_valid = False
        if len(company[str("phone_number")]) < 1:
            is_valid = False
            flash("Please enter a phone_number.")
        return is_valid
    @classmethod # Just get one company based on the id
    def get_one_company(cls, id):
        query = "SELECT * from company WHERE id = %(id)s;"
        results = connectToMySQL(cls.DB).query_db(query, {"id":id})
        one_company = []
        for row in results:
            one_company.append(cls(row))
        return one_company
    @classmethod
    def get_all_companies(cls):
        query= "SELECT * from company"
        results = connectToMySQL(cls.DB).query_db(query)
        all_companies = []
        for row in results:
            all_companies.append(cls(row))
        return all_companies
    @classmethod
    def get_user_companies(cls,user_id):
        query= "SELECT * from company WHERE user_id = %s"
        data = (user_id,)
        results=connectToMySQL(cls.DB).query_db(query,data)
        user_companies = [cls(row) for row in results]
        return user_companies
    @classmethod
    def edit_company(cls, data):
        query = """ UPDATE company SET company_name=%(company_name)s, physical_address=%(physical_address)s,
        phone_number = %(phone_number)s WHERE id = %(id)s;"""
        return connectToMySQL(cls.DB).query_db(query, data)

    @classmethod
    def delete(cls, id):
        query = "DELETE FROM company WHERE id = %(id)s;"
        data = {"id": id}
        return connectToMySQL(cls.DB).query_db(query,data)
