from django.conf import urls
from django.contrib import admin
from account.views import AuthView, ProfileView
from link.views import LinkView
from common.views import ErrorView


url = urls.url
include = urls.include

urlpatterns = [
    url(r'^$', AuthView.home_redirect, name='index'),
    url(r'^home/$', LinkView.wall, name='home'),
    url(r'^account/', include('account.urls')),
    url(r'^link/', include('link.urls')),
    url(r'^notification/', include('notification.urls')),
    url(r'^search/', include('search.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^(?P<username>\w+)/$', ProfileView.posts, name='profile'),
    url(r'^(?P<username>\w+)/following/$', ProfileView.following, name='following'),
    url(r'^(?P<username>\w+)/followers/$', ProfileView.followers, name='followers'),
    url(r'^(?P<username>\w+)/links/$', LinkView.links, name='links'),
]

urls.handler400 = ErrorView.not_authorized
urls.handler403 = ErrorView.permission_denied
urls.handler404 = ErrorView.page_not_found
urls.handler500 = ErrorView.server_error
