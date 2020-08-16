from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from shortuuidfield import ShortUUIDField
from django.db import models

class UserManager(BaseUserManager):
    def _create_self(self,telephone,username,password,**kwargs):
        if not telephone:
            raise ValueError('请传入手机号码')
        if not username:
            raise  ValueError('请输入用户名')
        if not password:
            raise  ValueError('请输入密码')
        user=self.model(telephone=telephone,username=username,**kwargs)
        user.set_password(password)
        user.save()
        return  user
    def create_user(self,telephone,username,password,**kwargs):
        kwargs['is_superuser']=False
        return self._create_self(telephone,username,password,**kwargs)
    def create_superuser(self,telephone,username,password,**kwargs):
        kwargs['is_superuser']=True
        kwargs['is_staff']=True
        return self._create_self(telephone, username, password, **kwargs)

class User(AbstractBaseUser,PermissionsMixin):
    '''首先安装第三包：pip install django-shortuuidfield'''
    uid=ShortUUIDField(primary_key=True)
    telephone=models.CharField(max_length=11,unique=True)
    email=models.EmailField(unique=True,null=True)
    username=models.CharField(max_length=100)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False) #是否为员工，只有员工才能进入后台管理系统
    date_joined=models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD='telephone'
    REQUIRED_FIELDS = ['username']
    EMAIL_FIELD='email'

    objects=UserManager()

    def get_full_name(self):
        return  self.username
    def get_short_name(self):
        return  self.username