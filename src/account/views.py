import os

from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required

from account.forms import SignUpForm, LoginForm, SettingsForm
from account.models import Account, Relationship
from notification.models import Notification, NotificationType


class AuthView:
    @staticmethod
    def signup(request):
        form = None
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                form_user = form.save(commit=False)
                user = User.objects.create_user(username=form_user.username, email=form_user.email,
                                                password=form_user.password,)
                user.first_name = form_user.first_name
                user.last_name = form_user.last_name
                user.save()
                account = Account(user=user)
                account.save()
        return render(request, 'index.html', {'formSignUp': form})

    @staticmethod
    def login(request):
        form = None
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                data = form.data
                if '@' in data['identity']:
                    kwargs = {'email': data['identity'].lower()}
                else:
                    kwargs = {'username': data['identity'].lower()}
                try:
                    user = User.objects.get(**kwargs)
                    if user is not None and user.check_password(data['password']):
                        login(request, user)
                        if 'keep_connected' in data:
                            request.session.set_expiry(0)
                        next_page = request.GET.get('next', None)
                        redirect_path = reverse('home')
                        if next_page is not None and next_page != '':
                            redirect_path = next_page
                        user_account = Account.get_by_user(user=user)
                        request.session['user_avatar'] = user_account.user_avatar
                        request.session.save()
                        return redirect(redirect_path)
                except User.DoesNotExist:
                    pass
        return render(request, 'index.html', {'form': form})

    @staticmethod
    def home_redirect(request):
        if request.user.is_authenticated:
            return redirect(reverse('home'))
        else:
            return render(request, 'index.html')

    @staticmethod
    @login_required
    def logout_redirect(request):
        logout(request)
        return redirect(reverse('index'))


class ProfileView:
    @staticmethod
    def following(request, username):
        notify_count = None
        profile = get_object_or_404(User, username=username)
        accounts = Account.objects.filter(followers__owner__user__username=username)
        profile_account = Account.get_by_user(user=profile)
        profile.user_avatar = profile_account.user_avatar
        if request.user.is_authenticated:
            session_account = Account.get_by_user(request.user)
            request.user.is_following = session_account.is_following(profile_account)
            notify_count = Notification.objects.filter(owner=session_account, viewed=False).count()
        return render(request, 'account/user.html', {'profile': profile, 'accounts': accounts,
                                                     'following': True,
                                                     'notify_count': notify_count})

    @staticmethod
    def followers(request, username):
        notify_count = None
        profile = get_object_or_404(User, username=username)
        accounts = Account.objects.filter(following__follow__user__username=username)
        profile_account = Account.get_by_user(user=profile)
        profile.user_avatar = profile_account.user_avatar
        if request.user.is_authenticated:
            session_account = Account.get_by_user(request.user)
            request.user.is_following = session_account.is_following(profile_account)
            notify_count = Notification.objects.filter(owner=session_account, viewed=False).count()
        return render(request, 'account/user.html', {'profile': profile, 'accounts': accounts,
                                                     'followers': True,
                                                     'notify_count': notify_count})

    @staticmethod
    @login_required
    def follow(request, username):
        if request.method == 'POST':
            relationship = Relationship()
            relationship.owner = Account.get_by_user(request.user)
            relationship.follow = Account.get_by_username(username)
            if not relationship.owner.is_following(relationship.follow):
                relationship.save()
                Notification.add(relationship.follow, relationship.owner, NotificationType.FOLLOW)
            return redirect('profile', username)

    @staticmethod
    @login_required
    def unfollow(request, username):
        if request.method == 'POST':
            owner = Account.get_by_user(request.user)
            follow = Account.get_by_username(username)
            owner.unfollow(follow)
            return redirect('profile', username)


class SettingsView:
    @staticmethod
    @login_required
    def settings(request):
        user = request.user
        form = None
        if request.method == 'POST':
            form = SettingsForm(request.POST)
            if form.is_valid():
                data = form.data
                user.first_name = data['first_name']
                user.last_name = data['last_name']
                if data['password']:
                    user.set_password(data['password'])
                user.save()
        notify_count = Notification.objects.filter(owner__user=user, viewed=False).count()
        return render(request, 'account/settings.html', {'settings': user, 'form': form,
                                                         'notify_count': notify_count})

    @staticmethod
    @login_required
    def upload_avatar(request):
        user = request.user
        user_avatar = request.FILES.get('user_avatar', None)
        if request.method == 'POST' and user_avatar:
            ext = os.path.splitext(user_avatar.name)[1]
            if ext.lower() in ['.jpg', '.jpeg', '.png']:
                filename = user.username + '.jpg'
                fs = FileSystemStorage()
                if fs.exists(filename):
                    fs.delete(filename)
                fs.save(filename, user_avatar)
                user_account = Account.get_by_user(user=user)
                request.session['user_avatar'] = user_account.user_avatar
                request.session.save()
        return redirect('account_settings')
