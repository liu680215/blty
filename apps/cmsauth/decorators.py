from utils import restful
from django.shortcuts import redirect

def my_login_required(func):
    def wrapper(request,*args,**kwargs):
        if request.user.is_authenticated:
            return func(request,*args,**kwargs)
        else:
            if request.is_ajax():
                return restful.auth_error(message='请先登录！')
            else:
                return redirect('/')

    return wrapper