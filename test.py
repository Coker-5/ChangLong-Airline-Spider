import concurrent.futures
import random
import threading
import time

import redis
import requests
import json
from fake_useragent import UserAgent
from conda.gateways.connection import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # 取消警告
location = 'fake_useragent.json'
ua = UserAgent(cache_path=location)
session = requests.session()
flights_data = {
    "result": [],
    "need": 0
}
t = int(round(time.time() * 1000))
client = redis.Redis(host="localhost", port=6379, db=1)
phone_client = redis.Redis(host="localhost", port=6379, db=2,decode_responses=True)


def proxy_ip():
    while True:
        time.sleep(random.uniform(0.02, 0.04))
        try:
            key_name = client.randomkey()
            cd_data_redis = client.get(key_name)
            cd_data = str(cd_data_redis.decode())
            break
        except Exception as e:
            print('jiuyuan IP redis:%s' % str(e), flush=True)
    return str(cd_data)


def do_login(start_data):
    global session
    try:
        header = {
            'host': 'www.loongair.cn',
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'content-length': '496',
            'accept-encoding': 'gzip',
            'user-agent': str(ua.random)}
        login_url = "https://www.loongair.cn/webhandler.ashx"  # 登录URL
        #   账号密码
        login_paras = {"ActionType": "AccountService_UserLoginHandler", "SessionId": "",
                       "Args": "{\"UserName\":\"%s\",\"Password\":\"%s\",\"Token\":\"\",\"ImgCode\":\"\",\"SaleChannel\":8,\"ConstID\":\"5e4275c4RnTIE51IOyn8PHez13fquwq9VePHCAq1\"}"%(start_data['username'],start_data['password']),
                       "MethodName": "AccountService_UserLoginHandler", "AppID": "ClientService",
                       "Parameters": "{\"UserName\":\"%s\",\"Password\":\"%s\",\"Token\":\"\",\"ImgCode\":\"\",\"SaleChannel\":8,\"ConstID\":\"5e4275c4RnTIE51IOyn8PHez13fquwq9VePHCAq1\"}"%(start_data['username'],start_data['password'])
                       }
        login_resp = session.post(url=login_url, headers=header, json=login_paras, verify=False)
        status = login_resp.json()
        #  登录状态判断
        if login_resp.status_code == 200:
            if status.get("ErrorCode") == 0:
                return {"resp": login_resp}
            else:
                print(f"账号{start_data['username']}错误")
                return {'error': f"账号出错，{status}"}
        else:
            return {"error": f"登陆出错，状态码{login_resp.status_code}"}
    except Exception as e:
        return {"error": f"login Error{e}"}


def get_data(start_data):
    global session
    start_data['daytime'] = start_data['daytime']+"T 00:00:00"
    data_url = "https://www.loongair.cn/webhandler.ashx"
    header = {
        'host': 'www.loongair.cn',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'content-length': '496',
        'accept-encoding': 'gzip',
        'user-agent': str(ua.random)}
    data_paras = {
        "ActionType": "searchConnectFlights", "SessionId": "",
        "Args": "{\"departureAirportCode\":\"%s\",\"arriveAirportCode\":\"%s\",\"departureTime\":\"%s\",\"tripType\":1,\"cross\":\"4565168990772300027072\",\"ifNonCompany\":false,\"SaleChannel\":8,\"ConstID\":\"5e4275c4RnTIE51IOyn8PHez13fquwq9VePHCAq1\"}"%(start_data['from'],start_data['to'],start_data['daytime']),
        "MethodName": "searchConnectFlights", "AppID": "ClientService",
        "Parameters": "{\"departureAirportCode\":\"%s\",\"arriveAirportCode\":\"%s\",\"departureTime\":\"%s\",\"tripType\":1,\"cross\":\"4565168990772300027072\",\"ifNonCompany\":false,\"SaleChannel\":8,\"ConstID\":\"5e4275c4RnTIE51IOyn8PHez13fquwq9VePHCAq1\"}"%(start_data['from'],start_data['to'],start_data['daytime'])
    }
    if start_data.get('proxy') is None:
        pro_ip = 'null'
    else:
        pro_ip = str(start_data['proxy'])
    try:
        if pro_ip != 'null':
            resp = session.post(url=data_url, json=data_paras, headers=header, proxies={'http': 'http://'+str(pro_ip)},timeout=18,verify=False)
        else:
            resp = session.post(url=data_url, json=data_paras, headers=header, timeout=18, verify=False)
        resp.encoding = "utf-8"
        # 获取数据状态
        if resp.status_code == 200 or resp.status_code == 201:
            result = resp.json()
            result = json.loads(result['Result'])['flightInfos']
            if result:
                json_data = resp.json()
                flight_data = json.loads(json_data['Result'])['flightInfos']  # 航班数据
                for flight in flight_data:
                    threads = threading.Thread(target=thread_data, args=(flight,))
                    threads.start()
                    threads.join()
                print(f"{pro_ip}请求成功")
                time.sleep(1.25)
                return {'data': flights_data}
            else:
                print(resp.text)
                return {'error': f"航班数据为空，{resp.text}"}
        else:

            time.sleep(5)
            if pro_ip != 'null':
                resp = session.post(url=data_url, json=data_paras, headers=header,
                                    proxies={'http': 'http://' + str(pro_ip)}, timeout=18, verify=False)
            else:
                resp = session.post(url=data_url, json=data_paras, headers=header, timeout=18, verify=False)
            resp.encoding = "utf-8"
            if resp.status_code == 200 or resp.status_code == 201:
                result = resp.json()
                result = json.loads(result['Result'])['flightInfos']
                if result:
                    json_data = resp.json()
                    flight_data = json.loads(json_data['Result'])['flightInfos']  # 航班数据
                    for flight in flight_data:
                        threads = threading.Thread(target=thread_data, args=(flight,))
                        threads.start()
                        threads.join()
                    print(f"{pro_ip}请求成功")
                    return {'data': flights_data}
                else:
                    print(resp.text)
                    return {'error': f"航班数据为空，{resp.text}"}
            else:
                print(resp.text)
                return {"error": f"两次获取数据出错，状态码{resp.status_code}"}
    except Exception as e:
        print(resp.text)
        return {"error": f"get_data Error {e}"}


