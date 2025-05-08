from django.contrib import admin
from django.urls import path, include
from myproject import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from users.views import TokenRefreshView  # Используем кастомный TokenRefreshView
from rest_framework_simplejwt.views import TokenRefreshView as SimpleJWTTokenRefreshView  # Для использования стандартного токена, если нужно

# Настройка для генерации схемы документации API
schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",  # Измените описание на ваше собственное
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Подключение URL'ов приложений
    path('product/', include('product.urls')),
    path('users/', include('users.urls')),
    path('cart/', include('cart.urls')),

    # Эндпоинт для обновления токенов (используем кастомный или стандартный по вашему выбору)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # path('api/token/refresh/', SimpleJWTTokenRefreshView.as_view(), name='token_refresh'),  # Если используете стандартный

    # Документация API (Swagger UI, JSON и ReDoc)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),  # Для получения JSON схемы
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Статические файлы
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

