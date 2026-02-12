"""
Middleware to prevent browser caching of dynamic pages.
This ensures that users always get the latest content when navigating.
"""

class NoCacheMiddleware:
    """
    Middleware that adds cache control headers to prevent browser,
    proxy, and CDN caching of dynamic content. This ensures fresh content is
    always fetched when navigating between pages.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Only apply no-cache to HTML responses (not static files, images, etc.)
        content_type = response.get('Content-Type', '')
        if 'text/html' in content_type:
            # Set cache control headers for HTML responses
            # This prevents caching at browser, proxy, and CDN levels
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['Vary'] = 'Accept-Encoding'
            
            # Tell proxies not to cache
            response['X-Accel-Expires'] = '0'
        
        return response
