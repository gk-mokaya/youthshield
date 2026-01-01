import uuid
from django.http import JsonResponse
from django.urls import reverse

class TabIndependentSessionMiddleware:
    """
    Middleware to enforce tab-independent sessions.
    Each browser tab must have its own authentication token stored in sessionStorage.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip middleware for certain paths
        exempt_paths = [
            '/login/',
            '/register/',
            '/admin/',
            '/static/',
            '/media/',
            '/api/',
        ]

        if any(request.path.startswith(path) for path in exempt_paths):
            return self.get_response(request)

        # Check if user is authenticated
        if request.user.is_authenticated:
            # Get tab token from header, cookie, or POST data
            tab_token = (
                request.headers.get('X-Tab-Token') or
                request.COOKIES.get('tab_token') or
                request.POST.get('tab_token')
            )

            if not tab_token:
                # No tab token provided - treat as unauthenticated
                from django.contrib.auth.models import AnonymousUser
                request.user = AnonymousUser()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'authenticated': False,
                        'login_url': '/login/',
                        'error': 'Tab token required'
                    }, status=401)
                else:
                    from django.shortcuts import redirect
                    return redirect('users:login')

            # Validate tab token against session
            session_tab_token = request.session.get('tab_token')
            if not session_tab_token or session_tab_token != tab_token:
                # Invalid or missing tab token - treat as unauthenticated
                from django.contrib.auth.models import AnonymousUser
                request.user = AnonymousUser()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'authenticated': False,
                        'login_url': '/login/',
                        'error': 'Invalid tab token'
                    }, status=401)
                else:
                    from django.shortcuts import redirect
                    return redirect('users:login')

        response = self.get_response(request)
        return response
