import csv
import io

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Company, Contact, LicenseRecord, InfringementOverview, ImportedCSVFile, InfringementDetail
from .forms import CompanyForm, ContactForm, LicenseRecordForm, InfringementOverviewForm, CSVImportForm


def excel_col_to_index(column):
    value = 0
    for char in column.upper():
        value = value * 26 + (ord(char) - ord('A') + 1)
    return value - 1


CSV_COLUMN_MAPPING = {
    'product': excel_col_to_index('D'),
    'version': excel_col_to_index('E'),
    'release': excel_col_to_index('F'),
    'feature_used': excel_col_to_index('G'),
    'active_mac': excel_col_to_index('W'),
    'mac2': excel_col_to_index('X'),
    'mac3': excel_col_to_index('Y'),
    'mac4': excel_col_to_index('Z'),
    'system_model': excel_col_to_index('AA'),
    'wifi_latitude_longitude': excel_col_to_index('AC'),
    'ip_latitude_longitude': excel_col_to_index('AD'),
    'public_ip_address': excel_col_to_index('AH'),
    'gateway_mac_address': excel_col_to_index('AO'),
    'active_wifi_access_point': excel_col_to_index('AP'),
    'license_info': excel_col_to_index('AY'),
}

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
        context['infringement_detail'] = getattr(self.object, 'infringement_detail', None)
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


