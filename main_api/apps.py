import json
from django.apps import AppConfig
# from main_api.models import Document
from django.db import models
from json.decoder import JSONDecodeError  # Import JSONDecodeError
from .dynamic_models import create_dynamic_model
from django.contrib import admin
from django.apps import apps

 
class MainApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main_api'

    # def ready(self):
    #     from .admin import register_all_dynamic_models
    #     register_all_dynamic_models()

 
    # def ready(self):
    #     from .models import Document

    #     # Iterate over existing documents and register dynamic models
    #     for document in Document.objects.all():
    #         if document.dynamic_collection_name and document.extracted_data:
    #             try:
    #                 extracted_data = json.loads(document.extracted_data)

    #                 if isinstance(extracted_data, list) and extracted_data:
    #                     model_fields = extracted_data[0]
    #                     model_name = f"Document_{document.id}_{document.file.name}"
                        
    #                     # Check if the model already exists using apps.all_models
    #                     app_models = self.apps.all_models.get('main_api', {})
    #                     model_class = app_models.get(model_name)

    #                     if not model_class:
    #                         create_dynamic_model(model_name, {field_name: models.CharField(max_length=255) for field_name in model_fields})
    #                         print(f"Created dynamic model: {model_name}")
    #                     else:
    #                         print(f"Model {model_name} already exists. Skipping creation.")
    #                 else:
    #                     print(f"Invalid format for extracted data in document {document.id}")
    #             except JSONDecodeError as e:
    #                 print(f"Error decoding JSON in document {document.id}: {e}")