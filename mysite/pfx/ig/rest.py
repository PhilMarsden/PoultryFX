from socket import gethostname
from rest_framework import status
import requests
import json
import os
from pfx.models import Member
from django.conf import global_settings

if os.environ.get('DJANGO_DEVELOPMENT', None):
    ig_apikey = "363fcb5c8b48e173ca115738967de2534021686d"
    ig_identifier = "phildemo2"
    ig_password = "Jellyfish_123"
    ig_password = "UNKNOWN"
    ig_url = "https://demo-api.ig.com/gateway/deal/"
elif os.environ.get('DJANGO_PRODUCTION', None):
    ig_apikey = "3d7e3de3996b7ca0187a3964522a3125df13d641"
    ig_identifier = "philmarsden"
    ig_password = "UNKNOWN"
    ig_url = "https://api.ig.com/gateway/deal/"
else:
    raise Exception("Please set one of DJANGO_DEVELOPMENT or DJANGO_PRODUCTION")

ig_securitytoken = ""
ig_cst = ""
ig_account_id = ""

class ig_rest:
    @staticmethod
    def need_password():
        if (ig_password == "UNKNOWN"):
            #print("Password UNKNOWN")
            return True
        else:
            #print("Password entered")
            return False

    @staticmethod
    def need_login():
        if (ig_cst == ""):
            #print("Login Needed")
            return True
        else:
            #print("CST Set - Login performed")
            return False

    @staticmethod
    def get_identifier():
            return ig_identifier

    @staticmethod
    def set_password(password):
        global ig_password
        ig_password = password

    @staticmethod
    def login():
        global ig_password
        body = {
            "identifier": ig_identifier,
            "password": ig_password
        }
        headers = {
            "X-IG-API-KEY": ig_apikey
        }

        resp = requests.post(ig_url + 'session', json=body, headers=headers)

        if (resp.status_code == 200):
            global ig_cst,ig_securitytoken,ig_account_id
            ig_cst = resp.headers["CST"]
            ig_securitytoken = resp.headers["X-SECURITY-TOKEN"]

            json_data = json.loads(resp.text)
            ig_account_id = json_data["accounts"][0]["accountId"]
        else:
            #print("Login failed - Restting password to Unknown, response code " + str(resp.status_code))
            #print(body)
            #print(headers)
            #print(resp.url)
            print(resp.content)
            ig_password = "UNKNOWN"

        #print(ig_cst)
        #print(ig_securitytoken)

        return 0

    @staticmethod
    def get_positions(member = None):
        ret_val = []
        req_headers = {
            "X-IG-API-KEY": ig_apikey,
            "X-SECURITY-TOKEN": ig_securitytoken,
            "CST": ig_cst,
            "Version": 2
        }

        resp = requests.get(ig_url + 'positions', headers=req_headers)
        if (resp.status_code == 200):
            json_data = json.loads(resp.text)
            #print(json.dumps(json_data,indent=4))
            for position in json_data["positions"]:
                ig_pos = ig_position(position,member)
                ret_val.append(ig_pos)
            #print (ret_val)

        return ret_val


    @staticmethod
    def get_transactions():
        ret_val = []
        req_headers = {
            "X-IG-API-KEY": ig_apikey,
            "X-SECURITY-TOKEN": ig_securitytoken,
            "CST": ig_cst,
            "Version": 2
        }

        resp = requests.get(ig_url + 'history/transactions', headers=req_headers)
        json_data = json.loads(resp.text)
        #print(json.dumps(json_data, indent=4))
        for trans in json_data["transactions"]:
            transaction = ig_transaction(trans)
            ret_val.append(transaction)
        #print(ret_val)

        return ret_val


class ig_position:
    ig_pos_size = None
    ig_pos_limit = None
    ig_pos_stop = None
    ig_pos_direction = None
    ig_pos_start_level = None
    ig_pos_instrument = None
    ig_pos_bid = None
    ig_pos_offer = None

    @property
    def ig_pos_price(self):
        if self.ig_pos_direction == "BUY":
            return self.ig_pos_bid
        else:
            return self.ig_pos_offer


    @property
    def ig_pos_profit(self):
        if self.ig_pos_direction == "BUY":
            return round(self.ig_pos_size * (self.ig_pos_price - self.ig_pos_start_level),2)
        else:
            return round(self.ig_pos_size * (self.ig_pos_start_level - self.ig_pos_price),2)

    def __init__(self,json_position, member = None):
        percentage_to_apply = 1
        if (member != None):
            percentage_to_apply = member.percentage_of_trades
        #print(json_position['position']['size'])
        self.ig_pos_size = json_position['position']['size'] * percentage_to_apply
        self.ig_pos_limit = json_position['position']['limitLevel']
        self.ig_pos_stop = json_position['position']['stopLevel']
        self.ig_pos_direction = json_position['position']['direction']
        self.ig_pos_start_level = json_position['position']['level']
        self.ig_pos_instrument = json_position['market']['instrumentName']
        self.ig_pos_bid = json_position['market']['bid']
        self.ig_pos_offer = json_position['market']['offer']


class ig_transaction:
    ig_trans_size = None
    ig_trans_limit = None
    ig_trans_stop = None
    ig_trans_direction = None
    ig_trans_start_level = None
    ig_trans_instrument = None
    ig_trans_bid = None
    ig_trans_offer = None

    @property
    def ig_trans_price(self):
        if self.ig_trans_direction == "BUY":
            return self.ig_trans_bid
        else:
            return self.ig_trans_offer


    @property
    def ig_trans_profit(self):
        if self.ig_trans_direction == "BUY":
            return round(self.ig_trans_size * (self.ig_trans_price - self.ig_trans_start_level),2)
        else:
            return round(self.ig_trans_size * (self.ig_trans_start_level - self.ig_trans_price),2)

    def __init__(self,json_position):
        #print(json_position['position']['size'])
        self.ig_trans_size = json_position['position']['size']
        self.ig_trans_limit = json_position['position']['limitLevel']
        self.ig_trans_stop = json_position['position']['stopLevel']
        self.ig_trans_direction = json_position['position']['direction']
        self.ig_trans_start_level = json_position['position']['level']
        self.ig_trans_instrument = json_position['market']['instrumentName']
        self.ig_trans_bid = json_position['market']['bid']
        self.ig_trans_offer = json_position['market']['offer']


if (ig_rest.need_password() == False):
    ig_rest.login()

