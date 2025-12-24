from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import raiz_inteligente, PortalDashboardView
from apps.core import views as core_views
from django.views.generic import RedirectView

urlpatterns = [
    path("", core_views.sonhe_mais_alto_landing, name="home"), # home temporária para o Projeto Sonhe + Alto
    path("admin/", admin.site.urls),
    #path("", raiz_inteligente, name="raiz"), - Home geral para Escola no Ar
    path("portal/", PortalDashboardView.as_view(), name="portal"),

    # Foco no Vocacional
    path("vocacional/", include(("apps.vocacional.urls", "vocacional"), namespace="vocacional")),
    path("contas/", include(("apps.contas.urls", "contas"), namespace="contas")),
    path("projeto21/", include(("apps.projeto21.urls", "projeto21"), namespace="projeto21")),
    path("guia/", core_views.guia_redirect_preview, name="guia"),

    # Webhooks (Hotmart)
    path("webhooks/", include("apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    