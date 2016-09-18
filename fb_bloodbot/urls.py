from django.conf.urls import include, url
from .views import BloodbotView
urlpatterns = [
	url(r'^83128f578c0815ef8efeeedd9f2c1edef33d5c4efa6c22df18/?$', BloodbotView.as_view())
]