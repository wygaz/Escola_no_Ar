from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import raiz_inteligente, PortalDashboardView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", raiz_inteligente, name="raiz"),
    path("portal/", PortalDashboardView.as_view(), name="portal"),

    # Foco no Vocacional
    path("vocacional/", include(("apps.vocacional.urls", "vocacional"), namespace="vocacional")),
    path("contas/", include(("apps.contas.urls", "contas"), namespace="contas")),
    path("projeto21/", include(("apps.projeto21.urls", "projeto21"), namespace="projeto21")),

    # Webhooks (Hotmart)
    path("webhooks/", include("apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
