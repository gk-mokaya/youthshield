from .models import WebsiteSetting

def website_info(request):
    try:
        website_settings = WebsiteSetting.objects.first()
    except:
        website_settings = None
    
    return {
        'website_settings': website_settings,
    }