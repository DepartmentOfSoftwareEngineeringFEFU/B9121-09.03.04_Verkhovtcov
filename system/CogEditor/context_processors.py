from .models import StructuralUnit  # Или ваша модель организаторов


def organizers_processor(request):
    return {"organizers": StructuralUnit.objects.all().order_by("unit")}
