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
        import base64
        import io
        from flask import request

        body = request.get_json(force=True, silent=True)
        if not body or 'file' not in body:
            return {'status': 'error', 'text': 'No file in request body'}, 400
            
        file_b64 = body['file']
        if not file_b64:
            return {'status': 'error', 'text': 'File field is empty'}, 400
            
        if ',' in file_b64:
            file_b64 = file_b64.split(',', 1)[1]
            
        try:
            file_bytes = base64.b64decode(file_b64)
        except Exception as e:
            return {'status': 'error', 'text': f'Invalid base64 format: {str(e)}'}, 400
            
        file_like = io.BytesIO(file_bytes)
        headers = http_repository.get_headers()
        response = transaction_handler.process_b3_dividends(file_like, headers)
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
