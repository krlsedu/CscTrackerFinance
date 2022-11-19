import socket
import time

import requests
import schedule

from service.Interceptor import Interceptor


class LoadBalancerRegister(Interceptor):
    def __init__(self):
        super().__init__()

    def register_service(self, service_name, host_name=None, port=None):
        schedule.every(3).seconds.do(self.register, service_name, host_name, port)
        while True:
            schedule.run_pending()
            time.sleep(1)
        pass

    def register(self, service_name, host_name=None, port=None):
        if host_name is None:
            host_name = socket.gethostname()
        if port is None:
            port = 5000
        pod = {'service': service_name, 'host': host_name, 'port': port}
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post('http://balancer:8080/pod', json=pod, headers=headers)
            if response.status_code < 200 or response.status_code > 299:
                print(pod, response.status_code)
                print(f'Error sending metrics: {response.text}')
            pass
        except Exception as e:
            print(e)
            pass

    def lock_unlock(self, service_name, locked=True, host_name=None):
        if host_name is None:
            host_name = socket.gethostname()
        pod = {'service': service_name, 'host': host_name, 'locked': locked}
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post('http://balancer:8080/lock-unlock', json=pod, headers=headers)
            if response.status_code < 200 or response.status_code > 299:
                print(pod, response.status_code)
                print(f'Error sending metrics: {response.text}')
            pass
        except Exception as e:
            print(e)
            pass
