from django.db import models
# Create your models here.
class NewsCategory(models.Model):
    name=models.CharField(max_length=100)

class News(models.Model):
    title=models.CharField(max_length=200)
    desc=models.CharField(max_length=200)
    thumbnail=models.URLField()
    content=models.TextField()
    put_time=models.DateTimeField(auto_now_add=True)
    category=models.ForeignKey('NewsCategory',on_delete=models.SET_NULL,null=True)
    author=models.ForeignKey('cmsauth.User',on_delete=models.SET_NULL,null=True)
    class Meta:
        ordering = ['-put_time']
#评论
class Comment(models.Model):
    content=models.TextField()
    pub_time=models.DateTimeField(auto_now_add=True)
    author=models.ForeignKey('cmsauth.User',on_delete=models.CASCADE,null=True)
    news=models.ForeignKey('News',on_delete=models.CASCADE,related_name='comments')
    class Meta:
        ordering=['-pub_time']
#轮播图
class Banner(models.Model):
    priority = models.IntegerField(default=0)
    image_url=models.URLField()
    link_to=models.URLField()
    pub_time=models.DateTimeField(auto_now_add=True)
    #排序
    class Meta:
        ordering=['-priority']