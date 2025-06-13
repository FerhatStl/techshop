from django.urls import path
from . import views
from .views import account_page, add_address, add_card, checkout, delete_address, delete_card


urlpatterns = [
    path('', views.index, name='index'),
    path('categories/', views.categories),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('products/', views.products_by_category, name='products_by_category'),
    path('search/', views.search_products, name='search_products'),
    path('account/', account_page, name='account'),
    path('account/add_address/', add_address, name='add_address'),
    path('account/add_card/', add_card, name='add_card'),
    path('checkout/', checkout, name='checkout'),
    path('account/delete_address/<int:address_id>/', delete_address, name='delete_address'),
    path('account/delete_card/<int:card_id>/', delete_card, name='delete_card'),
    path('order/<int:order_id>/details/', views.order_detail, name='order_detail'),
]