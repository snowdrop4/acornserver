from django.shortcuts import render

from .models import NewsArticle


def homepage(request):
	articles = NewsArticle.objects.order_by('-pub_date')[:5]
	
	print(f"pub={articles[0].pub_date}, mod={articles[0].mod_date}")
	
	return render(request, 'root/homepage.html', { 'articles': articles })


def about(request):
	return render(request, 'root/about.html', { })
