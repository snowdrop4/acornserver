from django.conf import settings
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path("", include("root.urls")),
    path("account/", include("account.urls")),
    path("api/", include("api.urls")),
    path("forum/", include("forum.urls")),
    path("inbox/", include("inbox.urls")),
    path("search/", include("search.urls")),
    path("torrent/", include("torrent.urls")),
    path("tracker/", include("tracker.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("debug/", include("debug.urls")),
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