def dp(e, t):
    if e:
        n = e.split("&")
        n = [(int(e) - 7 - t) / (2 + i) for i, e in enumerate(n)]
        return ''.join(chr(int(num)) for num in n)


def thread_data(flight):
    float_price = flight['floatPrice']  # 浮动航班（解码）
    flight_num = flight['flightNum']
    read_fli = dp(flight_num, float_price)  # 航班号
    cabin = dp(flight['cabinInfos'][0]['cabinName'], float_price)  # 舱位信息
    departure_time = flight['departureTime']  # 航班出发时间
    departure_time = departure_time.replace("-", "").replace("T", "").replace(":", "")[:-2]
    arrived_time = flight['arriveTime']  # 航班到达时间
    arrived_time = arrived_time.replace("-", "").replace("T", "").replace(":", "")[:-2]
    departure_name = flight['departureAirportInfo']['airportCode']  # 航班出发机场
    arrived_name = flight['arriveAirportInfo']['airportCode']  # 航班到达机场
    flight_price = flight['childCabinInfos'][0]['ticketPrice']  # 航班价格
    if flight['stopOver'] is False:  # 航班停靠点
        stopcity = ""
    else:
        stopcity = flight['stopOverInfo']['cityName']
    adult_tax = flight['adultTaxRMBTotal']  # 成年税费
    seat = flight['cabinInfos'][0]['leftCount']  # 座位信息
    parse(departure_name, arrived_name, departure_time, arrived_time, read_fli, stopcity, flight_price, adult_tax,
          cabin, seat)


def parse(depAir, arrAir, deptime, arrtime, flightN, stopCities,adultPrice,tax,cabinCode,seats):
    segments = [
        [
            {
                "flightNumber": flightN,
                "depAirport": depAir,
                "depTime": deptime,
                "depTerminal": "",
                "arrAirport": arrAir,
                "arrTime": arrtime,
                "arrTerminal": "",
                "stopCities": stopCities,
                "operatingFlightNumber": "",
                "cabin": cabinCode,
                "cabinClass": "",
                "seats": seats,
                "aircraftCode": "",
                "operating": 0
            }
        ]
    ]
    flights = [
        {
            "segmentsList": segments,
            "currency": "CNY",
            "adultPrice": adultPrice,
            "adultTax": tax,
            "adultTotalPrice": adultPrice + tax
        }
    ]
    flight_re = {
        "_id": f"loongair-{depAir}-{arrAir}-{deptime[:-4]}-{flightN}",
        "flights": flights,
        "status": 0,
        "msg": "",
        "siteCode": "loongair",
        "datetime": deptime[:-4],
        "updatetime": t
    }
    flights_data['result'].append(flight_re)


def depair(start_data):
    # 判断登录状态
    login = do_login(start_data)
    if login.get('error') is None:
        data = get_data(start_data)
        if data.get("error") is None:
            pass
        else:
            print(f"获取数据出错,{data['error']}")
            flights_data['need'] = 1
            flights_data['result'] = []
    else:
        print(f"登陆出错,{login['error']}")
        flights_data['need'] = 1
        flights_data['result'] = []

    # print(flights_data)


if __name__ == '__main__':
    # start_data = {
    #             'from': 'HGH',
    #             'to': 'HRB',
    #             'daytime': '2023-08-20',
    #             'adt_num': 1,
    #             'chd_num': '0',
    #             'inf_num': '0',
    #             'fly_num': '1',
    #             'limit_seat': '1',
    #             'proxy': 'null',
    #             'username': '18974744190',
    #             "password": 'Sese950708'
    #         }
    # print(session.cookies)
    # do_login(start_data)
    # print(depair(start_data))





    # 单线程版
    # num = client.dbsize()
    # for i in range(num):
    #     ip = proxy_ip()
    #     start_data = {
    #         'from': 'HGH',
    #         'to': 'HRB',
    #         'daytime': '2023-08-20',
    #         'adt_num': 1,
    #         'chd_num': '0',
    #         'inf_num': '0',
    #         'fly_num': '1',
    #         'limit_seat': '1',
    #         'proxy': ip,
    #         'username': '18974744190',
    #         "password": 'Sese950708'
    #     }
    #     depair



    #     time.sleep(2)



    # 多线程版
    num = phone_client.keys()
    threads = []
    with concurrent.futures.ThreadPoolExecutor(2) as th:
        try:
            for item in num:
                ip = proxy_ip()
                start_data = {
                    'from': 'HGH',
                    'to': 'HRB',
                    'daytime': '2023-08-30',
                    'adt_num': 1,
                    'chd_num': '0',
                    'inf_num': '0',
                    'fly_num': '1',
                    'limit_seat': '1',
                    'proxy': ip,
                    'username': item,
                    "password": phone_client.get(item)
                }
                future = th.submit(depair, start_data)
                threads.append(future)

            # for future in concurrent.futures.as_completed(threads):
            #     try:
            #         result = future.result()
            #         # 处理任务结果
            #     except Exception as e:
            #         print(f"任务执行出错{e}")
        except Exception as e:
            print(f"假数据或线程问题,{e}")


