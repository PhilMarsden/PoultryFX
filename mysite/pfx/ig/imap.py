EMAIL_ACCOUNT = "phil@marsdy.com"
EMAIL_FOLDER = "INBOX"
EMAIL_RECIPIENT = "phil.marsden@softwire.com"
IMAP_SERVER="imap.europe.secureserver.net"

from pfx.ig.imap_private import *


from pfx.models import IGPL
from pfx.models import TradeEmail

import sys
import imaplib
import getpass
import email
import email.header
import datetime
import re

from django.core.mail import EmailMessage

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
logger.info('IMAP Initialised')

from threading import Thread, Event

class pfx_imap(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        logger.info('IMAP Thread started')
        self.scan_emails()
        while not self.stopped.wait(60.0):
            self.scan_emails()

    def scan_emails(self):
        logger.info('Scanning Emails - Start Server:%s, Account:%s',IMAP_SERVER,EMAIL_ACCOUNT)
        try:
            logger.info('IMAP : Connect to Server')
            M = imaplib.IMAP4_SSL(IMAP_SERVER)
            logger.info('IMAP : Login')
            rv, data = M.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
            logger.info('IMAP : List')
            rv2, mailboxes = M.list()
            if rv2 == 'OK':
                logger.info('IMAP : Select EMAIL_FOLDER')
                rv3, data = M.select(EMAIL_FOLDER)
                if rv3 == 'OK':
                    logger.info('IMAP : Search Emails')
                    #typ, data = M.search(None, 'OR SUBJECT "New Live Trade" SUBJECT "New Trade" SUBJECT "Currency Club - New Live Trade Notification - for Member: MAR003" SUBJECT "Currency Club - New Live Trade Notification"')
                    typ, data = M.search(None, 'ALL')
                    for num in data[0].split():
                        logger.debug('Found an email')
                        typ, data2 = M.fetch(num, '(BODY[HEADER.FIELDS (MESSAGE-ID SUBJECT)])')
                        msg_str = email.message_from_string(data2[0][1].decode('utf-8'))
                        imap_message_id = msg_str.get('Message-ID').strip()
                        msg_subject = msg_str.get('SUBJECT').strip()
                        logger.info('IMAP Message ID : %s Subject : %s' % (imap_message_id,msg_subject))
                        existing_trade_email = TradeEmail.objects.filter(message_id=imap_message_id)
                        if existing_trade_email.count() > 0:
                            logger.debug(
                                'Trade email already exists for IMAP Message ID : %s' % existing_trade_email[0].message_id)
                        else:
                            logger.info('Check trades for IMAP Message ID : %s' % imap_message_id)
                            typ, data = M.fetch(num, '(RFC822)')
                            raw_email = data[0][1].decode('utf-8')
                            msg = email.message_from_string(raw_email).get_payload(decode=False)
                            store_trade = 0
                            section_type = 0
                            # Multi-part messages are a list which we dont handle so check this is a string
                            if isinstance(msg,str):
                                for line in msg.split("\n"):
                                    if "<< WINNING TRADE >>" in line:
                                        logger.debug('Found a winning trade')
                                    if "<< LIVE TRADE >>" in line:
                                        section_type = 1
                                        logger.debug('Found a live trade')
                                    if "Trade Date - " in line:
                                        trade_date = re.sub('Trade Date - ', '', (line.strip()))
                                        logger.debug('Trade Date : %s' % trade_date)
                                    if "Time Live - " in line:
                                        time_live = re.sub('Time Live - ', '', (line.strip()))
                                        logger.debug('Time Live : %s' % time_live)
                                    if "Currency Pair - " in line:
                                        currency_pair = re.sub('Currency Pair - ', '', (line.strip()))
                                        logger.debug('Currency Pair : %s' % currency_pair)
                                    if "Trade Start Price - " in line:
                                        trade_start = re.sub('Trade Start Price - ', '', (line.strip()))
                                        logger.debug('Trade Start : %s' % trade_start)
                                    if "Trade Stop Price - " in line:
                                        trade_stop = re.sub('Trade Stop Price - ', '', (line.strip()))
                                        logger.debug('Trade Stop : %s' % trade_stop)
                                    if "Trade Target Price - " in line:
                                        trade_target = re.sub('Trade Target Price - ', '', (line.strip()))
                                        logger.debug('Trade Target : %s' % trade_target)
                                        store_trade = 1
                                    if "Trade Target Price- " in line:
                                        trade_target = re.sub('Trade Target Price- ', '', (line.strip()))
                                        logger.debug('Trade Target : %s' % trade_target)
                                        if (section_type == 1):
                                            logger.debug('Store trade')
                                            store_trade = 1
                                        else:
                                            logger.debug('Ignore trade')

                                    if store_trade == 1:
                                        store_trade = 0
                                        if (trade_target > trade_start):
                                            trade_direction = "BUY"
                                        else:
                                            trade_direction = "SELL"
                                        emailToSendBody = '{} Direction:{} Start:{} Stop:{} Target:{} {}'.format(currency_pair, trade_direction, trade_start, trade_stop,trade_target, time_live)
                                        emailToSend = EmailMessage('Trade ', emailToSendBody, to=[EMAIL_RECIPIENT])
                                        logger.info('Sending email about trade with IMAP Message ID : %s' % imap_message_id)
                                        emailToSend.send()
                                        trade_email = TradeEmail()
                                        trade_email.message_id = imap_message_id
                                        trade_email.market = currency_pair
                                        trade_email.trade_date = trade_date
                                        trade_email.time_live = time_live
                                        trade_email.start_price = float(trade_start)
                                        trade_email.stop_price = float(trade_stop)
                                        trade_email.target_price = float(trade_target)
                                        logger.info('Saving trade to database with IMAP Message ID : %s' % imap_message_id)
                                        trade_email.save()

                                        trade_date = ''
                                        time_live = ''
                                        currency_pair = ''
                                        trade_start = ''
                                        trade_stop = ''
                                        trade_target = ''
                                        section_type = 0
                            else:
                                logger.info('Multi part message - ignore')

                    M.close()
                else:
                    logger.debug("ERROR: IMAP Error 1", rv3)

            else:
                logger.debug("ERROR: IMAP Error 2", rv2)

            M.logout()
        except Exception as inst:
            logger.error('IMAP Exception : ' % inst)

        logger.info('Scanning Emails - Stop')

