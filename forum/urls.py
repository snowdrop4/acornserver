from django.urls import path

from .views import index, thread, category

app_name = 'forum'
urlpatterns = [
    path('index', index.view, name='index_view'),

    path('category/view/<int:pk>', category.view, name='category_view'),

    path('thread/add',           thread.add,  name='thread_add'),
    path('thread/view/<int:pk>', thread.view, name='thread_view'),
]
