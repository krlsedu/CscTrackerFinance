import threading

import requests
from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics

from service.LoadBalancerRegister import LoadBalancerRegister
from service.TransactionHandler import TransactionHandler

app = Flask(__name__)

transaction_handler = TransactionHandler()

# group by endpoint rather than path
metrics = PrometheusMetrics(app, group_by='endpoint')

balancer = LoadBalancerRegister()


def schedule_job():
    balancer.register_service('finance')


t1 = threading.Thread(target=schedule_job, args=())
t1.start()


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
