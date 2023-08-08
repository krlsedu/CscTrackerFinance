from datetime import datetime
import decimal
import json
import re

import requests
from flask import request

from service.Interceptor import Interceptor


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)


class TransactionHandler(Interceptor):
    def __init__(self):
        pass

    def generate_transaction(self, json_info):
        try:
            text_ = json.loads(json_info['text'])
            info_ = text_['textInfo']
            if info_ == '':
                info_ = text_['textBig']
                if info_ == '':
                    info_ = text_['text']
                    if info_ == '':
                        info_ = text_['textSummary']

            title = text_['title']
            if title.find('NuPay') != -1:
                info_ = title + ' ' + info_
            self.transaction(info_, text_)
        except Exception as e:
            print(e)

    def transaction(self, test_str, json_info):
        test_str = test_str.replace('  ', ' ')
        regex = r"(.*) ((.*\$)( | )(([1-9]\d{0,2}(.\d{3})*)|(([1-9]\d*)?\d))(\,\d\d)?)(.*)$"
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
                f = int(json_info['postTime'])
                transaction['type'] = self.get_type(type, status)
                transaction['value'] = self.get_value(value)
                transaction['name'] = self.get_name(status)
                transaction['package_name'] = package
                transaction['app_name'] = app_name
                transaction['text'] = test_str
                fromtimestamp = datetime.fromtimestamp(f / 1000)
                transaction['date'] = fromtimestamp \
                    .strftime('%Y-%m-%d %H:%M:%S')
                self.save_transaction(transaction)

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
        response = requests.post("http://bff:8080/repository/transactions", headers=request.headers, json=transaction)
        print(response)
        print(response.json())
        return response.json(), response.status_code
