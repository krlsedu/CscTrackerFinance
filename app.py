import json
import re

import psycopg2
from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics

from Message import Message
from service.TransactionHandler import TransactionHandler

app = Flask(__name__)

transaction_handler = TransactionHandler()

# group by endpoint rather than path
metrics = PrometheusMetrics(app, group_by='endpoint')

conn = psycopg2.connect(
    host="postgres",
    database="postgres",
    user="postgres",
    password="postgres")


def read_heartbeats():
    message = Message()
    select_heartbeats = "SELECT " + message.get_cols_select() + " FROM messages where \"text\" like '%com.nu%' or \"text\" like '%com.btg%'"

    cursor, cursor_heartbeats = execute_query(select_heartbeats)

    heartbeats = []
    for row in cursor_heartbeats:
        hb = {}
        for key in message.__dict__:
            hb[key] = row[message.__dict__[key]]
        heartbeats.append(hb)
    cursor.close()
    return heartbeats


def execute_query(select_heartbeats):
    cursor = conn.cursor()
    cursor.execute(select_heartbeats)
    cursor_heartbeats = cursor.fetchall()
    return cursor, cursor_heartbeats


@app.route('/test')
def hello_world():  # put application's code here

    heartbeats = read_heartbeats()

    for heartbeat in heartbeats:
        text_ = heartbeat['text']
        jsonInfo = json.loads(text_)
        transaction_handler.generate_transaction(jsonInfo)
    return 'Hello World!'


@app.route('/transaction', methods=['POST'])
def hello_world():
    transaction_handler.generate_transaction(request.json)
    return request.json, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
