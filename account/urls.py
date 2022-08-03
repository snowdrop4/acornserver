from django.urls import path
from django.contrib.auth import views as auth_views
from global_login_required import login_not_required

from . import views as account_views


app_name = 'account'
urlpatterns = [
	path('signup/',  login_not_required(account_views.signup), name='signup'),
	path('signin/',  login_not_required(auth_views.LoginView.as_view(template_name='account/authentication/signin.html')), name='signin'),
	path('signout/', auth_views.logout_then_login, name='signout'),
	
	path('profile/view/<int:pk>', account_views.profile_view, name='profile_view'),
	
	path('profile/edit', account_views.profile_edit, name='profile_edit'),
	path('account/edit', account_views.account_edit, name='account_edit'),
]
