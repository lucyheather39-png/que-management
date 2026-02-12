"""
Middleware to prevent browser caching of all pages.
This ensures that users always get the latest content when navigating.
"""

class NoCacheMiddleware:
    """
    Middleware that adds aggressive cache control headers to prevent browser,
    proxy, and CDN caching of dynamic content. This ensures fresh content is
    always fetched when navigating between pages.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Set aggressive cache control headers for all responses
        # This prevents caching at browser, proxy, and CDN levels
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        response['Vary'] = 'Accept-Encoding'
        
        # Tell proxies not to cache
        response['X-Accel-Expires'] = '0'
        
        return response
