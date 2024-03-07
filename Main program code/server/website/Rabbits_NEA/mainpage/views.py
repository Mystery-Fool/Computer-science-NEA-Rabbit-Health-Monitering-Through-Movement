from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect

#below all mine
from mainpage.backend_management.backend_handler import handler


def mainpage(request):
    """
    Renders the main page view aggrogating the required data into one place.

    Args:
        request: The HTTP request object.

    Returns:
        An HTTP response containing the rendered main page template.
    """
    if request.user.is_authenticated:
        # Call out to other modules
        template = loader.get_template('mainpage/mainpage.html')
        backend = handler()
        hypothesis, times = backend.handle_website()
        context = {
            "cinny_hypothesis": hypothesis[0],
            "cleo_hypothesis": hypothesis[1],
            "cinny_time": times[0],
            "cleo_time": times[1]
        }
        return HttpResponse(template.render(context))
    else:    
        return redirect("login/")
    
def print(request):
    """
    Renders the print view aggrogating the data together.

    Args:
        request: The HTTP request object.

    Returns:
        An HTTP response containing the rendered print template.
    """
    if request.user.is_authenticated:
        template = loader.get_template('mainpage/print.html')
        backend = handler()
        hypothesis, times = backend.handle_report()
        context = {
            "cinny_hypothesis": hypothesis[0],
            "cleo_hypothesis": hypothesis[1],
            "cinny_time": times[0],
            "cleo_time": times[1]
        }
        return HttpResponse(template.render(context))
    else:    
        return redirect("../login/")