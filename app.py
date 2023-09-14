import threading

import requests
from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics

from service.TransactionHandler import TransactionHandler

app = Flask(__name__)

transaction_handler = TransactionHandler()

# group by endpoint rather than path
metrics = PrometheusMetrics(app, group_by='endpoint', default_labels={'application': 'CscTrackerFinance'})


@app.route('/transaction', methods=['POST'])
def transaction():
    try:
        transaction_handler.generate_transaction(request.json)
        return request.json, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        message = {
            'text': 'transaction not saved',
            'status': 'error',
            'error': str(e)
        }
        print(e)
        return message, 400, {'Content-Type': 'application/json'}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
