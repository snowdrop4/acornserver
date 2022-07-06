from django.shortcuts import render

from .models import NewsArticle


def homepage(request):
	articles = NewsArticle.objects.order_by('pub_date')[:5]
	
	return render(request, 'root/homepage.html', { 'articles': articles })
