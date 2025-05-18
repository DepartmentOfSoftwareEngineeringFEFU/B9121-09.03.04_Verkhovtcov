from bootstrap_datepicker_plus import DatePickerInput
from CogEditor.models import Application
from django import forms


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = '__all__'
        widgets = {
            'audio_training_date': DatePickerInput(
                options={
                    "format": "DD.MM.YYYY",
                    "locale": "ru",
                }
            ),
        }
