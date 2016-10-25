from socket import gethostname
import os,django,csv,codecs,sys,datetime

import logging
logger = logging.getLogger("csvimport")
print("enable logging csvimport")
logger.info('CSVIMPORT Logger Initialised')


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
from pfx.models import Member, IGPL, IndividualPL, IndividualCash, total_calculated_trade_size,total_gross_profit

def trades_for_phil(file_suffix):
    u1 = User.objects.get(email='phil.marsden@softwire.com')
    m1 = Member.objects.get(user=u1)
    m1.current_commission = 0
    m1.current_fun_fund = 0
    m1.save
    igpls = import_csv(csv_filepathname + file_suffix)
    member_list = [m1]
    for igpl in igpls:
        for m1 in member_list:
            igpl.AddIndividualPL(m1, member_list)
    m1.current_commission = 0.05
    m1.current_fun_fund = 0.01
    m1.save


def trades_for_all(file_suffix):
    igpls = import_csv(csv_filepathname + file_suffix)
    member_list = Member.objects.all()
    for igpl in igpls:
        for m1 in member_list:
            igpl.AddIndividualPL(m1, member_list)

def asserts_for_all():
    member_list = Member.objects.all()
    f = open('tmp.txt', 'a')
    for m1 in member_list:
        f.write("assert (Member.objects.get(user=User.objects.get(email='{}')).balance == {})\n".format(m1,m1.balance))
    f.close()

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

    Member.set_all_trade_sizes(10,300)

    #m1 = Member.objects.get(user = u1)
    #m2 = Member.objects.get(user = u2)
    #m3 = Member.objects.get(user = u3)
    #m4 = Member.objects.get(user = u4)
    #m5 = Member.objects.get(user = u5)
    #m6 = Member.objects.get(user = u6)

    date1 = datetime.datetime(2016,5,3)
    ic1 = IndividualCash(member = m1, size = 3340.90, transaction_date = date1)
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
    ic6 = IndividualCash(member=m6, size=3000, transaction_date=date1)
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
    igpls = []
    for row in reader:
        if start_import:
            logger.info(row)
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
            igpls.append(igpl)
            logger.info("Imported " + row[0])

        try:
            if row[0] == 'Closing Ref':
                start_import = True
        except:
            start_import = False
    return igpls

bootstrap_data()
f = open('tmp.txt', 'w')
f.write("#trades1.csv\n")
f.close()

igpls = import_csv(csv_filepathname + '1.csv')
for igpl in igpls:
    igpl.AddAllIndividualPL()

assert (Member.objects.get(user=User.objects.get(email='phil.marsden@softwire.com')).calculated_trade_size == 10.0)
assert (Member.objects.get(user=User.objects.get(email='john.cooper@ensoft.co.uk')).calculated_trade_size == 20.0)
assert (Member.objects.get(user=User.objects.get(email='dan.shavick@softwire.com')).calculated_trade_size == 10.0)
assert (Member.objects.get(user=User.objects.get(email='nigel.ratcliffe@ensoft.co.uk')).calculated_trade_size == 20.0)
assert (Member.objects.get(user=User.objects.get(email='seancurran78@googlemail.com')).calculated_trade_size == 10.0)
assert (Member.objects.get(user=User.objects.get(email='crowecameron@hotmail.com')).calculated_trade_size == 10.0)

#Dan Add more money and make trade size 20
u1 = User.objects.get(email='dan.shavick@softwire.com')
m1 = Member.objects.get(user=u1)
m1.manual_trade_size = 20
m1.save()
m1.set_calculated_trade_size_old()

# Phil automatic trade size in time for May 19th - total = 100

member_list = Member.objects.all()
for m1 in member_list:
    m1.automatic_trade_size = True
    m1.save()

Member.set_all_trade_sizes_old()

f = open('tmp.txt', 'a')
f.write("#trades2.csv\n")
f.close()

igpls = import_csv(csv_filepathname + '2.csv')
for igpl in igpls:
    igpl.AddAllIndividualPL()

