from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Company, Contact, LicenseRecord, InfringementOverview
from .forms import CompanyForm, ContactForm, LicenseRecordForm, InfringementOverviewForm

# LoginRequiredMixin sẽ tự động đá người dùng ra trang login nếu chưa đăng nhập
class DashboardView(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'dashboard.html'
    context_object_name = 'companies'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_companies'] = Company.objects.count()
        return context


class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'company/list.html'
    context_object_name = 'companies'
    login_url = '/login/'
    paginate_by = 10  # 10 companies per page

    def get_queryset(self):
        queryset = Company.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(company_name__icontains=query) |
                Q(english_name__icontains=query) |
                Q(phone__icontains=query) |
                Q(industry__icontains=query) |
                Q(tax_code__icontains=query)
            )
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'company/detail.html'
    context_object_name = 'company'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['license_records'] = self.object.license_records.order_by('expiration_date', 'id')
        context['infringement_overviews'] = self.object.infringement_overviews.order_by('-created_at', '-id')
        return context


class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'company/form.html'
    success_url = reverse_lazy('company_list')
    login_url = '/login/'

    def form_valid(self, form):
        messages.success(self.request, f'Company "{form.instance.company_name}" has been created successfully!')
        return super().form_valid(form)


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'company/form.html'
    success_url = reverse_lazy('company_list')
    login_url = '/login/'

    def form_valid(self, form):
        messages.success(self.request, f'Company "{form.instance.company_name}" has been updated successfully!')
        return super().form_valid(form)


class CompanyDeleteView(LoginRequiredMixin, DeleteView):
    model = Company
    template_name = 'company/confirm_delete.html'
    success_url = reverse_lazy('company_list')
    login_url = '/login/'

    def delete(self, request, *args, **kwargs):
        company = self.get_object()
        messages.success(request, f'Company "{company.company_name}" has been deleted successfully!')
        return super().delete(request, *args, **kwargs)


class ContactCreateView(LoginRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'contact/form.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = Company.objects.get(pk=self.kwargs['company_pk'])
        return context

    def form_valid(self, form):
        form.instance.company = Company.objects.get(pk=self.kwargs['company_pk'])
        messages.success(self.request, f'Contact "{form.instance.contact_name}" has been added successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('company_detail', kwargs={'pk': self.kwargs['company_pk']})


class ContactDetailView(LoginRequiredMixin, DetailView):
    model = Contact
    template_name = 'contact/detail.html'
    context_object_name = 'contact'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.object.company
        return context


class ContactUpdateView(LoginRequiredMixin, UpdateView):
    model = Contact
    form_class = ContactForm
    template_name = 'contact/form.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.object.company
        return context

    def form_valid(self, form):
        messages.success(self.request, f'Contact "{form.instance.contact_name}" has been updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('company_detail', kwargs={'pk': self.object.company.pk})


class ContactDeleteView(LoginRequiredMixin, DeleteView):
    model = Contact
    template_name = 'contact/confirm_delete.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.object.company
        return context

    def delete(self, request, *args, **kwargs):
        contact = self.get_object()
        company = contact.company
        messages.success(request, f'Contact "{contact.contact_name}" has been deleted successfully!')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('company_detail', kwargs={'pk': self.object.company.pk})


class LicenseRecordCreateView(LoginRequiredMixin, CreateView):
    model = LicenseRecord
    form_class = LicenseRecordForm
    template_name = 'license_record/form.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = Company.objects.get(pk=self.kwargs['company_pk'])
        return context

    def form_valid(self, form):
        form.instance.company = Company.objects.get(pk=self.kwargs['company_pk'])
        messages.success(self.request, f'License record "{form.instance.product_name}" has been added successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('company_detail', kwargs={'pk': self.kwargs['company_pk']})


class LicenseRecordDetailView(LoginRequiredMixin, DetailView):
    model = LicenseRecord
    template_name = 'license_record/detail.html'
    context_object_name = 'license_record'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.object.company
        return context


class LicenseRecordUpdateView(LoginRequiredMixin, UpdateView):
    model = LicenseRecord
    form_class = LicenseRecordForm
    template_name = 'license_record/form.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.object.company
        return context

    def form_valid(self, form):
        messages.success(self.request, f'License record "{form.instance.product_name}" has been updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('company_detail', kwargs={'pk': self.object.company.pk})


class LicenseRecordDeleteView(LoginRequiredMixin, DeleteView):
    model = LicenseRecord
    template_name = 'license_record/confirm_delete.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.object.company
        return context

    def delete(self, request, *args, **kwargs):
        license_record = self.get_object()
        messages.success(request, f'License record "{license_record.product_name}" has been deleted successfully!')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('company_detail', kwargs={'pk': self.object.company.pk})


class InfringementOverviewCreateView(LoginRequiredMixin, CreateView):
    model = InfringementOverview
    form_class = InfringementOverviewForm
    template_name = 'infringement_overview/form.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = Company.objects.get(pk=self.kwargs['company_pk'])
        return context

    def form_valid(self, form):
        form.instance.company = Company.objects.get(pk=self.kwargs['company_pk'])
        messages.success(self.request, 'Infringement overview has been added successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('company_detail', kwargs={'pk': self.kwargs['company_pk']})


class InfringementOverviewDetailView(LoginRequiredMixin, DetailView):
    model = InfringementOverview
    template_name = 'infringement_overview/detail.html'
    context_object_name = 'infringement_overview'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.object.company
        return context


class InfringementOverviewUpdateView(LoginRequiredMixin, UpdateView):
    model = InfringementOverview
    form_class = InfringementOverviewForm
    template_name = 'infringement_overview/form.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.object.company
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Infringement overview has been updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('company_detail', kwargs={'pk': self.object.company.pk})


class InfringementOverviewDeleteView(LoginRequiredMixin, DeleteView):
    model = InfringementOverview
    template_name = 'infringement_overview/confirm_delete.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.object.company
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Infringement overview has been deleted successfully!')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('company_detail', kwargs={'pk': self.object.company.pk})
