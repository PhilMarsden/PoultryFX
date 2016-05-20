import requests
import json
from pfx.ig.rest_private import *
from datetime import datetime,timedelta
from pfx.models import IGPL
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
logger.info('IG REST Initialised')

ig_securitytoken = ""
ig_cst = None
ig_account_id = ""
ig_json_positions = []
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
        if (ig_password == None):
            return True
        else:
            return False

    @staticmethod
    def need_login():
        if (ig_cst == None):
            return True
        else:
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
        global ig_password,logger
        if (ig_password != None) and (ig_cst == None):
            logger.info("Attempting Login")
            body = {
                "identifier": ig_identifier,
                "password": ig_password
            }
            headers = {
                "X-IG-API-KEY": ig_apikey
            }

            resp = requests.post(ig_url + 'session', json=body, headers=headers)

            if (resp.status_code == 200):
                logger.info("Login succeeded")
                global ig_cst,ig_securitytoken,ig_account_id
                ig_cst = resp.headers["CST"]
                ig_securitytoken = resp.headers["X-SECURITY-TOKEN"]

                json_data = json.loads(resp.text)
                ig_account_id = json_data["accounts"][0]["accountId"]
            else:
                logger.warning("Login failed - Restting password to NONE, response code " + str(resp.status_code))
                logger.debug(body)
                logger.debug(headers)
                logger.debug(resp.url)
                logger.warning(resp.content)
                ig_password = None
                ig_cst = None

    @staticmethod
    def get_positions(member = None):
        global logger, ig_positions_datetime,ig_json_positions,ig_cst
        logger.info('Get positions')

        refresh_positions = False
        if (ig_positions_datetime == None):
            logger.info('First time getting positions')
            refresh_positions = True
        else:
            if (datetime.now() > (ig_positions_datetime + timedelta(seconds = 10))):
                logger.info('Positions out of date, refresh')
                refresh_positions = True

        if (refresh_positions and ig_cst != None):
            req_headers = {
                "X-IG-API-KEY": ig_apikey,
                "X-SECURITY-TOKEN": ig_securitytoken,
                "CST": ig_cst,
                "Version": 2
            }
            resp = requests.get(ig_url + 'positions', headers=req_headers)
            if (resp.status_code == 401):
                logger.warning("401 return code, try logging in again")
                ig_cst = None
                ig_rest.login()
            elif (resp.status_code == 200):
                logger.info("200 return code, all good")
                json_data = json.loads(resp.text)
                #logger.debug('Positions {}'.format(json.dumps(json_data, indent=4)))
                ig_json_positions = json_data["positions"]
                ig_positions_datetime = datetime.now()
            else:
                logger.error('** Failed to get positions : {}'.format(str(resp.status_code)))
        else:
            logger.info('Take positions from cache')

        positions = []
        for jposition in ig_json_positions:
            pos = ig_position(jposition, member)
            positions.append(pos)
        return positions

    @staticmethod
    def get_activity(include_all):
        global logger, ig_activities,ig_activities_datetime,ig_cst
        logger.info('Get activity')

        refresh_positions = False
        if (ig_activities_datetime == None):
            logger.info('First time getting activity')
            refresh_positions = True
        else:
            if (datetime.now() > (ig_activities_datetime + timedelta(seconds = 10))):
                logger.info('Activity out of date, refresh')
                refresh_positions = True
        if (refresh_positions and ig_cst != None):
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
            if (resp.status_code == 401):
                logger.warning("401 return code, try logging in again")
                ig_cst = None
                ig_rest.login()
            elif (resp.status_code == 200):
                logger.info("200 return code, all good")
                json_data = json.loads(resp.text)
                #logger.debug('Activity {}'.format(json.dumps(json_data, indent=4)))
                for act_i in json_data["activities"]:
                    if (act_i["activity"] == "Order") or include_all:
                        activity = ig_activity(act_i)
                        ig_activities.append(activity)
            else:
                logger.error('** Failed to get activities : {}'.format(str(resp.status_code)))
            ig_activities_datetime = datetime.now()
        else:
            logger.info('Take activity from cache')

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
            return self.ig_pos_size * (self.ig_pos_price - self.ig_pos_start_level)
        else:
            return self.ig_pos_size * (self.ig_pos_start_level - self.ig_pos_price)

    @property
    def ig_pos_max_win(self):
        if self.ig_pos_direction == "BUY":
            return self.ig_pos_size * (self.ig_pos_limit - self.ig_pos_start_level)
        else:
            return self.ig_pos_size * (self.ig_pos_start_level - self.ig_pos_limit)

    @property
    def ig_pos_max_loss(self):

        if self.ig_pos_direction == "BUY":
            return self.ig_pos_size * (self.ig_pos_stop - self.ig_pos_start_level)
        else:
            return self.ig_pos_size * (self.ig_pos_start_level - self.ig_pos_stop)

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
        self.ig_act_level = float(json_position['level'])
        self.ig_act_size = float(json_position['size'])
        self.ig_act_dealid = json_position['dealId']
        self.ig_act_datetime = json_position['date'] + json_position['time']
        if self.ig_act_marketName in ig_instrument_urls:
            self.ig_act_url = ig_instrument_urls[self.ig_act_marketName]
        else:
            self.ig_act_url = ""
        logger.debug('URL for {} = {}'.format(self.ig_act_marketName, self.ig_act_url))

    @staticmethod
    def get_act(dealid):
        for act in ig_activities:
            if (act.ig_act_dealid == dealid):
                return act
        return None

    @property
    def open_activity(self):
        for act in ig_activities:
            if (act.ig_act_dealid[-8:] == self.matched_open_position):
                logger.debug('Found matching open activity {}'.format(act.ig_act_dealid))
                return act
        return None

    def add_trade(self):
        logger.debug('Adding trade for deal id {}'.format(self.ig_act_dealid))
        matching_act = self.open_activity
        igpl = IGPL()
        igpl.closing_ref = self.ig_act_dealid[-8:]
        igpl.closed_date = datetime.strptime(self.ig_act_datetime, "%d/%m/%y%H:%M").strftime("%Y-%m-%d")
        igpl.opening_ref = matching_act.ig_act_dealid[-8:]
        igpl.opening_date = datetime.strptime(matching_act.ig_act_datetime, "%d/%m/%y%H:%M").strftime("%Y-%m-%d")
        igpl.market = self.ig_act_marketName
        igpl.period = "DFB"
        if (self.ig_act_size < 0):
            igpl.direction = "BUY"
        else:
            igpl.direction = "SELL"
        igpl.size = abs(self.ig_act_size)
        igpl.opening_price = matching_act.ig_act_level
        igpl.closing_price = self.ig_act_level
        igpl.trade_ccy = "GBP"
        if (igpl.direction == "BUY"):
            igpl.gross_profit = igpl.size * (igpl.closing_price - igpl.opening_price)
        else:
            igpl.gross_profit = igpl.size * (igpl.opening_price - igpl.closing_price)
        igpl.funding = 0
        igpl.borrowing = 0
        igpl.dividends = 0
        igpl.lrprem = 0
        igpl.others = 0
        igpl.commccy = 0
        igpl.comm = 0
        igpl.net_profit = igpl.gross_profit
        igpl.save()

    @property
    def add_trade_url(self):
        ret_url = "?dealid=" + self.ig_act_dealid
        logger.debug('URL for adding trade = {}'.format(ret_url))
        return ret_url

    #
    @property
    def matched_open_position(self):
        if self.ig_act_result.startswith('Position/s closed:'):
            # Its a closing trade so see if we have a trade for it
            return self.ig_act_result.lstrip('Position/s closed: ')
        else:
            return None

    @property
    def trade_needed(self):
        if self.ig_act_result.startswith('Position/s closed:'):
            # Its a closing trade so see if we have a trade for it
            act_open_ref = self.matched_open_position
            logger.info('Checking for trade with ref:{}:'.format(act_open_ref))
            try:
                igpls = IGPL.objects.get(opening_ref = act_open_ref)
                return False
            except:
                logger.info('Trade ref doesnt exist')
                return True
        else:
            return False

if (ig_rest.need_password() == False):
    ig_rest.login()

#ig_rest.get_activity()