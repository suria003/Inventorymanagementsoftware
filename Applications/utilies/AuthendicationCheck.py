from flask import jsonify
from DB.db import mysql_connection, Error

class AuthendicationCHK:

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def _userChk(self):
        conn = mysql_connection()
        if conn is None:
            return jsonify({ "message": "DB connection failed.", "Location": "__userChk" }), 500

        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = 'SELECT name FROM users WHERE username = %s'
            value = (self.username,)

            cursor.execute(query, value)
            user = cursor.fetchone()

            if user:
                return True
            else:
                return False

        except Exception:
            return jsonify({ "status": 500, "message": "Internal Server Error"}), 500

        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def _passChk(self):
        conn = mysql_connection()
        if conn is None:
            return jsonify({ "message": "DB connection failed", "Location": "__passChk" }), 500

        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = 'SELECT username FROM users WHERE username = %s AND password = %s'
            value = (self.username, self.password)

            cursor.execute(query, value)
            user = cursor.fetchone()

            if user:
                return True
            else:
                return False

        except Exception:
            return jsonify({ "status": 500, "message": "Internal Server Error"}), 500

        finally:
            if cursor: cursor.close()
            if conn: conn.close()

class AuthendicationCreate:

    def __init__(self, name, username, password, location):
        self.name = name
        self.username = username
        self.password = password
        self.location = location

    def _createAccount(self):
        conn = mysql_connection()
        if conn is None:
            return jsonify({
                "status": 500,
                "message": "DB Connection failed."
            }), 500

        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            query = ''' INSERT INTO users (name, username, password, location) VALUES (%s, %s, %s, %s,) '''
            values = (self.name, self.username, self.password, self.location)

            cursor.execute(query, values)
            conn.commit()

            return jsonify({
                "status": 201,
                "message": "User account created successfully."
            }), 201

        except Error as e:
            conn.rollback()
            return jsonify({
                "status": 500,
                "message": f"Error creating account: {str(e)}"
            }), 500

        finally:
            if cursor:
                cursor.close()
            conn.close()