from rest_framework import serializers

from core.utils import validators


error = validators.init_error(serializers.ValidationError)

validate_file_format_bills = validators.validator_file_format_field('bills', error)
validate_file_format_client_org = validators.validator_file_format_field('client_org', error)
validate_bills = validators.validate_bills(error)
validate_client_org = validators.validate_client_org(error)
