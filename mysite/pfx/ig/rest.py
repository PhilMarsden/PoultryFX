import requests
import json
from pfx.ig.rest_private import *
from datetime import datetime,timedelta
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
logger.info('IG REST Initialised')

ig_securitytoken = ""
ig_cst = ""
ig_account_id = ""
ig_json_positions = None
ig_positions_datetime = None
ig_activities = []
ig_activities_datetime = None
ig_instrument_urls = {
    'NZD/USD': 'http://www.ig.com/uk/ig-forex/nzd-usd',
    'GBP/USD': 'http://www.ig.com/uk/ig-forex/gbp-usd',
    'EUR/GBP': 'http://www.ig.com/uk/ig-forex/eur-gbp',
    'EUR/USD': 'http://www.ig.com/uk/ig-forex/eur-usd',
    'Tesla Motors Inc (All Sessions)': 'http://www.ig.com/uk/ig-shares/tesla-motors-TSLA-US',
}

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
        global logger, ig_positions_datetime,ig_json_positions
        logger.info('Get positions')

        refresh_positions = False
        if (ig_positions_datetime == None):
            logger.debug('First time getting positions')
            refresh_positions = True
        else:
            if (datetime.now() > (ig_positions_datetime + timedelta(seconds = 10))):
                logger.debug('Positions out of date, refresh')
                refresh_positions = True

        if (refresh_positions):
            req_headers = {
                "X-IG-API-KEY": ig_apikey,
                "X-SECURITY-TOKEN": ig_securitytoken,
                "CST": ig_cst,
                "Version": 2
            }
            resp = requests.get(ig_url + 'positions', headers=req_headers)
            if (resp.status_code == 200):
                json_data = json.loads(resp.text)
                #logger.debug('Positions {}'.format(json.dumps(json_data, indent=4)))
                ig_json_positions = json_data["positions"]
            # print (ret_val)
            else:
                logger.error('** Failed to get positions : {}'.format(str(resp.status_code)))
            ig_positions_datetime = datetime.now()
        else:
            logger.debug('Take positions from cache')

        positions = []
        for jposition in ig_json_positions:
            pos = ig_position(jposition, member)
            positions.append(pos)
        return positions

    @staticmethod
    def get_activity():
        global logger, ig_activities,ig_activities_datetime
        logger.info('Get activity')

        refresh_positions = False
        if (ig_activities_datetime == None):
            logger.debug('First time getting activity')
            refresh_positions = True
        else:
            if (datetime.now() > (ig_activities_datetime + timedelta(seconds = 10))):
                logger.debug('Activity out of date, refresh')
                refresh_positions = True
        if (refresh_positions):
            ig_activities = []
            req_headers = {
                "X-IG-API-KEY": ig_apikey,
                "X-SECURITY-TOKEN": ig_securitytoken,
                "CST": ig_cst,
                "Version": 1
            }

            num_hours = 24 * 90
            time_period = 1000 * 60 * 60 * num_hours

            logger.debug('time in milliseconds = {}'.format(time_period))

            resp = requests.get(ig_url + 'history/activity/' + str(time_period), headers=req_headers)
            if (resp.status_code == 200):
                json_data = json.loads(resp.text)
                #logger.debug('Activity {}'.format(json.dumps(json_data, indent=4)))
                for act_i in json_data["activities"]:
                    activity = ig_activity(act_i)
                    ig_activities.append(activity)
            else:
                logger.error('** Failed to get activities : {}'.format(str(resp.status_code)))
            ig_activities_datetime = datetime.now()
        else:
            logger.debug('Take activity from cache')

        return ig_activities


class ig_position:
    ig_pos_size = None
    ig_pos_limit = None
    ig_pos_stop = None
    ig_pos_direction = None
    ig_pos_start_level = None
    ig_pos_instrument = None
    ig_pos_bid = None
    ig_pos_offer = None
    ig_pos_dealid = None
    ig_pos_url = None

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
        global ig_instrument_urls
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
        self.ig_pos_dealid = json_position['position']['dealId']
        if self.ig_pos_instrument in ig_instrument_urls:
            self.ig_pos_url = ig_instrument_urls[self.ig_pos_instrument]
        else:
            self.ig_pos_url = ""
        logger.debug('URL for {} = {}'.format(self.ig_pos_instrument, self.ig_pos_url))


class ig_activity:
    ig_act_activity = None
    ig_act_result = None
    ig_act_limit = None
    ig_act_marketName = None
    ig_act_stop = None
    ig_act_level = None
    ig_act_size = None
    ig_act_dealid = None
    ig_act_datetime = None
    ig_act_url = None

    def __init__(self,json_position):
        global ig_instrument_urls
        self.ig_act_activity = json_position['activity']
        self.ig_act_result = json_position['result']
        self.ig_act_limit = json_position['limit']
        self.ig_act_marketName = json_position['marketName']
        self.ig_act_stop = json_position['stop']
        self.ig_act_level = json_position['level']
        self.ig_act_size = json_position['size']
        self.ig_act_dealid = json_position['dealId']
        self.ig_act_datetime = json_position['date'] + json_position['time']
        if self.ig_act_marketName in ig_instrument_urls:
            self.ig_act_url = ig_instrument_urls[self.ig_act_marketName]
        else:
            self.ig_act_url = ""
        logger.debug('URL for {} = {}'.format(self.ig_act_marketName, self.ig_act_url))


if (ig_rest.need_password() == False):
    ig_rest.login()

#ig_rest.get_activity()