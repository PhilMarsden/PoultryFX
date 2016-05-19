from socket import gethostname
import os,django,csv,codecs,sys,datetime

my_hostname = gethostname()
if (my_hostname == 'pm-django.zoo.lan'):
    DEBUG = False
    ALLOWED_HOSTS = ['poultryfx.com']
    csv_filepathname = '/home/softwire/PoultryFX/mysite/imports/trades'
    path = '/home/softwire/PoultryFX/mysite'  # use your own username here
elif (my_hostname == 'PHILLAPTOP'):
    DEBUG = True
    ALLOWED_HOSTS = []
    csv_filepathname='E:\\Work\\\PoultryFX\\\mysite\\\imports\\trades'
    path = 'E:\\Work\\PoultryFX\\mysite'  # use your own username here
else:
    DEBUG = True
    ALLOWED_HOSTS = []
    csv_filepathname='C:\\Work\\\PoultryFX\\\mysite\\\imports\\trades'
    path = 'C:\\Work\\PoultryFX\\mysite'  # use your own username here

if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.contrib.auth.models import User
from pfx import models
from pfx.models import Member, IGPL, IndividualPL, IndividualCash


def bootstrap_data():
    from pfx.models import Member,IGPL,IndividualPL,IndividualCash
    models.IGPL.objects.all().delete()
    models.IndividualPL.objects.all().delete()
    models.IndividualCash.objects.all().delete()
    models.Member.objects.all().delete()

    #u1 = User.objects.create_user('john.cooper@ensoft.com','john.cooper@ensoft.co.uk','jellyfish')
    #u2 = User.objects.create_user('dan.shavick@softwire.com','dan.shavick@softwire.com','jellyfish')
    #u3 = User.objects.create_user('nigel.ratcliffe@ensoft.co.uk','nigel.ratcliffe@ensoft.co.uk','jellyfish')
    #u4 = User.objects.create_user('seancurran78@googlemail.com','seancurran78@googlemail.com','jellyfish')
    #u5 = User.objects.create_user('crowecameron@hotmail.com','crowecameron@hotmail.com','jellyfish')
    #u1.save()
    #u2.save()
    #u3.save()
    #u4.save()
    #u5.save()
    u1 = User.objects.get(email='phil.marsden@softwire.com')
    u2 = User.objects.get(email = 'john.cooper@ensoft.co.uk')
    u3 = User.objects.get(email = 'dan.shavick@softwire.com')
    u4 = User.objects.get(email = 'nigel.ratcliffe@ensoft.co.uk')
    u5 = User.objects.get(email='seancurran78@googlemail.com')
    u6 = User.objects.get(email='crowecameron@hotmail.com')

    m1 = Member(user = u1,manual_trade_size = 10,current_commission = 0.05, current_fun_fund = 0.01)
    m1.save()
    m2 = Member(user = u2,manual_trade_size = 20,current_commission = 0.05, current_fun_fund = 0.01)
    m2.save()
    m3 = Member(user = u3,manual_trade_size = 10,current_commission = 0.05, current_fun_fund = 0.01)
    m3.save()
    m4 = Member(user = u4,manual_trade_size = 20,current_commission = 0.05, current_fun_fund = 0.01)
    m4.save()
    m5 = Member(user = u5,manual_trade_size = 10,current_commission = 0.05, current_fun_fund = 0.01)
    m5.save()
    m6 = Member(user = u6,manual_trade_size = 10,current_commission = 0.05, current_fun_fund = 0.01)
    m6.save()

    Member.set_all_trade_sizes()

    #m1 = Member.objects.get(user = u1)
    #m2 = Member.objects.get(user = u2)
    #m3 = Member.objects.get(user = u3)
    #m4 = Member.objects.get(user = u4)
    #m5 = Member.objects.get(user = u5)
    #m6 = Member.objects.get(user = u6)

    date1 = datetime.datetime(2016,5,3)
    ic1 = IndividualCash(member = m1, size = 3340, transaction_date = date1)
    ic1.save()
    ic2 = IndividualCash(member = m2, size = 6000, transaction_date = date1)
    ic2.save()
    ic3 = IndividualCash(member = m3, size=3000, transaction_date=date1)
    ic3.save()
    ic3 = IndividualCash(member = m3, size = 2500, transaction_date = datetime.datetime(2016,5,19))
    ic3.save()
    ic4 = IndividualCash(member = m4, size = 6000, transaction_date = date1)
    ic4.save()
    ic5 = IndividualCash(member = m5, size = 3000, transaction_date = date1)
    ic5.save()
    ic6 = IndividualCash(member = m6, size = 3000, transaction_date = date1)
    ic6.save()




def mycsv_reader(csv_reader):
  while True:
    try:
      yield next(csv_reader)
    except csv.Error:
      pass
    continue

def import_csv(csv_filename):
    reader = mycsv_reader(csv.reader(open(csv_filename, encoding='utf-16', mode='rU'), dialect='excel-tab'))
    start_import = False

    for row in reader:
        if start_import:
            print(row)
            igpl = models.IGPL()
            igpl.closing_ref = row[0]
            igpl.closed_date = datetime.datetime.strptime(row[1], "%d/%m/%y").strftime("%Y-%m-%d")
            igpl.opening_ref = row[2]
            igpl.opening_date = datetime.datetime.strptime(row[3], "%d/%m/%y").strftime("%Y-%m-%d")
            igpl.market = row[4]
            igpl.period = row[5]
            igpl.direction = row[6]
            igpl.size = float(row[7])
            igpl.opening_price = float(row[8])
            igpl.closing_price = float(row[9])
            igpl.trade_ccy = row[10]
            igpl.gross_profit = float(row[11])
            igpl.funding = float(row[12])
            igpl.borrowing = float(row[13])
            igpl.dividends = float(row[14])
            igpl.lrprem = float(row[15])
            igpl.others = float(row[16])
            if (row[17] == "-" ):
                igpl.commccy = float(0)
            else:
                igpl.commccy = float(row[17])
            igpl.comm = float(row[18])
            igpl.net_profit = float(row[19])
            igpl.save()
            print("Imported",row[0])

        try:
            if row[0] == 'Closing Ref':
                start_import = True
        except:
            start_import = False

bootstrap_data()
import_csv(csv_filepathname + '1.csv')

# Dan Add more money and make trade size 20
u1 = User.objects.get(email='dan.shavick@softwire.com')
m1 = Member.objects.get(user=u1)
m1.manual_trade_size = 20
m1.save()
m1.set_calculated_trade_size()

# Phil automatic trade size
m1 = Member.objects.get(user=User.objects.get(email='phil.marsden@softwire.com'))
m1.automatic_trade_size = True
m1.save()
m1.set_calculated_trade_size()

member_list = Member.objects.all()
for m1 in member_list:
    m1.automatic_trade_size = True
    m1.save()
    m1.set_calculated_trade_size()

#import_csv(csv_filepathname + '2.csv')