assert (Member.objects.get(user=User.objects.get(email='phil.marsden@softwire.com')).calculated_trade_size == 12.0)
assert (Member.objects.get(user=User.objects.get(email='john.cooper@ensoft.co.uk')).calculated_trade_size == 23.0)
assert (Member.objects.get(user=User.objects.get(email='dan.shavick@softwire.com')).calculated_trade_size == 20.0)
assert (Member.objects.get(user=User.objects.get(email='nigel.ratcliffe@ensoft.co.uk')).calculated_trade_size == 23.0)
assert (Member.objects.get(user=User.objects.get(email='seancurran78@googlemail.com')).calculated_trade_size == 11.0)
assert (Member.objects.get(user=User.objects.get(email='crowecameron@hotmail.com')).calculated_trade_size == 11.0)

#exit()

# Meat Liquor Trades
u1 = User.objects.get(email='phil.marsden@softwire.com')
u3 = User.objects.get(email='dan.shavick@softwire.com')
u5 = User.objects.get(email='seancurran78@googlemail.com')
u6 = User.objects.get(email='crowecameron@hotmail.com')

m1 = Member.objects.get(user=u1)
m3 = Member.objects.get(user=u3)
m5 = Member.objects.get(user=u5)
m6 = Member.objects.get(user=u6)
m1.calculated_trade_size = total_calculated_trade_size() /4
m3.calculated_trade_size = total_calculated_trade_size() /4
m5.calculated_trade_size = total_calculated_trade_size() /4
m6.calculated_trade_size = total_calculated_trade_size() /4
m1.current_commission = 0
m3.current_commission = 0
m5.current_commission = 0
m6.current_commission = 0
m1.current_fun_fund = 0
m3.current_fun_fund= 0
m5.current_fun_fund = 0
m6.current_fun_fund = 0

f = open('tmp.txt', 'a')
f.write("#trades3.csv\n")
f.close()

igpls = import_csv(csv_filepathname + '3.csv')
member_list = [m1,m3,m5,m6]
for igpl in igpls:
    for m1 in member_list:
        igpl.AddIndividualPL(m1,member_list)

m1.current_commission = 0.05
m3.current_commission = 0.05
m5.current_commission = 0.05
m6.current_commission = 0.05
m1.current_fun_fund = 0.01
m3.current_fun_fund= 0.01
m5.current_fun_fund = 0.01
m6.current_fun_fund = 0.01

# Add AAron
#u7 = User.objects.create_user('aronrollin@hotmail.com','aronrollin@hotmail.com','jellyfish')
#u7.save()
u7 = User.objects.get(email='aronrollin@hotmail.com')
m7 = Member(user=u7, manual_trade_size=10, current_commission=0.05, current_fun_fund=0.01)
m7.save()
date7 = datetime.datetime(2016, 5, 24)
ic7 = IndividualCash(member=m7, size=3000, transaction_date=date7)
ic7.save()
Member.set_all_trade_sizes(10,30)

# FTSE bet loss
trades_for_phil('4.csv')
trades_for_phil('5.csv')

Member.set_all_trade_sizes(10,30)

f = open('tmp.txt', 'a')
f.write("#trades6.csv\n")
f.close()

# May/June EUR/USD
trades_for_all('6.csv')
assert (Member.objects.get(user=User.objects.get(email='phil.marsden@softwire.com')).calculated_trade_size == 12.0)
assert (Member.objects.get(user=User.objects.get(email='john.cooper@ensoft.co.uk')).calculated_trade_size == 25.0)
assert (Member.objects.get(user=User.objects.get(email='dan.shavick@softwire.com')).calculated_trade_size == 21.0)
assert (Member.objects.get(user=User.objects.get(email='nigel.ratcliffe@ensoft.co.uk')).calculated_trade_size == 25.0)
assert (Member.objects.get(user=User.objects.get(email='seancurran78@googlemail.com')).calculated_trade_size == 12.0)
assert (Member.objects.get(user=User.objects.get(email='crowecameron@hotmail.com')).calculated_trade_size == 12.0)
assert (Member.objects.get(user=User.objects.get(email='aronrollin@hotmail.com')).calculated_trade_size == 10.0)

trades_for_phil('7.csv')

# Add commision to balance when working out balance (used for trade size)
u1 = User.objects.get(email='phil.marsden@softwire.com')
m1 = Member.objects.get(user=u1)
m1.commission_received = 1.0
m1.save()

