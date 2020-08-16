from django.urls import path
from . import views
app_name='cmsauth'
urlpatterns=[
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('img_captcha/',views.img_captcha,name='img_captcha'),
    path('sms-captcha/',views.sms_captcha,name='sms_captcha'),
    path('register/',views.register_view,name='register'),
    path('cache/',views.cache_test,name='cache')
]