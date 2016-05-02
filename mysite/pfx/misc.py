import os,django,csv,codecs,sys,datetime
path = 'E:\\Work\\\PoultryFX\\\mysite'  # use your own username here
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()


from django.contrib.auth.models import User
from pfx.models import Member, IGPL, IndividualPL, IndividualCash

u1 = User.objects.get(email='phil.marsden@softwire.com')

m1 = Member.objects.get(user=u1)

IndividualCash.objects.filter(member_id=self.id).aggregate(Sum('size'))


