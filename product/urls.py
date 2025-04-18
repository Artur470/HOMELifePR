from django.urls import path
from product.views import *
from django.views.decorators.cache import cache_page
from product.views import ReviewCreateView, ReviewDetailView



urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('brands/', BrandListCreateView.as_view(), name='brand-list'),
    path('brands/<int:pk>/', BrandDetailView.as_view(), name='brand-detail'),
    path('colors/', ColorListCreateView.as_view(), name='color-list'),
    path('colors/<int:pk>/', ColorDetailView.as_view(), name='color-detail'),
    path('homepage/', HomepageView.as_view(), name='homepage'),
    path('all/', ProductListView.as_view(), name='product-all'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('new/', ProductNewView.as_view(), name='product-new'),
    path('popular/', ProductPopularView.as_view(), name='product-popular'),
    path('promotions/', ProductPromotionView.as_view(), name='product-promotions'),
    # path('day/', ProductDayView.as_view(), name='product-of-the-day'),
    path('comment/', ReviewCreateView.as_view(), name='create-review'),  # Маршрут для создания отзыва
    path('<int:product_id>/comments/', ReviewDetailView.as_view(), name='product-comments'),

    # Маршрут для детального просмотра отзыва
    path('banner/', BannerView.as_view(), name='banner-detail'),

    path('archive/', ProductArchiveListView.as_view(), name='product-archive-list'),


]
