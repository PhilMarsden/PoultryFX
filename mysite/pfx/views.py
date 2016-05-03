from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader
from django.contrib.auth.decorators import login_required
from pfx.models import Member
from pfx.ig.rest import ig_rest

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


@login_required
def ig_view(request):
    if ig_rest.need_password():
        if request.method == 'POST':
            print (request.POST['password'])
            # create a form instance and populate it with data from the request:
            ig_rest.set_password(request.POST['password'])
            ig_rest.login()
            return HttpResponseRedirect('/pfx/ig_view/')
        else:
            template = loader.get_template('pfx/ig_get_password.html')
            context = {'identifier': ig_rest.get_identifier(),
                       }
            return HttpResponse(template.render(context, request))

    else:
        template = loader.get_template('pfx/ig_view.html')
        positions = ig_rest.get_positions()
        transactions = ig_rest.get_transactions()
        context = {'positions':positions,
                   'transactions':transactions,}
        return HttpResponse(template.render(context, request))



