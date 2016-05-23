from pfx.models import IGPL
from pfx.models import TradeEmail

import sys
import imaplib
import getpass
import email
import email.header
import datetime
import re

EMAIL_ACCOUNT = "phil.marsden@softwire.com"
EMAIL_PASSWORD = "twyms69ER"
EMAIL_FOLDER = "INBOX"

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
logger.info('IMAP Initialised')

class pfx_imap:
    @staticmethod
    def scan_emails():
        M = imaplib.IMAP4_SSL('imap.softwire.com')

        try:
            rv, data = M.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        except imaplib.IMAP4.error:
            print ("LOGIN FAILED!!! ")
            sys.exit(1)

        print (rv, data)

        rv, mailboxes = M.list()
        if rv == 'OK':
            rv, data = M.select(EMAIL_FOLDER)
            if rv == 'OK':
                print ("Processing mailbox...\n")
                typ, data = M.search(None, '(SUBJECT "New CurrencyClub Trade")')
                for num in data[0].split():
                    typ, data2 = M.fetch(num, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')
                    msg_str = email.message_from_string(data2[0][1].decode('utf-8'))
                    imap_message_id = msg_str.get('Message-ID').strip()
                    try:
                        existing_trade_email = TradeEmail.objects.get(message_id = imap_message_id)
                        logger.debug('Trade email already exists for IMAP Message ID : %s' % existing_trade_email.message_id)
                    except:
                        logger.debug('IMAP Message ID : %s' % imap_message_id)
                        typ, data = M.fetch(num, '(RFC822)')
                        raw_email = data[0][1].decode('utf-8')
                        msg = email.message_from_string(raw_email).get_payload(decode=False)
                        for line in msg.split("\n"):
                            if "Trade Date - " in line:
                                trade_date = re.sub('Trade Date - ','',(line.strip()))
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
                        trade_email.save()
                M.close()
            else:
                logger.debug("ERROR: Unable to open mailbox ", rv)

        M.logout()

#pfx_imap.scan_emails()

