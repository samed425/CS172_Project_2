from django.urls import path
from . import views
urlpatterns = [
    path('', views.mainPageRender, name='form-submit'),
]

