from django import forms

from clients import validators


class UploadForm(forms.Form):
    bills = forms.FileField(required=False,
                            validators=
                            [
                                validators.validate_file_format_bills,
                                validators.validate_bills,
                            ])
    client_org = forms.FileField(required=False,
                                 validators=
                                 [
                                     validators.validate_file_format_client_org,
                                     validators.validate_client_org,
                                 ])

    def clean(self):
        cleaned_data = super(UploadForm, self).clean()
        bills = cleaned_data.get('bills')
        client_org = cleaned_data.get('client_org')

        if bills is None and client_org is None:
            raise forms.ValidationError(
                [
                    {
                        'bills': ['Вы не прикрепили файлы'],
                    },
                    {
                        'client_org': ['Вы не прикрепили файлы'],
                    }
                ]
            )

        return cleaned_data


class FilterForm(forms.Form):
    search = forms.CharField(max_length=256)
