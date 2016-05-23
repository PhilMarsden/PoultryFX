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
        logger.info('Scanning Emails - Start')
        try:
            M = imaplib.IMAP4_SSL('imap.softwire.com')
            rv, data = M.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
            rv2, mailboxes = M.list()
            if rv2 == 'OK':
                rv3, data = M.select(EMAIL_FOLDER)
                if rv3 == 'OK':
                    typ, data = M.search(None, '(SUBJECT "New CurrencyClub Trade")')
                    for num in data[0].split():
                        typ, data2 = M.fetch(num, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')
                        msg_str = email.message_from_string(data2[0][1].decode('utf-8'))
                        imap_message_id = msg_str.get('Message-ID').strip()
                        try:
                            existing_trade_email = TradeEmail.objects.get(message_id=imap_message_id)
                            logger.debug(
                                'Trade email already exists for IMAP Message ID : %s' % existing_trade_email.message_id)
                        except:
                            logger.info('IMAP Message ID : %s' % imap_message_id)
                            typ, data = M.fetch(num, '(RFC822)')
                            raw_email = data[0][1].decode('utf-8')
                            msg = email.message_from_string(raw_email).get_payload(decode=False)
                            for line in msg.split("\n"):
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
                                if "Trade Target Price- " in line:
                                    trade_target = re.sub('Trade Target Price- ', '', (line.strip()))
                                    logger.debug('Trade Target : %s' % trade_target)
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
                            emailToSendBody = '{} Start:{} Stop:{} Target:{} {}'.format(currency_pair, trade_start, trade_stop,trade_target, time_live)
                            emailToSend = EmailMessage('Trade', emailToSendBody, to=[EMAIL_RECIPIENT])
                            logger.info('Sending email about trade with IMAP Message ID : %s' % imap_message_id)
                            emailToSend.send()

                    M.close()
                else:
                    logger.debug("ERROR: IMAP Error", rv3)

            else:
                logger.debug("ERROR: IMAP Error", rv2)

            M.logout()
        except imaplib.IMAP4.error:
            logger.error("IMAP Error")

        logger.info('Scanning Emails - Stop')

