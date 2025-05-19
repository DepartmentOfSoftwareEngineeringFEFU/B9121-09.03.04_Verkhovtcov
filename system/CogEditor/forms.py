import datetime

from bootstrap_datepicker_plus.widgets import DatePickerInput
from CogEditor.models import (
    AgreedStatus,
    Application,
    Employee,
    EmployeePosition,
    Schedule,
    Sources,
)
from django import forms
from django.utils import timezone


class ApplicationForm(forms.ModelForm):
    e_title = forms.CharField(
        max_length=256,
        widget=forms.Textarea(attrs={'rows': 1}),
        label="Наименование мероприятия",
    )

    e_description = forms.CharField(
        max_length=2048,
        widget=forms.Textarea(attrs={'rows': 8}),
        label="Описание мероприятия",
    )

    organizer_employee_name = forms.CharField(
        max_length=64,
        label="ФИО ответственного за организацию",
        required=True,
    )

    now = timezone.now()
    local_now = timezone.localtime(now)
    base_time = local_now.replace(minute=0, second=0, microsecond=0)
    day_1 = base_time + datetime.timedelta(days=3, hours=1)
    day_2 = base_time + datetime.timedelta(days=3, hours=4)

    event_date = forms.DateField(
        label="Дата мероприятия",
        widget=forms.DateInput(
            attrs={
                'class': 'form-control form-control-sm',
                'type': 'date',
                'value': day_1.date().strftime("%Y-%m-%d"),
            }
        ),
        initial=day_1.date().strftime("%Y-%m-%d"),
    )
    event_date_end = forms.DateField(
        label="Дата окончания",
        widget=forms.DateInput(
            attrs={
                'class': 'form-control form-control-sm',
                'type': 'date',
            }
        ),
        required=False,
        initial=day_2.date().strftime("%Y-%m-%d"),
    )

    event_time_start = forms.TimeField(
        label="Время начала",
        widget=forms.TimeInput(
            attrs={
                'class': 'form-control form-control-sm',
                'type': 'time',
                'value': day_1.time(),
                'format': '%HH:%MM',
            }
        ),
        initial=day_1.time(),
    )

    event_time_end = forms.TimeField(
        label="Время окончания",
        widget=forms.TimeInput(
            attrs={
                'class': 'form-control form-control-sm',
                'type': 'time',
            }
        ),
        initial=day_2.time(),
        required=False,
    )

    event_all_day = forms.BooleanField(
        label="Весь день",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    # Поля для монтажа/демонтажа
    setup_date_start = forms.DateField(
        label="Дата начала монтажа",
        widget=forms.DateInput(
            attrs={'class': 'form-control form-control-sm', 'type': 'date'}
        ),
        required=False,
    )

    setup_date_end = forms.DateField(
        label="Дата окончания демонтажа",
        widget=forms.DateInput(
            attrs={'class': 'form-control form-control-sm', 'type': 'date'}
        ),
        required=False,
    )

    class Meta:
        model = Application
        exclude = [
            'application_source',
            'organizer_employee',
            'event_schedule',
            'installation_dismantling',
        ]
        widgets = {
            'subm_date': forms.HiddenInput(),  # Скрытое поле
            'status': forms.HiddenInput(),  # Скрытое поле
            'audio_training_date': DatePickerInput(
                options={
                    "format": "DD.MM.YYYY",
                    "locale": "ru",
                }
            ),
        }

    def __init__(
        self, *args, default_status=None, default_source=None, **kwargs
    ):
        super().__init__(*args, **kwargs)

        # Делаем поля необязательными для формы
        self.fields['subm_date'].required = False
        self.fields['status'].required = False

        if default_status is None:
            default_status, _ = AgreedStatus.objects.get_or_create(
                n_stage=4,
                defaults={
                    'status': 'Направлена на согласование администратору'
                },
            )

        if default_source is None:
            default_source, _ = Sources.objects.get_or_create(
                name="Сайт", defaults={'name': 'Сайт'}
            )

        self.initial.update(
            {
                'subm_date': timezone.now(),
                'status': default_status,
                'application_source': default_source,
            }
        )

        # Устанавливаем значения по умолчанию
        self.initial.update(
            {
                'subm_date': timezone.now(),
                'status': AgreedStatus.objects.get(n_stage=4),
                'application_source': Sources.objects.get(name="Сайт"),
            }
        )

    def clean(self):
        cleaned_data = super().clean()
        all_day = cleaned_data.get('event_all_day')

        if all_day:
            date_start = cleaned_data.get('event_date_start')
            date_end = cleaned_data.get('event_date_end')

            if not date_start or not date_end:
                raise forms.ValidationError(
                    "Для мероприятия на весь день необходимо указать"
                    " даты начала и окончания"
                )

            if date_start > date_end:
                raise forms.ValidationError(
                    "Дата начала не может быть позже даты окончания"
                )

            cleaned_data['event_start'] = datetime.datetime.combine(
                date_start, datetime.time.min
            )
            cleaned_data['event_end'] = datetime.datetime.combine(
                date_end, datetime.time.max
            )
        else:
            event_date = cleaned_data.get('event_date')

            time_start = cleaned_data.get('event_time_start')
            time_end = cleaned_data.get('event_time_end')

            if not event_date:
                raise forms.ValidationError(
                    "Необходимо указать дату мероприятия"
                )

            if time_start is None or time_end is None:
                raise forms.ValidationError(
                    "Необходимо указать время начала и окончания"
                )

            if time_start >= time_end:
                raise forms.ValidationError(
                    "Время начала не может быть позже времени окончания"
                )
            cleaned_data['event_start'] = datetime.datetime.combine(
                event_date, time_start
            )
            cleaned_data['event_end'] = datetime.datetime.combine(
                event_date, time_end
            )

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

        # Сначала сохраняем instance, чтобы получить id
        if commit:
            instance.save()
            self.save_m2m()  # Сохраняем ManyToMany, если они есть

        # Теперь можно работать с ManyToMany (event_schedule)
        schedule = Schedule.objects.create(
            start=self.cleaned_data['event_start'],
            end=self.cleaned_data['event_end'],
            all_day=self.cleaned_data['event_all_day'],
        )
        instance.event_schedule.add(schedule)  # Теперь instance имеет id

        # Обработка сотрудника
        full_name = self.cleaned_data['organizer_employee_name']
        employee, created = Employee.objects.get_or_create(
            full_name=full_name,
            defaults={
                'position': EmployeePosition.objects.get_or_create(
                    position='Не указана'
                )[0],
                'structural_unit': instance.organizer,
            },
        )
        instance.organizer_employee = employee

        if commit:
            instance.save()  # Сохраняем изменения

        print(f"Заявка сохранена! ID: {instance.id}")
        return instance
