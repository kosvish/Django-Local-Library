from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Введите дату между текущим днем и 4 неделями(по умолчанию 3)")

    def clean_renewal_date(self):
        data = self.cleaned_data["renewal_date"]
        # проверка того, что дата не в прошлом
        if data < datetime.datetime.today():
            raise ValidationError(_("Неправильная дата, возрат в прошлом"))

        if data > datetime.datetime.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_("Неправильная дата, дата не может превышать 4 недели"))

        return data



