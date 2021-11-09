from django.urls import path, include

from lfp import views
from rest_framework.urlpatterns import format_suffix_patterns

from django.conf import settings
from django.conf.urls.static import static

# Using Router
from rest_framework.routers import DefaultRouter

router = DefaultRouter()  #  automatically creates the API root view
router.register('lfp', views.LogFileProcessorViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]

#+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
