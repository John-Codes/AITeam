from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        # Incluye los contextos diferentes para la misma URL base
        return [
            'login', 
            'signup', 
            'subscription', 
            ('ai-team', 'main'),
            ('ai-team', 'panel-admin'),
            ('ai-team', 'subscriptions')
        ]

    def location(self, item):
        if isinstance(item, tuple):
            # Maneja URLs con múltiples componentes (como las del chat)
            return reverse(item[0], args=[item[1]])
        else:
            # Maneja URLs estándar
            return reverse(item)