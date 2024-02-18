from django.db import models
from django.db import connection
from django.apps import apps
import logging
from itertools import count

# model_counter = count() 


def create_dynamic_model(model_name, fields):
    # Convert fields to a string representation
    fields_str = str(fields)

    # Add a unique identifier to the model name using fields string
    unique_identifier = hex(hash(fields_str))  # You can use a different method to generate a unique identifier
    model_name_with_identifier = f"{model_name}_{unique_identifier}"

    # Check if the model already exists
    app_models = apps.all_models.get('main_api', {})
    existing_model_class = app_models.get(model_name_with_identifier)

    if not existing_model_class:
        new_model = type(model_name_with_identifier, (models.Model,), {'__module__': 'main_api.models', **fields})
        app_models[model_name_with_identifier] = new_model

        # Create a new collection in MongoDB for the dynamically created model
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(new_model)

        # Ensure the model is properly registered
        apps.all_models['main_api'][model_name_with_identifier] = new_model

        logging.debug(f"Created dynamic model: {model_name_with_identifier}, Table: {new_model._meta.db_table}")

    return model_name_with_identifier

  
# # Add this function to clear existing dynamic models
# def clear_existing_dynamic_models():
#     app_models = apps.all_models.get('main_api', {})  
#     for model_name in list(app_models.keys()):
#         if 'Document' in model_name and '_-0x' in model_name:
#             del app_models[model_name]

#             # Drop the MongoDB collection associated with the dynamic model
#             collection_name = app_models[model_name]._meta.db_table
#             utils.drop_collection(collection_name) 