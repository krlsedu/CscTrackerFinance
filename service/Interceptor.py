import time
from threading import Thread

import requests


class Interceptor:
    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        if hasattr(attr, '__call__') and name != 'send_logs':
            def newfunc(*args, **kwargs):
                start = time.time() * 1000
                result = attr(*args, **kwargs)
                new_thread = Thread(target=self.send_logs, args=(attr.__module__, name, start))
                new_thread.start()
                return result

            return newfunc
        else:
            return attr

    def send_logs(self, className, methodName, start):
        execution_time = int(time.time() * 1000 - start)
        clazz = className[className.rfind('.') + 1:className.__len__()]
        metrics = {'clazz': clazz, 'method': methodName, 'executionTime': execution_time,
                   'appName': 'CscTrackerDataSource', 'fullClassName': className}

        response = requests.post('http://metrics-service:5000/metric', json=metrics)
