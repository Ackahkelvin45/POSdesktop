# pos/urls.py (or your project's main urls.py)
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

# Import the websocket URL patterns

urlpatterns = [
    # WebSocket URL routing

    # Other regular URL patterns
    path('admin/', admin.site.urls),
    path("auth/", include("authentication.urls")),
    path("", include("dashboard.urls")),
    path("users/", include("users.urls")),
    path("product/", include("product.urls")),
    path("permission/", include("permissions.urls")),
  path("inventory/", include("inventory.urls")),
  path("activities/", include("activities.urls")),
    path("notifications/", include("notifications.urls")),
    path("sales/", include("sales.urls"))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
