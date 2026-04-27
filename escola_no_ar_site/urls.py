# escola_no_ar_site/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.core import views as core_views

urlpatterns = [
    # entrada pública: anônimo vai para login; autenticado segue para o portal
    path("", core_views.home_funil, name="inicio"),

    # portal pós-login (o nome 'portal' precisa apontar aqui)
    path("portal/", core_views.portal_home, name="portal"),
    path("portal/demo/", core_views.portal_demo, name="portal_demo"),
    path("portal/proxima-etapa/", core_views.portal_next_step, name="portal_next_step"),
    path("produtos/<slug:produto_slug>/entrar/", core_views.produto_resolver, name="produto_resolver"),

    # Termos / Privacidade (módulo geral do Core)
    path("legal/", include(("apps.core.urls_legal", "core"), namespace="core")),

    path("home/", core_views.sonhe_mais_alto_landing, name="home"),
    path("admin/", admin.site.urls),
    path("contas/", include(("apps.contas.urls", "contas"), namespace="contas")),
    path("es/", include(("apps.es.urls", "es"), namespace="es")),
    path("sonhe-mais-alto/", core_views.sonhe_mais_alto_landing, name="sonhe_mais_alto_landing"),
    path("projeto21/", include(("apps.projeto21.urls", "projeto21"), namespace="projeto21")),
    path("vocacional/", include(("apps.vocacional.urls", "vocacional"), namespace="vocacional")),

    # governança (dashboard.html)
    path("portal/dashboard/", core_views.PortalDashboardView.as_view(), name="portal_dashboard"),

    # staff: testar como usuário (impersonação)
    path("portal/impersonar/", core_views.portal_impersonar, name="portal_impersonar"),
    path("portal/impersonar/sair/", core_views.portal_impersonar_sair, name="portal_impersonar_sair"),

    path("guia/", core_views.guia_redirect_preview, name="guia"),
    path("sobre/", core_views.sobre, name="sobre"),
    path("contato/", core_views.contato, name="contato"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
