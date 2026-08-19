from django.contrib import admin
from django.apps import apps


class RawFieldNameModelAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name, field in form.base_fields.items():
            field.label = field_name
        return form


app_models = apps.get_app_config('competency').get_models()

for model in app_models:
    try:
        admin.site.register(model, RawFieldNameModelAdmin)
    except admin.sites.AlreadyRegistered:
        pass