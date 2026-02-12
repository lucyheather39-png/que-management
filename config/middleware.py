"""
Middleware to prevent browser caching of all pages.
This ensures that users always get the latest content when navigating.
"""

class NoCacheMiddleware:
    """
    Middleware that adds cache control headers to prevent browser caching
    of dynamic content. This fixes issues where the wrong page content
    is displayed when navigating between pages.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add cache control headers to prevent browser from caching pages
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response
