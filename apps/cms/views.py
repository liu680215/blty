from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import View
from django.views.decorators.http import require_POST, require_GET
from apps.news.models import NewsCategory, News, Banner
from .forms import EditCategoryForm, WriteNewsForm, EditBannerForm, AddBannerForm, EditNewsForm
from apps.news.serializers import BannerSerializer
from utils import restful
import os
from django.conf import settings
import qiniu
from django.core.paginator import Paginator
from datetime import datetime
from django.utils.timezone import make_aware
from urllib import parse


@staff_member_required(login_url='index')  # 如果不是员工，直接进入首页，不能进入后台管理系统
def index(request):
    return render(request, 'cms/index.html')


class WriteNewView(View):
    def get(self, request):
        categories = NewsCategory.objects.all()
        return render(request, 'cms/write_news.html', {'categories': categories})

    def post(self, request):
        form = WriteNewsForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            desc = form.cleaned_data.get('desc')
            thumbnail = form.cleaned_data.get('thumbnail')
            content = form.cleaned_data.get('content')
            category_id = form.cleaned_data.get('category')
            category = NewsCategory.objects.get(pk=category_id)
            News.objects.create(title=title, desc=desc, thumbnail=thumbnail, content=content, category=category,
                                author=request.user)
            return restful.ok()
        else:
            return restful.params_error(message=form.get_errors())


# 编辑新闻
class EditNewView(View):
    def get(self, request):
        news_id = request.GET.get('news_id')
        news = News.objects.get(pk=news_id)
        categories = NewsCategory.objects.all()
        return render(request, 'cms/write_news.html', {'news': news, 'categories': categories})

    def post(self, request):
        form = EditNewsForm(request.POST)
        if form.is_valid():
            pk = form.cleaned_data.get('pk')
            title = form.cleaned_data.get('title')
            desc = form.cleaned_data.get('desc')
            thumbnail = form.cleaned_data.get('thumbnail')
            content = form.cleaned_data.get('content')
            category_id = form.cleaned_data.get('category')
            category = NewsCategory.objects.get(pk=category_id)
            News.objects.filter(pk=pk).update(title=title, desc=desc, thumbnail=thumbnail, category=category,
                                              content=content)
            return restful.ok()
        else:
            return restful.method_error(message=form.get_errors())

#删除新闻
@require_GET
def DeleteNews(request):
    news_id=request.GET.get('news_id')
    News.objects.get(pk=news_id).delete()
    return restful.ok()

# 新闻分类
@require_GET
def news_category(request):
    newslist = NewsCategory.objects.all()
    return render(request, 'cms/news-category.html', {'categories': newslist})


# 添加分类
@require_POST
def add_news_category(request):
    name = request.POST.get('name')
    exists = NewsCategory.objects.filter(name=name).exists()
    if not exists:
        NewsCategory.objects.create(name=name)
        return restful.ok()
    else:
        return restful.params_error(message='该分类已经存在！')


# 更新分类
@require_POST
def edit_news_category(request):
    form = EditCategoryForm(request.POST)
    if form.is_valid():
        pk = form.cleaned_data.get('pk')
        name = form.cleaned_data.get('name')
        exists = NewsCategory.objects.filter(name=name).exists()
        if exists:
            return restful.params_error(message="已经有此类名称！")
        else:
            try:
                NewsCategory.objects.filter(pk=pk).update(name=name)
                return restful.ok()
            except:
                return restful.params_error(message="该分类ID不存在！")
    else:
        return restful.params_error(message=form.get_error())


# 删除分类
@require_POST
def delete_news_category(request):
    pk = request.POST.get('pk')
    try:
        NewsCategory.objects.filter(pk=pk).delete()
        return restful.ok()
    except:
        return restful.params_error(message="没有此分类ID")


# 上传文件
@require_POST
def upload_file(request):
    file = request.FILES.get('file')
    name = file.name
    with open(os.path.join(settings.MEDIA_ROOT, name), 'wb') as fp:
        for chunk in file.chunks():
            fp.write(chunk)
    url = request.build_absolute_uri(settings.MEDIA_URL + name)
    return restful.result(data={'url': url})


