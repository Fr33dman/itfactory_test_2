from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Q

from clients.utils import update
from clients.forms import UploadForm, FilterForm
from clients.models import Client, Bill, Organization


def index(request):
    return render(request, 'client_index.html')


class BillsView(generic.list.ListView):
    model = Bill
    template_name = 'bill_list.html'

    def get_queryset(self):
        queryset = Bill.objects.all()
        search_name = self.request.GET.get('search')
        if search_name is not None:
            queryset = queryset.filter(
                Q(organization__name__icontains=search_name) |
                Q(organization__client__name__icontains=search_name)
            )
        return queryset

    def render_to_response(self, context, **response_kwargs):
        context['filter_form'] = FilterForm()
        return super(BillsView, self).render_to_response(context, **response_kwargs)


class ClientView(generic.list.ListView):
    model = Client
    template_name = 'client_list.html'


class OrganizationView(generic.list.ListView):
    model = Organization
    template_name = 'organization_list.html'

    def get_queryset(self):
        queryset = Organization.objects.all()
        search_name = self.request.GET.get('search')
        if search_name is not None:
            queryset = queryset.filter(Q(name__icontains=search_name) | Q(client__name__icontains=search_name))
        return queryset

    def render_to_response(self, context, **response_kwargs):
        context['filter_form'] = FilterForm()
        return super(OrganizationView, self).render_to_response(context, **response_kwargs)


class ClientDetailViews(generic.detail.DetailView):
    model = Client
    template_name = 'client_detail.html'
    slug_field = 'name'

    def get_object(self, queryset=None):
        slug = self.kwargs.get(self.slug_url_kwarg, None)
        obj = get_object_or_404(Client, name=slug)
        return obj

    def get_context_data(self, **kwargs):
        context = super(ClientDetailViews, self).get_context_data(**kwargs)
        bills_sum = Bill.objects.filter(organization__client=self.object).aggregate(Sum('sum')).get('sum__sum')
        organizations_count = Organization.objects.filter(client=self.object).count()
        context['bills_sum'] = bills_sum if bills_sum is not None else 0
        context['organizations_count'] = organizations_count
        return context


def upload_files(request):
    errors = []
    success = False
    if request.method == 'POST':
        files = UploadForm(request.POST, request.FILES)
        if files.is_valid():
            bills = request.FILES.get('bills')
            client_org = request.FILES.get('client_org')
            update(client_org.file if client_org else None, bills.file if bills else None)
            success = True
        else:
            errors = files.errors

    form = UploadForm()
    return render(request, 'upload_files.html',
                  {'form': form, 'errors': errors, 'success': success})
    