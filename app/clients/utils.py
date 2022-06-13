import io

from django.db.models import Q

from clients.models import Client, Organization, Bill
from core.utils.excel import read_file


def update_clients(rows) -> None:
    names = set(row[0] for row in rows)
    existing_clients = Client.objects.filter(Q(name__in=names)).values_list('name', flat=True)
    names = list(names - set(existing_clients))
    Client.objects.bulk_create(
        [Client(name=name) for name in names]
    )


def update_organizations(rows) -> None:
    client_names, organization_names = list(row[0] for row in rows), list(row[1] for row in rows)

    existing_organizations = Organization.objects.filter(
        Q(client__name__in=client_names) & Q(name__in=organization_names)
    ).values_list('name', 'client')
    clients = Client.objects.filter(name__in=client_names).values('id', 'name')
    clients = {cli.get('name'): cli.get('id') for cli in clients}

    new_organizations = list(filter(lambda x: (x[1], clients[x[0]]) not in existing_organizations, rows))

    Organization.objects.bulk_create(
        [Organization(name=org[1], client_id=clients[org[0]]) for org in new_organizations]
    )


def update_bills(rows) -> None:
    organization_names = set(row[0] for row in rows)

    organizations = Organization.objects.filter(name__in=organization_names).values('id', 'name')
    organizations = {org.get('name'): org.get('id') for org in organizations}

    bills = Bill.objects.filter(organization_id__in=organizations.values()).order_by('organization_id')
    bills_exist = bills.values_list('organization_id', flat=True)

    rows_orgs_exists = list(filter(lambda x: organizations.get(x[0]) is not None, rows))
    rows_orgs_name_2_id = list([organizations.get(x[0]), *x[1:]] for x in rows_orgs_exists)
    rows_sorted = sorted(rows_orgs_name_2_id, key=lambda x: x[0])

    rows_2_update = list(filter(lambda x: x[0] in bills_exist, rows_sorted))
    rows_2_create = list(filter(lambda x: x[0] not in bills_exist, rows_sorted))

    for i in range(bills.count()):
        bills[i].unique_id = rows_2_update[i][1]
        bills[i].sum = rows_2_update[i][2]
        bills[i].date = rows_2_update[i][3]

    Bill.objects.bulk_update(bills, ['unique_id', 'sum', 'date'])

    Bill.objects.bulk_create(
        [Bill(organization_id=row[0], unique_id=row[1], sum=row[2], date=row[3]) for row in rows_2_create]
    )


def update(clients_org: io.BytesIO | None, bills: io.BytesIO | None) -> list:
    result = []

    if clients_org is not None:

        data_clients_org = read_file(clients_org)

        update_clients(data_clients_org[0].get('rows'))
        update_organizations(data_clients_org[1].get('rows'))

        result += data_clients_org

    if bills is not None:

        data_bills = read_file(bills)
        update_bills(data_bills[0].get('rows'))

        result += data_bills

    return result