#6th June 2016 - Nigel add more money
m1 = Member.objects.get(user=User.objects.get(email='nigel.ratcliffe@ensoft.co.uk'))
date1 = datetime.datetime(2016, 6, 6)
ic1 = IndividualCash(member=m1, size=4500, transaction_date=date1)
ic1.save()

#Margin changes
Member.set_all_trade_sizes(10,30)

assert (total_gross_profit() == 8869.45)

f = open('tmp.txt', 'a')
f.write("#trades8.csv\n")
f.close()

trades_for_all('8.csv')

assert (Member.objects.get(user=User.objects.get(email='phil.marsden@softwire.com')).calculated_trade_size == 14.0)
assert (Member.objects.get(user=User.objects.get(email='john.cooper@ensoft.co.uk')).calculated_trade_size == 26.0)
assert (Member.objects.get(user=User.objects.get(email='dan.shavick@softwire.com')).calculated_trade_size == 23.0)
assert (Member.objects.get(user=User.objects.get(email='nigel.ratcliffe@ensoft.co.uk')).calculated_trade_size == 41.0)
assert (Member.objects.get(user=User.objects.get(email='seancurran78@googlemail.com')).calculated_trade_size == 13.0)
assert (Member.objects.get(user=User.objects.get(email='crowecameron@hotmail.com')).calculated_trade_size == 13.0)
assert (Member.objects.get(user=User.objects.get(email='aronrollin@hotmail.com')).calculated_trade_size == 10.0)

trades_for_phil('9.csv')
assert (round(Member.objects.get(user = User.objects.get(email='phil.marsden@softwire.com')).balance,2) == 4533.22)
assert (round(Member.objects.get(user = User.objects.get(email='john.cooper@ensoft.co.uk')).balance,2) == 8331.6)
assert (round(Member.objects.get(user = User.objects.get(email='dan.shavick@softwire.com')).balance,2) == 7156.13)
assert (round(Member.objects.get(user = User.objects.get(email='nigel.ratcliffe@ensoft.co.uk')).balance,2) == 12989.52)
assert (round(Member.objects.get(user = User.objects.get(email='seancurran78@googlemail.com')).balance,2) == 4156.62)
assert (round(Member.objects.get(user = User.objects.get(email='crowecameron@hotmail.com')).balance,2) == 4156.62)
assert (round(Member.objects.get(user = User.objects.get(email='aronrollin@hotmail.com')).balance,2) == 3326.18)

trades_for_phil('10.csv')
assert (total_gross_profit() == 10931.98)

# 30 Jun onwards
trades_for_phil('11.csv')

Member.set_all_trade_sizes(10,30)
# Total = 145
assert (Member.objects.get(user=User.objects.get(email='phil.marsden@softwire.com')).calculated_trade_size == 16.0)
assert (Member.objects.get(user=User.objects.get(email='john.cooper@ensoft.co.uk')).calculated_trade_size == 27.0)
assert (Member.objects.get(user=User.objects.get(email='dan.shavick@softwire.com')).calculated_trade_size == 23.0)
assert (Member.objects.get(user=User.objects.get(email='nigel.ratcliffe@ensoft.co.uk')).calculated_trade_size == 43.0)
assert (Member.objects.get(user=User.objects.get(email='seancurran78@googlemail.com')).calculated_trade_size == 13.0)
assert (Member.objects.get(user=User.objects.get(email='crowecameron@hotmail.com')).calculated_trade_size == 13.0)
assert (Member.objects.get(user=User.objects.get(email='aronrollin@hotmail.com')).calculated_trade_size == 10.0)

f = open('tmp.txt', 'a')
f.write("#trades12.csv\n")
f.close()

# Jul 1st Trades
trades_for_all('12.csv')
assert (total_gross_profit() == 17216.33)
assert (Member.objects.get(user=User.objects.get(email='phil.marsden@softwire.com')).balance == 5926.7775)
assert (Member.objects.get(user=User.objects.get(email='john.cooper@ensoft.co.uk')).balance == 9446.835)
assert (Member.objects.get(user=User.objects.get(email='dan.shavick@softwire.com')).balance == 8106.148999999999)
assert (Member.objects.get(user=User.objects.get(email='nigel.ratcliffe@ensoft.co.uk')).balance == 14765.635)
assert (Member.objects.get(user=User.objects.get(email='seancurran78@googlemail.com')).balance == 4693.5830000000005)
assert (Member.objects.get(user=User.objects.get(email='crowecameron@hotmail.com')).balance == 4693.5830000000005)
assert (Member.objects.get(user=User.objects.get(email='aronrollin@hotmail.com')).balance == 3739.23)

