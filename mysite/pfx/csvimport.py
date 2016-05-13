from socket import gethostname
import os,django,csv,codecs,sys,datetime

my_hostname = gethostname()
if (my_hostname == 'pm-django.zoo.lan'):
    DEBUG = False
    ALLOWED_HOSTS = ['poultryfx.com']
    csv_filepathname = '/home/softwire/PoultryFX/mysite/imports/trades.csv'
    path = '/home/softwire/PoultryFX/mysite'  # use your own username here
elif (my_hostname == 'PHILLAPTOP'):
    DEBUG = True
    ALLOWED_HOSTS = []
    csv_filepathname='E:\\Work\\\PoultryFX\\\mysite\\\imports\\trades.csv'
    path = 'E:\\Work\\PoultryFX\\mysite'  # use your own username here
else:
    DEBUG = True
    ALLOWED_HOSTS = []
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
    #models.IndividualPL.objects.all().delete()
    #models.IndividualCash.objects.all().delete()
    #models.Member.objects.all().delete()

    #u1 = User.objects.create_user('john.cooper@ensoft.com','john.cooper@ensoft.co.uk','jellyfish')
    #u2 = User.objects.create_user('dan.shavick@softwire.com','dan.shavick@softwire.com','jellyfish')
    #u3 = User.objects.create_user('nigel.ratcliffe@ensoft.co.uk','nigel.ratcliffe@ensoft.co.uk','jellyfish')
    #u4 = User.objects.create_user('seancurran78@googlemail.com','seancurran78@googlemail.com','jellyfish')
    #u5 = User.objects.create_user('crowecameron@hotmail.com','crowecameron@hotmail.com','jellyfish')
    #u3.save()
    #u4.save()
    #u5.save
    #u1 = User.objects.get(email='phil.marsden@softwire.com')
    #u2 = User.objects.get(email = 'john.cooper@ensoft.co.uk')
    #u3 = User.objects.get(email = 'dan.shavick@softwire.com')
    #u4 = User.objects.get(email = 'nigel.ratcliffe@ensoft.co.uk')
    #u5 = User.objects.get(email='seancurran78@googlemail.com')
    #u6 = User.objects.get(email='crowecameron@hotmail.com')

    #m1 = Member(user = u1,current_trade_size = 10,current_commission = -0.05, current_fun_fund = 0.01)
    #m1.save()
    #m2 = Member(user = u2,current_trade_size = 20,current_commission = 0.05, current_fun_fund = 0.01)
    #m2.save()
    #m3 = Member(user = u3,current_trade_size = 10,current_commission = 0.05, current_fun_fund = 0.01)
    #m3.save()
    #m4 = Member(user = u4,current_trade_size = 20,current_commission = 0.05, current_fun_fund = 0.01)
    #m4.save()
    #m5 = Member(user = u5,current_trade_size = 10,current_commission = 0.05, current_fun_fund = 0.01)
    #m5.save()
    #m6 = Member(user = u6,current_trade_size = 10,current_commission = 0.05, current_fun_fund = 0.01)
    #m6.save()



    #m1 = Member.objects.get(user = u1)
    #m2 = Member.objects.get(user = u2)
    #m3 = Member.objects.get(user = u3)
    #m4 = Member.objects.get(user = u4)
    #m5 = Member.objects.get(user = u5)
    #m6 = Member.objects.get(user = u6)

    #ic1 = IndividualCash(member = m1, size = 3340, transaction_date = datetime.datetime.now())
    #ic1.save()
    #ic2 = IndividualCash(member = m2, size = 6000, transaction_date = datetime.datetime.now())
    #ic2.save()
    #ic3 = IndividualCash(member = m3, size = 3000, transaction_date = datetime.datetime.now())
    #ic3.save()
    #ic4 = IndividualCash(member = m4, size = 6000, transaction_date = datetime.datetime.now())
    #ic4.save()
    #ic5 = IndividualCash(member = m5, size = 3000, transaction_date = datetime.datetime.now())
    #ic5.save()
    #ic6 = IndividualCash(member = m6, size = 3000, transaction_date = datetime.datetime.now())
    #ic6.save()

    #igpl1 = IGPL.objects.get(closing_ref = 'FBFWWPA2')
    #ipl1 = IndividualPL(member=m1, igpl=igpl1, size=5, commission=0.05, fun_fund=0.01)
    #ipl1.save()
    #ipl2 = IndividualPL(member=m2, igpl=igpl1, size=10, commission=0.05, fun_fund=0.01)
    #ipl2.save()
    #ipl3 = IndividualPL(member=m3, igpl=igpl1, size=5, commission=0.05, fun_fund=0.01)
    #ipl3.save()
    #ipl4 = IndividualPL(member=m4, igpl=igpl1, size=10, commission=0.05, fun_fund=0.01)
    #ipl4.save()
    #ipl5 = IndividualPL(member=m5, igpl=igpl1, size=5, commission=0.05, fun_fund=0.01)
    #ipl5.save()
    #ipl6 = IndividualPL(member=m6, igpl=igpl1, size=5, commission=0.05, fun_fund=0.01)
    #ipl6.save()


def mycsv_reader(csv_reader):
  while True:
    try:
      yield next(csv_reader)
    except csv.Error:
      pass
    continue

def import_csv():
    #dataReader = csv.reader(open(csv_filepathname, 'rU'), dialect='excel-tab')
    #start_import = False

    #u1 = User.objects.get(email='phil.marsden@softwire.com')
    #u2 = User.objects.get(email='john.cooper@ensoft.co.uk')
    #u3 = User.objects.get(email='dan.shavick@softwire.com')
    #u4 = User.objects.get(email='nigel.ratcliffe@ensoft.co.uk')
    #u5 = User.objects.get(email='seancurran78@googlemail.com')
    #u6 = User.objects.get(email='crowecameron@hotmail.com')

    #m1 = Member.objects.get(user = u1)
    #m2 = Member.objects.get(user = u2)
    #m3 = Member.objects.get(user = u3)
    #m4 = Member.objects.get(user = u4)
    #m5 = Member.objects.get(user = u5)
    #m6 = Member.objects.get(user = u6)

    reader = mycsv_reader(csv.reader(open(csv_filepathname, encoding='utf-16', mode='rU'), dialect='excel-tab'))
    start_import = False

    models.IGPL.objects.all().delete()

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
            igpl.gross_profit = float(row[19])
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
            igpl.net_profit = float(row[11])
            igpl.save()
            print("Imported",row[0])

        try:
            if row[0] == 'Closing Ref':
                start_import = True
        except:
            start_import = False

bootstrap_data()
import_csv()
