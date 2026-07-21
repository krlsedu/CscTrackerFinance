import logging

from csctracker_py_core.starter import Starter

from service.TransactionHandler import TransactionHandler

starter = Starter()
app = starter.get_app()
http_repository = starter.get_http_repository()
transaction_handler = TransactionHandler(starter.remote_repository, http_repository)
logger = logging.getLogger()


@app.route('/transaction', methods=['POST'])
def transaction():
    try:
        transaction_handler.generate_transaction(http_repository.get_json_body())
        return http_repository.get_json_body(), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        message = {
            'text': 'transaction not saved',
            'status': 'error',
            'error': str(e)
        }
        logger.exception(e)
        return message, 400, {'Content-Type': 'application/json'}


@app.route('/transactions', methods=['POST'])
def transactions():
    try:

        json = http_repository.get_json_body()
        if not isinstance(json, list):
            transactions = [json]
        else:
            transactions = json
        transaction_handler.save_transactions(transactions, http_repository.get_headers())

        message = {
            'text': 'transaction saved',
            'status': 'success'
        }
        return message, 201, {'Content-Type': 'application/json'}
    except Exception as e:
        message = {
            'text': 'transaction not saved',
            'status': 'error',
            'error': str(e)
        }
        logger.exception(e)
        return message, 400, {'Content-Type': 'application/json'}


@app.route('/transactions/dividends', methods=['POST'])
def process_dividends():
    try:
        from flask import request
        if 'file' not in request.files:
            return {'status': 'error', 'text': 'No file in request'}, 400
        
        file = request.files['file']
        if file.filename == '':
            return {'status': 'error', 'text': 'No file selected'}, 400
            
        headers = http_repository.get_headers()
        response = transaction_handler.process_b3_dividends(file, headers)
        return response, 201, {'Content-Type': 'application/json'}
    except Exception as e:
        message = {
            'text': 'dividends not processed',
            'status': 'error',
            'error': str(e)
        }
        logger.exception(e)
        return message, 400, {'Content-Type': 'application/json'}


starter.start()
