from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from imagens import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html')),
    path('upload/', views.upload),
    path('lista/', views.lista),
    path('status/<int:imagem_id>/', views.status),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
