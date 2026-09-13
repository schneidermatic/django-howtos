from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    # Show what Django sees behind the Nginx reverse proxy
    context = {
        'is_secure': request.is_secure(),
        'host': request.get_host(),
        'server': request.META.get('SERVER_SOFTWARE', '-'),
        'client_ip': request.META.get('HTTP_X_REAL_IP', request.META.get('REMOTE_ADDR')),
        'forwarded_for': request.META.get('HTTP_X_FORWARDED_FOR', '-'),
    }
    return render(request, 'core/index.html', context)


def healthz(request):
    # Used by the health check of the 'web' container
    return HttpResponse('ok', content_type='text/plain')
