from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.decorators import api_view
from django.db.models import Q

from clients.utils import update
from clients.models import Client, Organization, Bill
from api.serializers import (
    UploadFilesSerializer,
    ClientModelSerializer,
    OrganizationModelSerializer,
    BillModelSerializer
)


def index(request):
    return render(request, 'api_index.html')


@api_view(['POST'])
def upload_files(request):
    serializer = UploadFilesSerializer(request.POST, request.FILES)
    serializer.is_valid(raise_exception=True)
    bills = request.FILES.get('bills')
    client_org = request.FILES.get('client_org')
    result = update(client_org.file if client_org else None, bills.file if bills else None)
    return Response(result, status=HTTP_200_OK)


class ClientViewSet(viewsets.ModelViewSet):

    serializer_class = ClientModelSerializer
    queryset = Client.objects.all()


class OrganizationViewSet(viewsets.ModelViewSet):

    serializer_class = OrganizationModelSerializer

    def get_queryset(self):
        queryset = Organization.objects.all().prefetch_related('client')
        if 'search' in self.request.query_params:
            search_name = self.request.query_params.get('search')
            queryset = queryset.filter(Q(name__icontains=search_name) | Q(client__name__icontains=search_name))
        return queryset


class BillViewSet(viewsets.ModelViewSet):

    serializer_class = BillModelSerializer

    def get_queryset(self):
        queryset = Bill.objects.all().prefetch_related('organization')
        if 'search' in self.request.query_params:
            search_name = self.request.query_params.get('search')
            queryset = queryset.filter(
                Q(organization__name__icontains=search_name) |
                Q(organization__client__name__icontains=search_name)
            )
        return queryset

