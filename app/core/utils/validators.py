import zipfile
from datetime import datetime

from django.forms import ValidationError

from core.utils.excel import read_file
from clients.models import Client, Organization, Bill


def init_error(cls):

    def error_func(code: str, field: str) -> cls:
        errors = {

            'file_format': cls(
                [
                    {
                        field: [f'Такой формат не поддерживается.'],
                    }
                ]
            ),

            'default': cls(
                [
                    {
                        'error': ['Что-то пошло не так.'],
                    }
                ]
            ),

            'sheets': cls(
                [
                    {
                        'error': ['Таблицы не совпадают с форматом.'],
                    }
                ]
            ),

            'columns': cls(
                [
                    {
                        field: ['Колонки таблиц не совпадают с форматом.'],
                    }
                ]
            ),

            'rows': cls(
                [
                    {
                        field: ['Строки таблиц не совпадают с форматом.'],
                    }
                ]
            ),

            'types': cls(
                [
                    {
                        field: ['Формат ячеек не валиден.'],
                    }
                ]
            ),

            'overlap': cls(
                [
                    {
                        field: ['В таблице имеются повторяющиеся строки либо не соблюдена уникальность полей.'],
                    }
                ]
            ),

            'unique_id': cls(
                [
                    {
                        field: ['В таблице не соблюдена уникальность поля number.']
                    }
                ]
            ),
        }

        return errors.get(code) or errors['default']

    return error_func


def validator_file_format_field(field: str, error):

    def validate_format_type(file) -> None:

        allowed_file_formats = ['xls', 'xlsx']

        if file is not None:
            file_format = file._name.split('.')[-1]

            if file_format not in allowed_file_formats:
                raise error('file_format', field)

    return validate_format_type


def validate_types(len_rows: int, field_types: dict):

    def validate(rows: list, error_field: str, error) -> None:

        for row in rows:

            if len(row) != len_rows:
                raise error('rows', error_field)

            for index, field_type in field_types.items():

                if not isinstance(row[index], field_type):
                    try:
                        field_type(row[index])
                    except TypeError:
                        raise error('types', error_field)

    return validate


def validate_client_unique(rows: list, error_field: str, error) -> None:

    client_names = set(row[0] for row in rows)
    if len(rows) != len(client_names):
        raise error('overlap', error_field)


def validate_organization_unique(rows: list, error_field: str, error) -> None:

    organization_names_and_clients = set(f'{row[0]}{row[1]}' for row in rows)
    if len(rows) != len(organization_names_and_clients):
        raise error('overlap', error_field)


def validate_bill_client_org(rows: list, error_field: str, error) -> None:

    organization_names = set(row[0] for row in rows)
    if len(rows) != len(organization_names):
        raise error('overlap', error_field)


def validate_bill_number(rows: list, error_field: str, error) -> None:

    numbers = set(row[1] for row in rows)
    if len(rows) != len(numbers):
        raise error('overlap', error_field)


def validate_bill_number_exists(rows: list, error_field: str, error) -> None:

    bills = Bill.objects.all().prefetch_related('organization').values_list('organization__name', 'unique_id')
    bills = {name: unique_id for name, unique_id in bills}
    new_bills = {row[0]: row[1] for row in rows}
    bills.update(new_bills)
    unique_ids = bills.values()
    if len(set(unique_ids)) != len(unique_ids):
        raise error('unique_id', error_field)


def validate_tables(
        tables: dict,
        titles: dict,
        error_field: str,
        validators: dict,
        error
) -> None:

    for name, table in tables.items():

        if table.get('titles') != titles.get(name):
            raise error('columns', error_field)

        rows = table.get('rows')

        for validator in validators.get(name):
            validator(rows, error_field, error)


def validate_bills(error):

    def validator_bills(file) -> None:

        field = 'bills'

        bills = 1

        titles = {
            bills: [
                'client_org',
                '№',
                'sum',
                'date',
            ],
        }

        field_types = {
            bills: {
                0: str,
                1: float,
                2: float,
                3: datetime,
            },
        }

        validators = {
            bills: [
                validate_types(len(titles[bills]), field_types[bills]),
                validate_bill_client_org,
                validate_bill_number,
                validate_bill_number_exists,
            ]
        }

        try:
            workbook = read_file(file.file)
        except zipfile.BadZipFile or OSError or IOError:
            raise error('file_format', field)

        if len(workbook) != 1:
            raise error('sheets', field)

        tables = {
            bills: workbook[0],
        }

        validate_tables(tables, titles, field, validators, error)

    return validator_bills


def validate_client_org(error):

    def validator_client_org(file) -> None:

        field = 'client_org'

        client = 1
        organization = 2

        titles = {
            client: [
                'name',
            ],
            organization: [
                'client_name',
                'name',
            ],
        }

        field_types = {
            client: {
                0: str,
            },
            organization: {
                0: str,
                1: str,
            }
        }

        validators = {
            client: [
                validate_types(len(titles[client]), field_types[client]),
                validate_client_unique,
            ],
            organization: [
                validate_types(len(titles[organization]), field_types[organization]),
                validate_organization_unique,
            ]
        }

        try:
            workbook = read_file(file.file)
        except zipfile.BadZipFile:
            raise error('file_format', field)

        if len(workbook) != 2:
            raise error('sheets', field)

        tables = {
            client: workbook[0],
            organization: workbook[1],
        }

        validate_tables(tables, titles, field, validators, error)

    return validator_client_org