# 获取七牛token,以便通过javascript进行文件上传
@require_GET
def qntoken(request):
    AccessKey = settings.QINIU_ACCESS_KEY
    SecretKey = settings.QINIU_SECRET_KEY
    bucket = settings.QINIU_BUCKET_NAME  # hnroom为七年云上的空间名称
    q = qiniu.Auth(AccessKey, SecretKey)
    token = q.upload_token(bucket=bucket)

    return restful.result(data={'token': token})


# 添加轮播图
def banners(request):
    return render(request, 'cms/banners.html')


def banner_list(request):
    banners = Banner.objects.all()
    serialize = BannerSerializer(banners, many=True)
    return restful.result(data=serialize.data)


def add_banner(request):
    form = AddBannerForm(request.POST)
    if form.is_valid():
        priority = form.cleaned_data.get('priority')
        image_url = form.cleaned_data.get('image_url')
        link_to = form.cleaned_data.get('link_to')
        banner = Banner.objects.create(priority=priority, image_url=image_url, link_to=link_to)
        return restful.result(data={"banner_id": banner.pk})
    else:
        return restful.params_error(message=form.get_errors())


def delete_banner(request):
    banner_id = request.POST.get('banner_id')
    Banner.objects.filter(pk=banner_id).delete()
    return restful.ok()


def edit_banner(request):
    form = EditBannerForm(request.POST)
    if form.is_valid():
        pk = form.cleaned_data.get('pk')
        image_url = form.cleaned_data.get('image_url')
        link_to = form.cleaned_data.get('link_to')
        priority = form.cleaned_data.get('priority')
        Banner.objects.filter(pk=pk).update(image_url=image_url, link_to=link_to, priority=priority)
        return restful.ok()
    else:
        return restful.params_error(message=form.get_errors())


class NewsListView(View):
    def get(self, request):
        page = int(request.GET.get('p', 1))  # 当前页码
        start = request.GET.get('start')
        end = request.GET.get('end')
        title = request.GET.get('title')
        category_id = int(request.GET.get('category', 0))

        categories = NewsCategory.objects.all()
        newses = News.objects.select_related('author', 'category')

        if start and end:
            start_date = datetime.strptime(start, '%Y-%m-%d')
            end_date = datetime.strptime(end + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            newses = newses.filter(put_time__range=(make_aware(start_date), make_aware(end_date)))
        if title:
            newses = newses.filter(title__icontains=title)
        if category_id:
            newses = newses.filter(category=category_id)

        paginator = Paginator(newses, 3)  # 2表示每页显示的行数
        page_obj = paginator.page(page)
        cur_page_data = page_obj.object_list
        context_data = self.get_pagination_data(paginator, page_obj)
        context = {
            'categories': categories,
            'newses': cur_page_data,
            'page_obj': page_obj,
            'paginator': paginator,
            'start': start,
            'end': end,
            'title': title,
            'category_id': category_id,
            'url_query': '&' + parse.urlencode({
                'start': start or '',
                'end': end or '',
                'title': title or '',
                'category': category_id or 0
            })
        }
        context.update(context_data)
        return render(request, 'cms/news_list.html', context=context)

    def get_pagination_data(self, paginator, page_obj, around_count=2):
        current_page = page_obj.number
        num_pages = paginator.num_pages

        left_has_more = False
        right_has_more = False

        if current_page <= around_count + 2:
            left_pages = range(1, current_page)
        else:
            left_has_more = True
            left_pages = range(current_page - around_count, current_page)

        if current_page >= num_pages - around_count - 1:
            right_pages = range(current_page + 1, num_pages + 1)
        else:
            right_has_more = True
            right_pages = range(current_page + 1, current_page + around_count + 1)

        return {
            'left_pages': left_pages,
            'right_pages': right_pages,
            'current_page': current_page,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'num_pages': num_pages
        }
