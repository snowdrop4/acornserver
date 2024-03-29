from django.urls import path
from django.contrib.auth.views import LoginView, logout_then_login

from global_login_required import login_not_required as lnr

from .views import PassKeyReset, signup, account_edit, profile_edit, profile_view

app_name = "account"
urlpatterns = [
    path("signup/", lnr(signup), name="signup"),
    path(
        "signin/",
        lnr(LoginView.as_view(template_name="account/authentication/signin.html")),
        name="signin",
    ),
    path("signout/", logout_then_login, name="signout"),
    path("profile/view/<int:pk>", profile_view, name="profile_view"),
    path("profile/edit", profile_edit, name="profile_edit"),
    path("account/edit", account_edit, name="account_edit"),
    path("passkey/reset", PassKeyReset.as_view(), name="passkey_reset"),
]