# Jul 1st - Jul 7th Phil
trades_for_phil('13.csv')
assert (total_gross_profit() == 17200.93)

trades_for_phil('14.csv')
assert (total_gross_profit() == 17296.43)

# 8 - 14 July
u1 = User.objects.get(email='phil.marsden@softwire.com')
m1 = Member.objects.get(user=u1)
date1 = datetime.datetime(2016, 7, 11)
ic1 = IndividualCash(member=m1, size=200, transaction_date=date1)
ic1.save()
trades_for_phil('15.csv')
assert (total_gross_profit() == 17267.83)

# 15 - 19 July
trades_for_phil('16.csv')
assert (total_gross_profit() == 17042.43)

trades_for_phil('17-phil.csv')

Member.set_all_trade_sizes(10,30)
#Total = 166

trades_for_all('17-all.csv')
Member.set_all_trade_sizes(10,30)

#30 Aug - JC add more money
m1 = Member.objects.get(user=User.objects.get(email='john.cooper@ensoft.co.uk'))
date1 = datetime.datetime(2016, 8, 30)
ic1 = IndividualCash(member=m1, size=10000, transaction_date=date1)
ic1.save()

Member.set_all_trade_sizes(10,30)
#Total = 208

trades_for_all('18-all.csv')
Member.set_all_trade_sizes(10,30)
assert (total_gross_profit() == 21872.68)


# Sept 1
u1 = User.objects.get(email='phil.marsden@softwire.com')
m1 = Member.objects.get(user=u1)
date1 = datetime.datetime(2016, 9, 1)
ic1 = IndividualCash(member=m1, size=10000, transaction_date=date1)
ic1.save()

m1 = Member.objects.get(user=User.objects.get(email='john.cooper@ensoft.co.uk'))
date1 = datetime.datetime(2016, 9, 1)
ic1 = IndividualCash(member=m1, size=10000, transaction_date=date1)
ic1.save()

m1 = Member.objects.get(user=User.objects.get(email='nigel.ratcliffe@ensoft.co.uk'))
date1 = datetime.datetime(2016, 9, 1)
ic1 = IndividualCash(member=m1, size=9500, transaction_date=date1)
ic1.save()
Member.set_all_trade_sizes(10,30)
#Total = 278

trades_for_all('19.csv')
assert (total_gross_profit() == 14812.98)
assert (Member.objects.get(user=User.objects.get(email='phil.marsden@softwire.com')).calculated_trade_size == 55.0)
assert (Member.objects.get(user=User.objects.get(email='phil.marsden@softwire.com')).balance == 15428.006310681187)
assert (Member.objects.get(user=User.objects.get(email='john.cooper@ensoft.co.uk')).calculated_trade_size == 101.0)
assert (Member.objects.get(user=User.objects.get(email='john.cooper@ensoft.co.uk')).balance == 28252.975871779425)
assert (Member.objects.get(user=User.objects.get(email='dan.shavick@softwire.com')).calculated_trade_size == 29.0)
assert (Member.objects.get(user=User.objects.get(email='dan.shavick@softwire.com')).balance == 8123.691611028729)
assert (Member.objects.get(user=User.objects.get(email='nigel.ratcliffe@ensoft.co.uk')).calculated_trade_size == 84.0)
assert (Member.objects.get(user=User.objects.get(email='nigel.ratcliffe@ensoft.co.uk')).balance == 23587.130449003707)
assert (Member.objects.get(user=User.objects.get(email='seancurran78@googlemail.com')).calculated_trade_size == 16.0)
assert (Member.objects.get(user=User.objects.get(email='seancurran78@googlemail.com')).balance == 4710.090155699721)
assert (Member.objects.get(user=User.objects.get(email='crowecameron@hotmail.com')).calculated_trade_size == 16.0)
assert (Member.objects.get(user=User.objects.get(email='crowecameron@hotmail.com')).balance == 4710.090155699721)
assert (Member.objects.get(user=User.objects.get(email='aronrollin@hotmail.com')).calculated_trade_size == 10.0)
assert (Member.objects.get(user=User.objects.get(email='aronrollin@hotmail.com')).balance == 3759.0095461075066)

