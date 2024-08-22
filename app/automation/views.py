from django.conf import settings

from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from django.utils import translation
from django.utils.translation import gettext as _

from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, DetailView, ListView, RedirectView

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages

from .testing import AppiumTestAutomation
from .models import APP, AVD
from .forms import RegisterForm, APPForm
from .xml_to_html import XMLToHTMLConverter


    
#################################### Manage Account ####################################

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('automation:login')

class PasswordChangeFormView(auth_views.PasswordChangeView):
    def get_success_url(self) :
        messages.success(self.request, _("Password's been changed successfully!"))
        return reverse_lazy('automation:login')

class PasswordResetFormView(auth_views.PasswordResetView):
    def get_success_url(self) :
        messages.success(self.request, _("We've emailed you instructions for setting your password. You should receive the email shortly!"))
        return reverse_lazy('automation:password_reset')

class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    def get_success_url(self):
        messages.success(self.request, _("Password's been changed successfully, try to login"))
        return reverse_lazy('automation:login') 

#################################### Main Views ####################################

class HomeView(TemplateView):
    template_name = 'automation/home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 

        context['greeting'] = _("Welcome to App Manager")
        return context

class UserAppsListView(LoginRequiredMixin, ListView):
    template_name = 'automation/apps_list.html'
    paginate_by = 14

    def get_queryset(self):
        apps = APP.objects.filter(uploaded_by=self.request.user).order_by('created_at')
        return apps
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class CreateAppView(LoginRequiredMixin, CreateView):
    model = APP
    form_class = APPForm
    template_name = 'automation/app_form.html'

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, _("The App saved successfully"))
        return reverse_lazy('automation:app_detail', kwargs={'slug': self.object.slug})

class DetailAppView(LoginRequiredMixin, DetailView):
    model = APP
    template_name = 'automation/app_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.uploaded_by != self.request.user:
            raise Http404(_("App not found."))
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app = self.get_object()
        if app.is_tested:
            converter = XMLToHTMLConverter(app.ui_hierarchy.path)
            html_content = converter.convert()
            context['hierarchy_content'] = html_content
        return context

class UpdateAppView(LoginRequiredMixin, UpdateView):
    model = APP
    form_class = APPForm
    template_name = 'automation/app_form.html'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.uploaded_by != self.request.user:
            raise Http404(_("App not found."))
        return obj
    
    def get_success_url(self):
        messages.success(self.request, _("The App saved successfully"))
        return reverse_lazy('automation:app_detail', kwargs={'slug': self.object.slug})

class DeleteAppView(LoginRequiredMixin, DeleteView):
    model = APP
    template_name = 'automation/app_delete.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.uploaded_by != self.request.user:
            raise Http404(_("App not found."))
        return obj
    
    def get_success_url(self):
        messages.success(self.request, _("The App saved successfully"))
        return reverse_lazy('automation:user_apps')

#################################### Test View ####################################

class TestAppsRedirectView(RedirectView):
    model = APP
    pattern_name = 'automation:app_detail'

    def get_redirect_url(self, *args, **kwargs):
        app = get_object_or_404(APP, slug=kwargs['slug'])

        # Retrieve the last AVD instance from the database
        avd = AVD.objects.order_by('-id').first()
        device = AppiumTestAutomation(avd)

        result = device.run_test(app) 
        if result['status'] == 'success':
            app.screen_changed = result['action_taken']
            app.is_tested = True
            app.save()
            messages.success(self.request,_("The app's been Tested successfully"))
        else:
            messages.error(self.request,_("Unfortunately an error happened, please try again.."))
            print(result['cause'])
        return super().get_redirect_url(*args, **kwargs)

#################################### Accessibility ####################################

def switch_language(request):
    language = request.GET.get('language', 'en')
    translation.activate(language)
    response = redirect(request.META.get('HTTP_REFERER'))
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
    return response
