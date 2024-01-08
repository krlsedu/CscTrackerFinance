import decimal
import json
import logging
import re
from datetime import datetime

from csctracker_py_core.repository.http_repository import HttpRepository
from csctracker_py_core.repository.remote_repository import RemoteRepository
from csctracker_py_core.utils.utils import Utils


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)


class TransactionHandler:
    def __init__(self, remote_repository: RemoteRepository, http_repository: HttpRepository):
        self.logger = logging.getLogger()
        self.remote_repository = remote_repository
        self.http_repository = http_repository
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
            self.logger.info(json_info)
            self.logger.exception(e)

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
                try:
                    transaction['name'] = self.get_name(status).replace(' com cartão adicional de SUELEN', '')
                except:
                    transaction['name'] = self.get_name(status)

                transaction['package_name'] = package
                transaction['app_name'] = app_name
                transaction['text'] = test_str
                try:
                    key_ = json_info['key']
                    ##replace all special characters with _
                    key_ = re.sub('[^A-Za-z0-9]+', '_', key_)
                    transaction['key'] = key_
                except:
                    pass
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
        try:
            try:
                exists = self.remote_repository.get_objects("transactions",
                                                                keys=["key"],
                                                                data=transaction,
                                                                headers=self.http_repository.get_headers())
                self.logger.info(exists)
                if exists.__len__() > 0:
                    self.logger.info(f"Transaction already saved-> {transaction['key']} -> {transaction}")
                    Utils.inform_to_client(transaction, "urgent",
                                           self.http_repository.get_headers(),
                                           f"Transaction already saved-> {transaction['key']}")
            except Exception as e:
                self.logger.exception(e)
            response = self.remote_repository.insert("transactions",
                                                     data=transaction,
                                                     headers=self.http_repository.get_headers())
            return response, 201
        except Exception as e:
            self.logger.exception(e)
            return {
                'text': 'transaction not saved',
                'status': 'error',
                'error': str(e)
            }, 400
