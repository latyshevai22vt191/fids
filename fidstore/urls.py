from django.urls import path

from .views import *

urlpatterns = [
    path('batiskaf.xml/', get_batiskaf_list),
    path('parse_batiskaf/', parse_batiskaf),
    path('drevodesign.xml/', get_drevodesign_list),
    path('parse_drevodesign/', parse_drevodesign),
    ]