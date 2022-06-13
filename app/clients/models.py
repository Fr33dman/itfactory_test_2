from django.db import models


class Client(models.Model):
    name = models.CharField(verbose_name='Имя клиента', max_length=64, unique=True)


class Organization(models.Model):
    name = models.CharField(verbose_name='Название организации', max_length=64)
    client = models.ForeignKey(Client, verbose_name='Клиент', on_delete=models.CASCADE)


class Bill(models.Model):
    organization = models.OneToOneField(Organization, verbose_name='Организация', on_delete=models.CASCADE)
    unique_id = models.IntegerField(verbose_name='Уникальный номер', unique=True)
    _sum = models.IntegerField(verbose_name='Сумма', name='sum')
    date = models.DateTimeField(verbose_name='Дата')