Member.set_all_trade_sizes(10,30)
f = open('tmp.txt', 'a') ; f.write("#trades2016-09-08.csv\n") ; f.close()

trades_for_all('2016-09-08.csv')
assert (total_gross_profit() == 14174.98)
assert (Member.objects.get(user=User.objects.get(email='phil.marsden@softwire.com')).calculated_trade_size == 51.0)
#assert (Member.objects.get(user=User.objects.get(email='phil.marsden@softwire.com')).balance == 15302.597310681185)
assert (Member.objects.get(user=User.objects.get(email='john.cooper@ensoft.co.uk')).calculated_trade_size == 94.0)
assert (Member.objects.get(user=User.objects.get(email='john.cooper@ensoft.co.uk')).balance == 27900.09987177943)
assert (Member.objects.get(user=User.objects.get(email='dan.shavick@softwire.com')).calculated_trade_size == 27.0)
assert (Member.objects.get(user=User.objects.get(email='dan.shavick@softwire.com')).balance == 8022.33361102873)
assert (Member.objects.get(user=User.objects.get(email='nigel.ratcliffe@ensoft.co.uk')).calculated_trade_size == 78.0)
assert (Member.objects.get(user=User.objects.get(email='nigel.ratcliffe@ensoft.co.uk')).balance == 23294.31844900371)
assert (Member.objects.get(user=User.objects.get(email='seancurran78@googlemail.com')).calculated_trade_size == 15.0)
assert (Member.objects.get(user=User.objects.get(email='seancurran78@googlemail.com')).balance == 4653.780155699722)
assert (Member.objects.get(user=User.objects.get(email='crowecameron@hotmail.com')).calculated_trade_size == 15.0)
assert (Member.objects.get(user=User.objects.get(email='crowecameron@hotmail.com')).balance == 4653.780155699722)
assert (Member.objects.get(user=User.objects.get(email='aronrollin@hotmail.com')).calculated_trade_size == 10.0)
assert (Member.objects.get(user=User.objects.get(email='aronrollin@hotmail.com')).balance == 3721.4695461075066)
Member.set_all_trade_sizes(10,30)



f = open('tmp.txt', 'a') ; f.write("#trades2016-09-15.csv\n") ; f.close()
trades_for_all('2016-09-15.csv')
assert (Member.objects.get(user=User.objects.get(email='phil.marsden@softwire.com')).balance == 14347.462310681185)
assert (Member.objects.get(user=User.objects.get(email='john.cooper@ensoft.co.uk')).balance == 25638.339871779426)
assert (Member.objects.get(user=User.objects.get(email='dan.shavick@softwire.com')).balance == 7390.01361102873)
assert (Member.objects.get(user=User.objects.get(email='nigel.ratcliffe@ensoft.co.uk')).balance == 21421.678449003706)
assert (Member.objects.get(user=User.objects.get(email='seancurran78@googlemail.com')).balance == 4288.980155699722)
assert (Member.objects.get(user=User.objects.get(email='crowecameron@hotmail.com')).balance == 4288.980155699722)
assert (Member.objects.get(user=User.objects.get(email='aronrollin@hotmail.com')).balance == 3478.269546107507)
assert (total_gross_profit() == 7170.82)
#assert (total_gross_profit() == 10133.73)
Member.set_all_trade_sizes(10,30)

trades_for_all('2016-09-21.csv')
assert (total_gross_profit() == 3129.57)
Member.set_all_trade_sizes(10,30)

trades_for_all('2016-09-27.csv')
assert (total_gross_profit() == 10526.54)
Member.set_all_trade_sizes(10,30)

trades_for_all('2016-10-11.csv')
assert (total_gross_profit() == 18795.79)
Member.set_all_trade_sizes(10,30)

trades_for_all('2016-10-12.csv')
assert (total_gross_profit() == 10330.73)
Member.set_all_trade_sizes(10,30)

trades_for_all('2016-10-25.csv')
trades_for_phil('2016-10-26-Phil.csv')
assert (total_gross_profit() == 8349.63)
Member.set_all_trade_sizes(10,30)