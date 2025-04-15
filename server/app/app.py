from flask import Flask, request, jsonify
from utils import helpers 
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, origins=["https://example.com"]) #Change to own domain 

api_key=os.getenv('API_KEY')

@app.route(f"/{api_key}", methods=["GET"])
def get_routes():
    #Retrive arg from api
    date = request.args.get("date")  
    hour_str = request.args.get("hour")  
    vehicle_class_str = request.args.get("vhclass")


    if hour_str is None:
        return {"error": f"Missing 'hour' parameter, {vehicle_class} {date} {hour_str}"}, 400  # Bad Request error
    try:
        #Convert args in correct format
        hour = int(hour_str) 
        vehicle_class = int(vehicle_class_str)
    except ValueError:
        return {"error": "args must be an integer"}, 400  #Bad request error 
    df = helpers.ring_with_speeds(vehicle_class, date, hour)
    if df.empty:
        return jsonify({"error": "No data found for given date/hour"}), 400 #Bad request error 

    df = df[['route', 'path', 'actual_speed', 'speed_category']] 
    return df.to_dict(orient="records")

if __name__ == '__main__':
    debug = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1")
    port = int(os.getenv("FLASK_PORT"))
    app.run(debug=debug, host='0.0.0.0', port=port)