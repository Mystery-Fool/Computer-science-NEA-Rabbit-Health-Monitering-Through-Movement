from django.http import HttpResponse
from django.template import loader

def mainpage(request):
    template = loader.get_template('mainpage.html')
    return HttpResponse(template.render())