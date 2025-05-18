from bootstrap_datepicker_plus.widgets import DatePickerInput
from CogEditor.models import (AgreedStatus, Application, Employee,
                              EmployeePosition, Sources)
from django import forms
from django.utils import timezone


class ApplicationForm(forms.ModelForm):
    e_title = forms.CharField(
        max_length=256,
        widget=forms.Textarea(attrs={'rows': 2}),
        label="Наименование мероприятия*"
    )

    organizer_employee_name = forms.CharField(
        max_length=64,
        label="ФИО ответственного за организацию",
        required=True
    )

    class Meta:
        model = Application
        exclude = ['application_source', 'organizer_employee']
        widgets = {
            'subm_date': forms.HiddenInput(),  # Скрытое поле
            'status': forms.HiddenInput(),     # Скрытое поле
            'audio_training_date': DatePickerInput(
                options={
                    "format": "DD.MM.YYYY",
                    "locale": "ru",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Делаем поля необязательными для формы
        self.fields['subm_date'].required = False
        self.fields['status'].required = False

        # Устанавливаем значения по умолчанию
        self.initial.update({
            'subm_date': timezone.now(),
            'status': AgreedStatus.objects.get(n_stage=4),
            'application_source': Sources.objects.get(name="Сайт")
        })

    def clean(self):
        cleaned_data = super().clean()

        # Гарантируем установку обязательных полей
        if not cleaned_data.get('subm_date'):
            cleaned_data['subm_date'] = timezone.now()

        if not cleaned_data.get('status'):
            cleaned_data['status'] = AgreedStatus.objects.get(n_stage=5)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Устанавливаем обязательные поля, если они ещё не установлены
        if not instance.subm_date:
            instance.subm_date = timezone.now()

        if not instance.status_id:
            instance.status = AgreedStatus.objects.get(n_stage=5)

        if not instance.application_source_id:
            instance.application_source = Sources.objects.get(name="Сайт")

        # Обработка сотрудника
        full_name = self.cleaned_data['organizer_employee_name']
        employee, created = Employee.objects.get_or_create(
            full_name=full_name,
            defaults={
                'position': EmployeePosition.objects.get_or_create(position='Не указана')[0],
                'structural_unit': instance.organizer
            }
        )
        instance.organizer_employee = employee

        if commit:
            instance.save()
            self.save_m2m()
            print(f"Заявка сохранена! ID: {instance.id}")

        return instance
