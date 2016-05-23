from django.contrib import admin
from django.contrib.sites.models import Site

from .models import *


#admin.site.register(Site)
admin.site.register(IGPL)
admin.site.register(Member)
admin.site.register(IndividualPL)
admin.site.register(IndividualCash)
admin.site.register(TradeEmail)