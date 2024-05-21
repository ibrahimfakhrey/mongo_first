from flask import Flask, render_template, request, redirect, url_for, jsonify
from pymongo import MongoClient
from passlib.hash import bcrypt



app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
db.users.update_many({}, {"$set": {"password": "default_password"}})

@app.route('/')
def index():
    users = list(db.users.find())# Fetch all users from MongoDB
    user_weather_data = {}  # Dictionary to store weather data for each user


    # Iterate through each user and fetch their weather data
    for user in users:
        user_id = user['_id']  # Assuming user_id is stored as '_id' in MongoDB
        weather_data = list(db.weather.find({'user_id': str(user_id)}))  # Fetch weather data for the user
        user_weather_data[user_id] = weather_data  # Store weather data in dictionary

    return render_template('index.html', users=users, user_weather_data=user_weather_data)
@app.route('/create_weather_collection', methods=['GET'])
def create_weather_collection():
    # Define the schema for the weather collection
    weather_collection_schema = {
        "name": "Weather Document",
        "weather": "Sunny",
        "times": ["morning", "afternoon", "evening"],
        "user_id": "<user_id>"
    }

    # Create the weather collection in MongoDB
    db.create_collection('weather')

    # Insert a sample document to ensure the collection is created
    db.weather.insert_one(weather_collection_schema)

    return jsonify({'message': 'Weather collection created successfully'})
@app.route('/add_user', methods=['POST'])
def add_user():
    # Add a new user to MongoDB
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    db.users.insert_one({'name': name, 'email': email, 'password': bcrypt.hash(password)})
    return redirect(url_for('index'))
# Define other routes for updating, deleting, etc.

@app.route('/add_weather', methods=['POST'])
def add_weather():
    user_id = request.form['user_id']
    weather = request.form['weather']
    times = request.form['times']

    # Insert weather data into MongoDB
    db.weather.insert_one({'user_id': user_id, 'weather': weather, 'times': times})

    # Redirect back to the form or any other page
    return redirect('/')


@app.route('/get_weather/<user_id>', methods=['GET'])
def get_weather(user_id):
    # Fetch weather data for the specified user_id from MongoDB
    weather_data = list(db.weather.find({'user_id': user_id}))

    # Convert ObjectId to string for JSON serialization
    for item in weather_data:
        item['_id'] = str(item['_id'])

    # Return the weather data as JSON
    return jsonify(weather_data)
if __name__=="__main__":
    app.run(debug=True)