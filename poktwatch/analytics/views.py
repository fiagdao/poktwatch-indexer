from django.shortcuts import render
from .models import *

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.decorators import login_required
import decimal
from django import template
from django.template.loader import get_template
import sys

# LETS JSON ENCODE DECIMALS (MAINLY USED FOR TESTING)
def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def error_404(request, exception):
    return render(request, "404.html")

def dashboard(request):

    price_data = []

    # txs = Transaction.objects.using('thunderhead').all().filter(status="COMPLETED")
    txs = Transaction.objects.using('thunderhead').raw("SELECT * FROM main_transaction where status='COMPLETED'")

    for t in txs:
        # print(t.price)
        price_data.append({"x": t.dateFilled.timestamp()*1000, "y": t.price, "value": t.volume*t.price,"stringDate":t.dateFilled.strftime('%m/%d/%Y')})

    # print(txs, "txs")

    return render(request, "analytics/index.html", {
        "transactions": price_data
    })

def error505(request, template_name='nondefault505.html'):
    """
    500 error handler.
    Templates: `500.html`
    Context: sys.exc_info() results
     """ # You need to create a 500.html template.
    ltype,lvalue,ltraceback = sys.exc_info()
    # sys.exc_clear() #for fun, and to point out I only -think- this hasn't happened at
                    #this point in the process already
    return render(request, "nondefault505.html", {
    'type':ltype,'value':lvalue,'traceback':ltraceback
    })
