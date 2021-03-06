#要安装：pip install djangorestframework
from django.shortcuts import render
from .models import News,NewsCategory,Comment,Banner
from django.conf import settings
from utils import restful
from .serializers import NewsSerializer,CommentSerializer
from django.http import Http404
from .forms import PublicCommentForm
from apps.cmsauth.decorators import my_login_required
#from django.views.decorators.http import require_POST,require_GET
def index(request):
    count=settings.ONE_PAGE_LOAD_COUNT
    #newses=News.objects.order_by('-put_time')[0:count]
    newses = News.objects.select_related('category','author').all()[0:count]
    categories=NewsCategory.objects.all()
    banners=Banner.objects.all();
    return render(request,'news/index.html',{'newses':newses,'categories':categories,'banners':banners})

#动态加载数据
def news_list(request):
    # 通过p参数，来指定要获取第几页的数据
    # 并且这个p参数，是通过查询字符串的方式传过来的/news/list/?p=2
    page = int(request.GET.get('p', 1))
    # 分类为0：代表不进行任何分类，直接按照时间倒序排序
    category_id = int(request.GET.get('category_id', 0))

    start=(page-1)*settings.ONE_PAGE_LOAD_COUNT
    end=start+settings.ONE_PAGE_LOAD_COUNT
    if category_id == 0:
        # QuerySet
        # {'id':1,'title':'abc',category:{"id":1,'name':'热点'}}
        newses = News.objects.select_related('category', 'author').all()[start:end] #select_related优化性能
        #newses = News.objects.all()[start:end]
    else:
        newses = News.objects.select_related('category', 'author').filter(category__id=category_id)[start:end]
        #newses = News.objects.filter(category__id=category_id)[start:end]
    serializer = NewsSerializer(newses, many=True)
    data = serializer.data
    return restful.result(data=data)

def news_detail(request,news_id):
    try:
        news=News.objects.select_related('category','author').prefetch_related('comments').get(pk=news_id)
        return  render(request,'news/news_detail.html',{'news':news})
    except:
        raise Http404
def search(request):
    return render(request,'search/search.html')
#发布评论
@my_login_required
def public_comment(request):
    form=PublicCommentForm(request.POST)
    if form.is_valid():
        content=form.cleaned_data.get('content')
        news_id=form.cleaned_data.get('news_id')
        news=News.objects.get(pk=news_id)
        comment=Comment.objects.create(content=content,news=news,author=request.user)
        serializer=CommentSerializer(comment)
        return restful.result(data=serializer.data)
    else:
        return restful.params_error(message=form.get_errors())