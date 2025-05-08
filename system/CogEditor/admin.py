from django.contrib import admin

from CogEditor.models import (
    Application,
    AgreedStatus,
    ParticipatoryRole,
    Employee,
    EmployeePosition,
    StructuralUnit,
)

admin.site.register(Application)
admin.site.register(AgreedStatus)
admin.site.register(ParticipatoryRole)
admin.site.register(Employee)
admin.site.register(EmployeePosition)
admin.site.register(StructuralUnit)
