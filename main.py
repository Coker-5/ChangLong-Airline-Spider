# 没有挂代理的版本

import requests
import json
import execjs
from conda.gateways.connection import InsecureRequestWarning


#   初始化数据
header = {
            'host': 'www.loongair.cn',
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'content-length': '496',
            'accept-encoding': 'gzip',
            'user-agent': 'okhttp/3.12.1'}

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # 取消警告

session = requests.session()

login_url = "https://www.loongair.cn/webhandler.ashx"  # 登录URL

#   账号密码
login_paras = {
                   "ActionType": "AccountService_UserLoginHandler", "SessionId": "",
                   "Args": "{\"UserName\":\"15576136605\",\"Password\":\"Sese950708\",\"Token\":\"\",\"ImgCode\":\"\",\"SaleChannel\":8,\"ConstID\":\"5e4275c4RnTIE51IOyn8PHez13fquwq9VePHCAq1\"}",
                   "MethodName": "AccountService_UserLoginHandler", "AppID": "ClientService",
                   "Parameters": "{\"UserName\":\"15576136605\",\"Password\":\"Sese950708\",\"Token\":\"\",\"ImgCode\":\"\",\"SaleChannel\":8,\"ConstID\":\"5e4275c4RnTIE51IOyn8PHez13fquwq9VePHCAq1\"}"
                }


#   登陆处理
def login():
    login_url = "https://www.loongair.cn/webhandler.ashx"

    login_paras = {"ActionType": "AccountService_UserLoginHandler", "SessionId": "",
                   "Args": "{\"UserName\":\"15576136605\",\"Password\":\"Sese950708\",\"Token\":\"\",\"ImgCode\":\"\",\"SaleChannel\":8,\"ConstID\":\"5e4275c4RnTIE51IOyn8PHez13fquwq9VePHCAq1\"}",
                   "MethodName": "AccountService_UserLoginHandler", "AppID": "ClientService",
                   "Parameters": "{\"UserName\":\"15576136605\",\"Password\":\"Sese950708\",\"Token\":\"\",\"ImgCode\":\"\",\"SaleChannel\":8,\"ConstID\":\"5e4275c4RnTIE51IOyn8PHez13fquwq9VePHCAq1\"}"
                   }

    session.post(url=login_url, headers=header, json=login_paras, verify=False)


#   获取数据
def get_data():
    data_url = "https://www.loongair.cn/webhandler.ashx"

    data_paras = {
        "ActionType": "searchConnectFlights", "SessionId": "",
        "Args": "{\"departureAirportCode\":\"CTU\",\"arriveAirportCode\":\"HGH\",\"departureTime\":\"2023-08-01T 00:00:00\",\"tripType\":1,\"cross\":\"4565168990772300027072\",\"ifNonCompany\":false,\"SaleChannel\":8,\"ConstID\":\"5e4275c4RnTIE51IOyn8PHez13fquwq9VePHCAq1\"}",
        "MethodName": "searchConnectFlights", "AppID": "ClientService",
        "Parameters": "{\"departureAirportCode\":\"CTU\",\"arriveAirportCode\":\"HGH\",\"departureTime\":\"2023-08-01T 00:00:00\",\"tripType\":1,\"cross\":\"4565168990772300027072\",\"ifNonCompany\":false,\"SaleChannel\":8,\"ConstID\":\"5e4275c4RnTIE51IOyn8PHez13fquwq9VePHCAq1\"}"
    }

    resp = session.post(url=data_url, headers=header, json=data_paras, verify=False)
    resp.encoding = "utf-8"
    return resp


#   解析数据
def exec_data(resp):
    print(resp.text)
    json_data = json.loads(resp.text)

    flight_data = json.loads(json_data['Result'])['flightInfos']  # 航班数据

    num = len(flight_data)  # 航班数量

    print(f"航班数量共有：{num}")

    for flight in flight_data:
        # flight_type = flight.get('aircraftType',320)
        # print(flight['aircraftType'])
        # flight_type = flight['aircraftType']
        float_price = flight['floatPrice']  # 浮动航班（解码）
        flight_num = flight['flightNum']
        departure_time = flight['departureTime']  # 航班出发时间
        arrived_time = flight['arriveTime']  # 航班到达时间
        departure_name = flight['departureAirportInfo']['airportName']  # 航班出发机场
        arrived_name = flight['arriveAirportInfo']['airportName']  # 航班到达机场
        flight_price = flight['childCabinInfos'][0]['ticketPrice']  # 航班价格
        with open("get_fli.js","r",encoding="utf-8") as fp:
            comp = fp.read()
        read_fli = execjs.compile(comp).call('dp',flight_num,float_price)  # 航班号
        print(f"航班号：{read_fli}，航班出发点：{departure_name}，航班出发时间：{departure_time}，航班到达点：{arrived_name}，航班到达时间：{arrived_time}，经济舱价格：{flight_price}")


if __name__ == '__main__':
    login()
    resp = get_data()
    exec_data(resp)