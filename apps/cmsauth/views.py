from django.contrib.auth import login,logout,authenticate
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect,reverse
from django.http import HttpResponse
from .forms import LoginForm,RegisterForm
from utils import restful
from utils.aliyun.aliyunsms import send_sms
from PIL import Image
from utils.captcha.cmscaptcha import Captcha
from io import BytesIO
#使用memcached之前必须安装它：pip install python-memcached
from django.core.cache import cache
from django.contrib.auth import get_user_model
User=get_user_model()

@require_POST
@csrf_exempt
def login_view(request):
    form=LoginForm(request.POST)
    if form.is_valid():
        telephone=form.cleaned_data.get('telephone')
        password=form.cleaned_data.get('password')
        remember=form.cleaned_data.get('remember')
        user=authenticate(request,username=telephone,password=password)
        if user:
            if user.is_active:
                login(request,user)
                if remember:
                    request.session.set_expiry(None)
                else:
                    request.session.set_expiry(0)
                #return JsonResponse({"code":200,"message":"","data":{}})
                return  restful.ok()
            else:
                #return  JsonResponse({"code":401,"message":"","data":{}})
                return  restful.auth_error(message="你的帐户被冻结了")
        else:
            return restful.params_error(message="手机号码或密码错误")
    else:
        errors=form.get_errors()
        return  restful.params_error(message=errors)
#退出登录
def logout_view(request):
    logout(request)
    return redirect(reverse('index'))
#用户注册
@require_POST
def register_view(request):
    form=RegisterForm(request.POST)
    if form.is_valid():
        telephone=form.cleaned_data.get('telephone')
        username=form.cleaned_data.get('username')
        password=form.cleaned_data.get('password1')
        user=User.objects.create(telephone=telephone,username=username) #注册成功
        user.set_password(password)
        user.save()
        login(request,user) #进入登录状态
        return restful.ok()
    else:
        return restful.params_error(message=form.get_errors())

#生成验证码数据
def img_captcha(request):
    text,img=Captcha.gene_code()
    cache.set(text.lower(), text.lower(), 5 * 60)  # 把信息存入memcached中
    out=BytesIO() #BytesIO相当于一个管道，用来存储图片数据流
    img.save(out,'png') #将image数据对象保存到BytesIO中
    out.seek(0) #光标移到BytesIO最开始的位置

    response=HttpResponse(content_type='image/png')
    #BytesIO管理中读取数据,保存到response对象上
    response.write(out.read())
    response['Content-length']=out.tell()
    return  response
#手机短信发送验证
def sms_captcha(request):
    telephone=request.GET.get('telephone') #获取电话号码
    code=Captcha.gene_text() #获取随机号码
    cache.set(telephone, code.lower(), 5 * 60)  # 把信息存入memcached中
    #result = send_sms(telephone,code)
    print(code)
    return  restful.ok()
#测试memcached
def cache_test(request):
    cache.set('username','天缘电脑',60)
    result=cache.get('username')
    print(result)
    return  HttpResponse('success')