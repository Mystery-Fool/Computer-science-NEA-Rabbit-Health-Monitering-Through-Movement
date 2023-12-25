from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib.auth import logout


def mainpage(request):
    if request.user.is_authenticated:
        template = loader.get_template('mainpage/mainpage.html')
        return HttpResponse(template.render())
    else:    
        return redirect("login/")
    
from django.contrib.auth import logout

def login(request):
    pass