class CSVImportView(LoginRequiredMixin, FormView):
    template_name = 'import_csv/form.html'
    form_class = CSVImportForm
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        self.company = get_object_or_404(Company, pk=self.kwargs['company_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.company
        context['import_history'] = self.company.imported_csv_files.select_related('uploaded_by')[:10]
        return context

    def form_valid(self, form):
        uploaded_file = form.cleaned_data['csv_file']
        if not uploaded_file.name.lower().endswith('.csv'):
            form.add_error('csv_file', 'Chi ho tro file .csv')
            return self.form_invalid(form)

        imported_csv = ImportedCSVFile.objects.create(
            company=self.company,
            csv_file=uploaded_file,
            original_filename=uploaded_file.name,
            uploaded_by=self.request.user,
        )

        detail_defaults, unique_count = self._extract_unique_detail_data(imported_csv)

        InfringementDetail.objects.update_or_create(
            company=self.company,
            defaults={
                'imported_csv': imported_csv,
                **detail_defaults,
            },
        )

        # Xóa file vật lý của các lần import cũ, chỉ giữ metadata (tên + ngày)
        old_imports = ImportedCSVFile.objects.filter(company=self.company).exclude(pk=imported_csv.pk)
        for old in old_imports:
            if old.csv_file:
                old.csv_file.delete(save=False)
                old.csv_file = None
                old.save(update_fields=['csv_file'])

        messages.success(
            self.request,
            f'Import thanh cong. Da cap nhat Infringement Detail voi {unique_count} gia tri unique.',
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('company_detail', kwargs={'pk': self.company.pk})

    def _extract_unique_detail_data(self, imported_csv):
        imported_csv.csv_file.open('rb')
        try:
            file_bytes = imported_csv.csv_file.read()
        finally:
            imported_csv.csv_file.close()

        try:
            csv_text = file_bytes.decode('utf-8-sig')
        except UnicodeDecodeError:
            csv_text = file_bytes.decode('latin-1')

        reader = csv.reader(io.StringIO(csv_text))
        next(reader, None)  # Skip header row

        buckets = {
            'product': set(),
            'version': set(),
            'release': set(),
            'feature_used': set(),
            'active_mac': set(),
            'mac2': set(),
            'mac3': set(),
            'mac4': set(),
            'system_model': set(),
            'wifi_latitude_longitude': set(),
            'ip_latitude_longitude': set(),
            'public_ip_address': set(),
            'gateway_mac_address': set(),
            'active_wifi_access_point': set(),
            'license_info': set(),
        }
        feature_values = []
        feature_seen_keys = set()

        for row in reader:
            for field_name in [
                'product',
                'version',
                'release',
                'active_mac',
                'mac2',
                'mac3',
                'mac4',
                'system_model',
                'wifi_latitude_longitude',
                'ip_latitude_longitude',
                'public_ip_address',
                'gateway_mac_address',
                'active_wifi_access_point',
                'license_info',
            ]:
                index = CSV_COLUMN_MAPPING[field_name]
                value = row[index].strip() if index < len(row) else ''
                if value:
                    buckets[field_name].add(value)

            # feature_used: split by comma to collect individual unique features
            feature_idx = CSV_COLUMN_MAPPING['feature_used']
            feature_raw = row[feature_idx].strip() if feature_idx < len(row) else ''
            if feature_raw:
                for feat in feature_raw.split(','):
                    # CSV token format: feature:feature:number. Keep only feature name (before first ':').
                    feat = ' '.join(feat.strip().strip('"').split())
                    feature_name = feat.split(':', 1)[0].strip() if feat else ''
                    if feature_name:
                        feature_key = feature_name.lower()
                        if feature_key not in feature_seen_keys:
                            feature_seen_keys.add(feature_key)
                            feature_values.append(feature_name)

        detail_data = {
            'file': imported_csv.original_filename,
            'product': self._join_values(buckets['product']),
            'version': self._join_values(buckets['version']),
            'release': self._join_values(buckets['release']),
            'feature_used': '\n'.join(feature_values),
            'active_mac': self._join_values(buckets['active_mac']),
            'mac2': self._join_values(buckets['mac2']),
            'mac3': self._join_values(buckets['mac3']),
            'mac4': self._join_values(buckets['mac4']),
            'system_model': self._join_values(buckets['system_model']),
            'wifi_latitude_longitude': self._join_values(buckets['wifi_latitude_longitude']),
            'ip_latitude_longitude': self._join_values(buckets['ip_latitude_longitude']),
            'public_ip_address': self._join_values(buckets['public_ip_address']),
            'gateway_mac_address': self._join_values(buckets['gateway_mac_address']),
            'active_wifi_access_point': self._join_values(buckets['active_wifi_access_point']),
            'license_info': self._join_values(buckets['license_info']),
        }

        unique_count = sum(
            len(values)
            for field_name, values in buckets.items()
            if field_name != 'feature_used'
        ) + len(feature_values)
        return detail_data, unique_count

    @staticmethod
    def _join_values(values):
        if not values:
            return ''
        return '\n'.join(sorted(values))


class InfringementDetailDetailView(LoginRequiredMixin, DetailView):
    model = InfringementDetail
    template_name = 'infringement_detail/detail.html'
    context_object_name = 'infringement_detail'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.object.company
        context['field_counts'] = {
            'feature_used': self._count_items(self.object.feature_used),
            'active_mac': self._count_items(self.object.active_mac),
            'mac2': self._count_items(self.object.mac2),
            'mac3': self._count_items(self.object.mac3),
            'mac4': self._count_items(self.object.mac4),
            'system_model': self._count_items(self.object.system_model),
            'wifi_latitude_longitude': self._count_items(self.object.wifi_latitude_longitude),
            'ip_latitude_longitude': self._count_items(self.object.ip_latitude_longitude),
            'public_ip_address': self._count_items(self.object.public_ip_address),
            'gateway_mac_address': self._count_items(self.object.gateway_mac_address),
            'active_wifi_access_point': self._count_items(self.object.active_wifi_access_point),
            'license_info': self._count_items(self.object.license_info),
        }
        return context

    @staticmethod
    def _count_items(raw_value):
        if not raw_value:
            return 0

        # Stored values are newline-separated after import; split and dedupe defensively.
        values = {
            item.strip()
            for item in str(raw_value).splitlines()
            if item and item.strip()
        }
        return len(values)


class InfringementDetailDeleteView(LoginRequiredMixin, DeleteView):
    model = InfringementDetail
    template_name = 'infringement_detail/confirm_delete.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.object.company
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Infringement Detail has been deleted successfully!')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('company_detail', kwargs={'pk': self.object.company.pk})
