from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app import app
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


class User: 
    DB = "crm_db"
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.role = data['role']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.company = None
        self.notes = []
    @classmethod #save method will create a user in the database
    def save(cls, data):
        query="INSERT INTO user (first_name, last_name, role, email, password) VALUES (%(first_name)s, %(last_name)s,%(role)s, %(email)s, %(password)s);"
        result = connectToMySQL(cls.DB).query_db(query, data)
        return result
    @staticmethod
    def validate_user(user):
        is_valid = True
        if len(user['first_name']) < 2:
            flash("First Name must be at least 2 characters. Please try again.")
            is_valid=False
        if len(user['last_name']) < 2:
            flash("Last Name must be at least 2 characters. Please try again.")
            is_valid=False
        if len(user['password']) < 8:
            flash("Passwords must be at least 8 characters long. Please try again.")
            is_valid = False
        if user['confirm_password'] != user['password']:
            flash("The passwords you have entered do not match. Please try again. ")
            is_valid = False
        if not EMAIL_REGEX.match(user['email']):
            flash("Invalid email address. Please try again.")
            is_valid=False
        return is_valid
    @classmethod
    def get_all_users(cls):
        query = "SELECT * FROM user;"
        results = connectToMySQL('crm_db').query_db(query)
        users = []
        for user in results:
            users.append(cls(user))
        return users
    @classmethod
    def users_notes(cls, user_id):
        from flask_app.models.notes import Note

        query = """
        SELECT user.id, user.first_name, user.last_name, user.role, user.email, user.password, user.created_at, user.updated_at, notes.id, notes.note, notes.date, notes.created_at, notes.updated_at
        FROM user
        LEFT JOIN notes ON notes.user_id = user.id
        WHERE user.id = %(user_id)s;
        """
        data = {"user_id": user_id}

        results = connectToMySQL('crm_db').query_db(query, data)
        user = cls(results[0]) if results else None
        notes = []
        for row in results:
            if row['id'] and row['note']:
                note_data = {
                    "id": row['id'],
                    "note": row['note'],
                    "date": row['date'],
                    "created_at": row['created_at'],
                    "updated_at": row['updated_at']
                }
                notes.append(Note(note_data))
        user.notes = notes
        return user    
    @classmethod
    def get_email(cls, data):
        query = "SELECT * FROM user WHERE email = %(email)s;"
        result= connectToMySQL("crm_db").query_db(query,data)
        print(result)
        if len(result) < 1:
            return False
        return cls(result[0])
