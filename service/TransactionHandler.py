import re

import requests
from flask import request

from service.Interceptor import Interceptor


class TransactionHandler(Interceptor):
    def __init__(self):
        pass

    def generate_transaction(self, json_info):
        info_ = json_info['textInfo']
        if info_ == '':
            info_ = json_info['textBig']
            if info_ == '':
                info_ = json_info['text']
                if info_ == '':
                    info_ = json_info['textSummary']
        self.transaction(info_, json_info)

    def transaction(self, test_str, json_info):
        regex = r"(.*) ((.*\$)( | )(([1-9]\d{0,2}(.\d{3})*)|(([1-9]\d*)?\d))(\,\d\d)?)(.*)$"

        try:
            matches = re.finditer(regex, test_str)
            re_match = re.match(regex, test_str)
            if not re_match:
                regex = r"(.*) ((([1-9]\d{0,2}(.\d{3})*)|(([1-9]\d*)?\d))(\,\d\d)?)(.*)$"
                re_match = re.match(regex, test_str)
                if not re_match:
                    regex = r"(.*) ((.*\$)( | |  )(([1-9]\d{0,2}(.\d{3})*)|(([1-9]\d*)?\d))(\,\d\d)?)(.*)$"
                    re_match = re.match(regex, test_str)
            if re_match:
                for matchNum, match in enumerate(matches, start=1):
                    transaction = {}
                    type = match.group(1)
                    value = match.group(2)
                    status = match.group(11)
                    package = json_info['packageName']
                    app_name = json_info['appName']
                    transaction['type'] = self.get_type(type, status)
                    transaction['value'] = self.get_value(value)
                    transaction['name'] = self.get_name(status)
                    transaction['package'] = package
                    transaction['app_name'] = app_name
                    transaction['text'] = test_str
                    self.save_transaction(transaction)
        except:
            print("error")

    def get_type(self, text, status):
        regex = r"(.*)(compra|Compra|Recebemos.*pagamento)(.*)$"
        if re.match(regex, text):
            regex = r"(.*)(não.*autorizada)(.*)$"
            if re.match(regex, status):
                return 'unknown'
            regex = r"(.*)(estornada|cancelada)(.*)$"
            if re.match(regex, status):
                return "income"
            return "outcome"
        else:
            regex = r"(.*)(recebeu.*Pix|Recebemos.*PIX|Recebemos.*transferência|recebeu.*transferência)(.*)$"
            if re.match(regex, text):
                return "income"
        return "unknown"

    def get_value(self, text):
        regex = r"((([1-9]\d{0,2}(.\d{3})*)|(([1-9]\d*)?\d))(\,\d\d))$"
        matches = re.finditer(regex, text)

        for matchNum, match in enumerate(matches, start=1):
            value = match.group(1)
            return float(value.strip().replace('.', '').replace(',', '.'))
        return float(0)

    def get_name(self, text):
        regex = r"(.*)(em )(.*)(foi)(.*)$"
        if re.match(regex, text):
            return re.match(regex, text).group(3).strip()
        else:
            regex = r"(.*)(em )(.*)(\.)$"
            if re.match(regex, text):
                return re.match(regex, text).group(3).strip()
            else:
                regex = r"(.*)(de )(.*)(\.)$"
                if re.match(regex, text):
                    return re.match(regex, text).group(3).strip()
        return "unknown"

    def save_transaction(self, transaction):

        response = requests.get('http://service:5000/service?service=transaction')

        url_ = response.json()['url']+'save'
        response = requests.post(url_, headers=request.headers, json=transaction)
        return response.json(), response.status_code
