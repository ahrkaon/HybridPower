from flask import Flask, render_template, jsonify, json, request, redirect, url_for, flash
from flask_mqtt import Mqtt
import cx_Oracle
from SqlQuery import user_conn, check

app = Flask(__name__)
#app.config['MQTT_BROKER_URL'] = '192.168.0.8'
app.config['MQTT_BROKER_URL'] = '175.206.149.150'
app.config['MQTT_BROKER_PORT'] = 9002
app.config['MQTT_REFRESH_TIME'] = 1.0

mqtt = Mqtt(app)

sensor_data = []

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe("Sensor")

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    payload = message.payload.decode()
    payload_json = json.loads(payload)  # Convert payload to JSON object
    sensor_data.append(payload_json)  # Append JSON object to sensor_data list
    if len(sensor_data) > 10:
        sensor_data.pop(0)

#connection = cx_Oracle.connect(user_conn())
connection = user_conn()
cursor = connection.cursor()

@app.route('/')
def index():
    return render_template('index.html', sensor_data=sensor_data)
@app.route('/results')
def results():
    return render_template('results.html')
@app.route('/update-data')
def update_data():
    return jsonify(sensor_data[-1] if sensor_data else 0)
@app.route('/query', methods=['POST'])
def query_dht11_data():
    connection = user_conn()
    cursor = connection.cursor()
    check(cursor, connection)
    cursor.execute("SELECT vol, cur, watt FROM SENSORDATA")
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(result)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
