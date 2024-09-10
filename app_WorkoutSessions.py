from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
ma = Marshmallow(app)

def get_db_connection():
    db_name = "Fitness_Center_db"
    user = "root"
    password = "XXXXXXX" #PLEASE ENTER USER PASSWORD
    host = "localhost"

    try:
        conn =  mysql.connector.connect(
            database = db_name,
            user = user,
            password = password,
            host=host
        )
        
        print("Connected to MySQL database successfully")
        return conn
    
    except Error as e:
        print(f"Error: {e}")


class WorkoutSchema(ma.Schema):
    member_id = fields.String(required=True)
    session_date = fields.String(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)

    class Meta:
        fields = ('member_id', "session_date", "session_time", "activity", "session_id")

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

@app.route('/')
def home():
    return 'Welcome to the Fitness Center Database'
@app.route("/workoutsessions", methods=["GET"])
def get_workouts():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'Error': "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM WorkoutSessions"

        cursor.execute(query)

        workouts = cursor.fetchall()

        return workouts_schema.jsonify(workouts)
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
        
@app.route("/workoutsessions", methods=["POST"])
def add_workout():
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'Error': "Database connection failed"}), 500
        cursor = conn.cursor()

        new_workout = (workout_data['member_id'], workout_data['session_date'], workout_data['session_time'], workout_data['activity'])
        
        query = "INSERT INTO WorkoutSessions (member_id, session_date, session_time, activity) VALUES (%s, %s, %s, %s)"

        cursor.execute(query, new_workout)
        conn.commit()

        return jsonify({"message": "New workout added successfully"}), 201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/workoutsessions/<int:session_id>", methods=["PUT"])
def update_workout(session_id):
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'Error': "Database connection failed"}), 500
        cursor = conn.cursor()

        updated_workout = (workout_data['member_id'], workout_data['session_date'], workout_data['session_time'], workout_data['activity'], session_id)
                                    
        query = 'UPDATE WorkoutSessions SET member_id = %s, session_date = %s, session_time = %s, activity = %s WHERE session_id = %s'

        cursor.execute(query, updated_workout)
        conn.commit()

        return jsonify({f"message": "Updated workout successfully"}), 201
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/workoutsessions/<int:member_id>", methods=["GET"])
def get_workouts_member(member_id):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'Error': "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)
        view_workouts_member = (member_id,)
        query = "SELECT * FROM WorkoutSessions WHERE member_id = %s"

        cursor.execute(query, view_workouts_member)

        workouts = cursor.fetchall()

        return workouts_schema.jsonify(workouts)
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == '__main__':
    app.run(debug=True)