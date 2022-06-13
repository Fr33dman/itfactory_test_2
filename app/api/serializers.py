from rest_framework import serializers
from django.db.models import Sum

from api import validators
from clients.models import Client, Organization, Bill


class UploadFilesSerializer(serializers.Serializer):
    bills = serializers.FileField(required=False, validators=[
        validators.validate_file_format_bills,
        validators.validate_bills,
    ])
    client_org = serializers.FileField(required=False, validators=[
        validators.validate_file_format_client_org,
        validators.validate_client_org,
    ])

    def validate(self, attrs):
        validated_data = super(UploadFilesSerializer, self).validate(attrs)
        bills = validated_data.get('bills')
        client_org = validated_data.get('client_org')

        if bills is None and client_org is None:
            raise serializers.ValidationError(
                [
                    {
                        'bills': ['Вы не прикрепили файлы'],
                    },
                    {
                        'client_org': ['Вы не прикрепили файлы'],
                    }
                ]
            )

        return validated_data


class ClientModelSerializer(serializers.ModelSerializer):
    bills_sum = serializers.SerializerMethodField()
    organizations_count = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ('id', 'name', 'bills_sum', 'organizations_count')

    def get_bills_sum(self, obj):
        bills_sum = Bill.objects.filter(organization__client=obj).aggregate(Sum('sum')).get('sum__sum')
        return bills_sum if bills_sum is not None else 0

    def get_organizations_count(self, obj):
        organizations_count = Organization.objects.filter(client=obj).count()
        return organizations_count


class OrganizationModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = '__all__'

    def to_representation(self, instance):
        result = super(OrganizationModelSerializer, self).to_representation(instance)
        result['client'] = instance.client.name
        return result


class BillModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bill
        fields = '__all__'

    def to_representation(self, instance):
        result = super(BillModelSerializer, self).to_representation(instance)
        result['organization'] = instance.organization.name
        return result
