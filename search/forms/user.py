from django import forms


class UserSearchForm(forms.Form):
    username = forms.CharField(required=False, label='Username')
