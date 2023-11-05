from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models.user import User


class Note:
    DB = "crm_db"
    def __init__(self,data):
        self.id= data['id']
        self.note=data['note']
        self.date=data['date']
        self.created_at=data['created_at']
        self.updated_at=data['updated_at']
        self.user_id= None
    @classmethod # Create a new note in the DB
    def create_note(cls, data):
        query = """ INSERT INTO notes (note,date, created_at, updated_at, user_id, company_id)
        VALUES (%(note)s, %(date)s,NOW(), NOW(), %(user_id)s, %(company_id)s);"""
        return connectToMySQL('crm_db').query_db(query, data)
    @staticmethod 
    def validate_note(note):
        is_valid=True
        if len(note["note"]) < 1:
            flash("Your note must have content. Please try again.")
            is_valid = False
        return is_valid
    @classmethod 
    def get_one(cls, id):
        query = "SELECT * from notes WHERE id = %(id)s;"
        results = connectToMySQL(cls.DB).query_db(query, {"id":id})
        one_note = []
        for row in results:
            one_note.append(cls(row))
        return one_note
    @classmethod # get all notes
    def get_all_notes(cls):
        query= "SELECT * from notes"
        results = connectToMySQL(cls.DB).query_db(query)
        all_notes = []
        for row in results:
            all_notes.append(cls(row))
        return all_notes
    @classmethod
    def get_user_notes(cls,user_id):
        query= "SELECT * from notes WHERE user_id = %s"
        data = (user_id,)
        results=connectToMySQL(cls.DB).query_db(query,data)
        user_notes = [cls(row) for row in results]
        return user_notes
    @classmethod
    def edit_note(cls, data):
        query = """ UPDATE notes SET note=%(note)s WHERE id = %(id)s;"""
        return connectToMySQL(cls.DB).query_db(query, data)
    @classmethod
    def delete(cls, id):
        query = "DELETE FROM notes WHERE id = %(id)s;"
        data = {"id": id}
        return connectToMySQL(cls.DB).query_db(query,data)
    @classmethod
    def users_notes(cls, data):
        user_id = data["id"]
        query = "SELECT notes.id, notes.note, notes.date, notes.created_at, notes.updated_at FROM user LEFT JOIN notes ON notes.user_id = user.id WHERE user.id = %(id)s;"
        results = connectToMySQL('crm_db').query_db(query, data)
        print(results)
        user_ = User(results[0])
        notes = []
        for row_from_db in results:
            note_data = {
                "id": row_from_db['id'],
                "note": row_from_db['note'],
                "date": row_from_db['date'],
                "created_at": row_from_db['created_at'],
                "updated_at": row_from_db['updated_at']
            }
            notes.append(cls(note_data))
        user_.notes = notes
        return user_
    @classmethod
    def note_users(cls):
        query= "SELECT * from notes LEFT JOIN user ON user.id = user_id;"
        results= connectToMySQL('users').query_db(query)
        print(results)
        notes = []
        for row_from_db in results:
            note=cls(row_from_db)
            identified_user = { 
                "id":row_from_db["user.id"],
                "first_name":row_from_db["first_name"],
                "last_name":row_from_db["last_name"],
                "role":row_from_db["role"],
                "email":row_from_db["email"],
                "password":row_from_db["password"],
                "created_at":row_from_db["user.created_at"],
                "updated_at":row_from_db["user.updated_at"]
            }
            note = cls(row_from_db)
            note.user = User(identified_user)
            notes.append(note)
        return notes
