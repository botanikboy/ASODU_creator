from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.views.generic import CreateView, UpdateView
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from panels.models import Project
from panels.constants import OBJECTS_COUNT_ON_PAGE

User = get_user_model()


class SignUp(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('panels:index')
    template_name = 'users/signup.html'


class UserChangeView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'users/profile_form.html'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(User, pk=kwargs['pk'])
        if instance != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'users:profile', kwargs={'username': self.request.user.username})


def user_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    projects = Project.objects.filter(author=user)
    paginator = Paginator(projects, OBJECTS_COUNT_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'user': user,
        'page_obj': page_obj,
    }
    return render(request, 'users/profile.html', context)
