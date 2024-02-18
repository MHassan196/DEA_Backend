from django.contrib import admin
from django.apps import apps

# Register your models here.
from .models import Document

admin.site.register(Document)

# def register_all_dynamic_models():
#     app_models = apps.all_models.get('main_api', {})
#     for model_name, model_class in app_models.items():
#         if 'Document' in model_name and '_-0x' in model_name:
#             admin.site.register(model_class)

# # Call this function in your admin.py
# register_all_dynamic_models()
