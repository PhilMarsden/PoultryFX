from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from pfx.models import Member

from .models import IGPL,IndividualPL,IndividualCash

@login_required
def profile(request):
    m = Member.objects.get(user = request.user)
    trades = IndividualPL.objects.filter(member = m)
    template = loader.get_template('pfx/profile.html')
    context = {
        'trades': trades,
        'member' : m,
    }
    return HttpResponse(template.render(context, request))


