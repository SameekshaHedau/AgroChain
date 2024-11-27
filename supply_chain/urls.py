# supply_chain/urls.py
from django.urls import path
from .views import dashboard, list_crops, buy_crops, transaction_history
# from supply_chain.views import farmer_dashboard, distributor_dashboard, consumer_dashboard  # Import your views here
from .views import home,register  # Import your home view
from .views import profile_view, edit_crop_price
from . import views
from django.urls import path
from .views import custom_login,my_crops
from .views import buy_crops, purchased_crops
from .views import trace_crops,list_crops,view_blockchain, buy_crops, sell_crop, trace_crop
from .views import blockchain_status  # Import your new view
# urlpatterns = [
#     path('', home, name='home'),  # Map root URL to the home view
#     path('dashboard/', dashboard, name='dashboard'),
#     path('list_crops/', list_crops, name='list_crops'),
#     path('buy_crop/<int:crop_id>/', buy_crop, name='buy_crop'),
#     path('transaction_history/', transaction_history, name='transaction_history'),
#     path('register/', register, name='register'),
# ]



urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', home, name='home'),  #Replace home_view with your home view function
    path('register/', register, name='register'),
    path('dashboard/', dashboard, name='dashboard'),
    #adding new dashboard urls beacuse early ones are not working 
    # path('farmer-dashboard/', farmer_dashboard, name='farmer_dashboard'),
    # path('distributor-dashboard/', distributor_dashboard, name='distributor_dashboard'),
    # path('consumer-dashboard/', consumer_dashboard, name='consumer_dashboard'),
    # #end of changes
    path('list_crops/', list_crops, name='list_crops'),
    path('buy_crops/<int:crop_id>/', buy_crops, name='buy_crops'),
    path('transaction_history/', transaction_history, name='transaction_history'),
    path('register/', register, name='register'),
    path('accounts/profile/', profile_view, name='profile'),  # Add this line
    path('accounts/login/', custom_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    # path('logout/success/', views.logout_success, name='logout_success'),  # Add this line
    path('sell_crop/', sell_crop, name='sell_crop'),
    path('trace_crops/', trace_crops, name='trace_crops'),
    path('blockchain_status/', blockchain_status, name='blockchain_status'),
    # other URL patterns...
    path('my-crops/', my_crops, name='my_crops'),
    path('edit-crop-price/<int:crop_id>/', edit_crop_price, name='edit_crop_price'),
    path('accounts/logout/', views.user_logout, name='logout'),
    path('purchased_crops/', purchased_crops, name='purchased_crops'),
    path('blockchain/', view_blockchain, name='view_blockchain'),
]
