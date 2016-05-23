from socket import gethostname
import os, django, csv, codecs, sys, datetime

my_hostname = gethostname()
if (my_hostname == 'pm-django.zoo.lan'):
    DEBUG = False
    ALLOWED_HOSTS = ['poultryfx.com']
    csv_filepathname = '/home/softwire/PoultryFX/mysite/imports/trades'
    path = '/home/softwire/PoultryFX/mysite'  # use your own username here
elif (my_hostname == 'PHILLAPTOP'):
    DEBUG = True
    ALLOWED_HOSTS = []
    csv_filepathname = 'E:\\Work\\\PoultryFX\\\mysite\\\imports\\trades'
    path = 'E:\\Work\\PoultryFX\\mysite'  # use your own username here
else:
    DEBUG = True
    ALLOWED_HOSTS = []
    csv_filepathname = 'C:\\Work\\\PoultryFX\\\mysite\\\imports\\trades'
    path = 'C:\\Work\\PoultryFX\\mysite'  # use your own username here

if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()
from pfx.ig.imap import pfx_imap

from threading import Event
stopFlag = Event()
thread = pfx_imap(stopFlag)
thread.start()
# this will stop the timer
#stopFlag.set()