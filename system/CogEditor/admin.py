from CogEditor.models import (AgreedStatus, Application, Employee,
                              EmployeePosition, ParticipatoryRole,
                              StructuralUnit)
from django.contrib import admin

admin.site.register(Application)
admin.site.register(AgreedStatus)
admin.site.register(ParticipatoryRole)
admin.site.register(Employee)
admin.site.register(EmployeePosition)
admin.site.register(StructuralUnit)
