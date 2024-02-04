# # main_api/views.py
import re
from django.http import JsonResponse
from django.db import models
from django.apps import apps
from django.contrib.auth.models import AbstractUser
from rest_framework.decorators import api_view
from .models import Document
from . import ocr_functions
from authentication.models import CustomUser
from django.db import connection
import json
import re
import json
import logging
from django.http import JsonResponse
from django.db import models, connection
from rest_framework.decorators import api_view
from .models import Document
from . import ocr_functions
from authentication.models import CustomUser
from django.apps import apps
from datetime import datetime
# Add this import at the top of your views.py file
import pandas as pd


@api_view(['POST'])
def upload_and_extract_image(request):
    if request.method == 'POST' and request.FILES.get('file') and request.data.get('name'):
        uploaded_file = request.FILES['file']
        user = request.user  # Assuming the user is authenticated

        if user.is_authenticated:
            try:
                user_instance = CustomUser.objects.get(username=user.username)
            except CustomUser.DoesNotExist:
                user_instance = CustomUser.objects.create(username=user.username)

            name = request.data['name']  # Extracting the name from the request data

            # Extract file type from file name extension
            file_type = uploaded_file.name.split('.')[-1].lower() if '.' in uploaded_file.name else None

            # Read image data from the uploaded file
            image_data = uploaded_file.read()

            # Perform extraction
            extracted_data = None
            if uploaded_file.content_type.startswith('image'):
                extracted_data = ocr_functions.ocr_image(image_data)

            if not extracted_data or 'columns' not in extracted_data or not isinstance(extracted_data['columns'], list):
                print("Debug: Invalid format for extracted data")
                print(f"Debug: extracted_data: {extracted_data}")
                return JsonResponse({'error': 'Invalid format for extracted data'}, status=400)

            # Create a new Document instance
            document_instance = Document.objects.create(user=user_instance, file=uploaded_file, name=name, extracted_data=json.dumps(extracted_data), upload_date=datetime.now(), file_type=file_type)

            # Dynamically create a new model for the uploaded file
            model_name = re.sub(r'\W', '_', f"Document_{document_instance.id}_{uploaded_file.name}")
            document_instance.dynamic_collection_name = model_name  # Set the dynamically created collection name
            document_instance.save()
            model_fields = {field_name: models.CharField(max_length=255) for field_name in extracted_data['columns']}

            # Check if the model already exists
            if not apps.all_models['main_api'].get(model_name):
                new_model = type(model_name, (models.Model,), {'__module__': 'main_api.models', **model_fields})
                apps.all_models['main_api'][model_name] = new_model

                # Create a new collection in MongoDB for the dynamically created model
                with connection.schema_editor() as schema_editor:
                    schema_editor.create_model(new_model)

            # Create an instance of the dynamically created model and save the data
            new_model_instance = apps.get_model('main_api', model_name)()

            # Loop through all rows and save each row as a separate instance in the dynamically created model
            for row in extracted_data['data']:
                if isinstance(row, dict):
                    new_model_instance = apps.get_model('main_api', model_name)(**row)
                    new_model_instance.save()

            return JsonResponse({'document_id': document_instance.id, 'extracted_data': extracted_data}, status=200)

        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

    return JsonResponse({'error': 'Please provide a file'}, status=400)


# Configure logging
logging.basicConfig(level=logging.ERROR)

@api_view(['POST'])
def upload_and_extract_data(request):
    if request.method == 'POST' and request.FILES.get('file') and request.data.get('name'):
        uploaded_file = request.FILES['file']
        user = request.user  # Assuming the user is authenticated

        if user.is_authenticated:
            try:
                user_instance = CustomUser.objects.get(username=user.username)
            except CustomUser.DoesNotExist:
                user_instance = CustomUser.objects.create(username=user.username)

            name = request.data['name']  # Extracting the name from the request data

            # Extract file type from file name extension
            file_type = uploaded_file.name.split('.')[-1].lower() if '.' in uploaded_file.name else None

            # Perform extraction
            extracted_data = None
            if uploaded_file.content_type == 'application/pdf':
                extracted_data = ocr_functions.read_pdf_with_ocr(uploaded_file)
            elif uploaded_file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                extracted_data = ocr_functions.read_word(uploaded_file)
            elif uploaded_file.content_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']:
                extracted_data = ocr_functions.read_excel(uploaded_file)

            # Convert the extracted_data to a JSON-friendly format (if it's a DataFrame)
            if isinstance(extracted_data, pd.DataFrame):
                extracted_data = extracted_data.to_json(orient='records')

            # Convert JSON string to list of dictionaries (if needed)
            if isinstance(extracted_data, str):
                extracted_data = json.loads(extracted_data)

            # Use the first dictionary in the list to get column names
            if extracted_data and isinstance(extracted_data, list) and extracted_data[0]:
                model_fields = {field_name: models.CharField(max_length=255) for field_name in extracted_data[0].keys()}

                 # Create a new Document instance
                document_instance = Document.objects.create(user=user_instance, file=uploaded_file, name=name, extracted_data=json.dumps(extracted_data), upload_date=datetime.now(), file_type=file_type)

                # Dynamically create a new model for the uploaded file
                model_name = re.sub(r'\W', '_', f"Document_{document_instance.id}_{uploaded_file.name}")
                document_instance.dynamic_collection_name = model_name  # Set the dynamically created collection name
                document_instance.save()
                if not apps.all_models['main_api'].get(model_name):
                    new_model = type(model_name, (models.Model,), {'__module__': 'main_api.models', **model_fields})
                    apps.all_models['main_api'][model_name] = new_model

                    # Create a new collection in MongoDB for the dynamically created model
                    with connection.schema_editor() as schema_editor:
                        schema_editor.create_model(new_model)

                # Create an instance of the dynamically created model and save the data
                new_model_instance = apps.get_model('main_api', model_name)()

                # Loop through all rows and save each row as a separate instance in the dynamically created model
                for row in extracted_data:
                    if isinstance(row, dict):
                        try:
                            new_model_instance = apps.get_model('main_api', model_name)(**row)
                            new_model_instance.save()
                        except Exception as e:
                            # Log the error message to Django's logging system
                            logging.error(f"Error saving row to model: {e}, Row: {row}, Model Name: {model_name}")

               
                return JsonResponse({'document_id': document_instance.id, 'extracted_data': extracted_data}, status=200)
            else:
                return JsonResponse({'error': 'No data extracted or invalid data format'}, status=400)
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
    return JsonResponse({'error': 'Please provide a file'}, status=400)





# import json
# from django.http import JsonResponse
# from django.contrib.auth.models import AbstractUser
# from rest_framework.decorators import api_view
# from .models import Document
# from . import ocr_functions
# from authentication.models import CustomUser
# from pymongo import MongoClient
# from bson import ObjectId

# def serialize_document_instance(document_instance):
#     # Convert Document instance to dictionary excluding non-serializable fields
#     serialized_data = {
#         'id': str(document_instance.id),
#         'user': str(document_instance.user.id),
#         'file': str(document_instance.file),
#         'extracted_data': json.loads(document_instance.extracted_data),
        
#     }
#     return serialized_data


# @api_view(['POST'])
# def upload_and_extract_data(request):
#     if request.method == 'POST' and request.FILES.get('file'):
#         uploaded_file = request.FILES['file']
#         user = request.user  # Assuming the user is authenticated

#         if user.is_authenticated:
#             try:
#                 user_instance = CustomUser.objects.get(username=user.username)
#             except CustomUser.DoesNotExist:
#                 user_instance = CustomUser.objects.create(username=user.username)

#             # Perform extraction
#             extracted_data = None
#             if uploaded_file.content_type.startswith('image'): 
#                 extracted_data = ocr_functions.ocr_image(uploaded_file)
#             elif uploaded_file.content_type == 'application/pdf':
#                 extracted_data = ocr_functions.read_pdf_with_ocr(uploaded_file)
#             elif uploaded_file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
#                 extracted_data = ocr_functions.read_word(uploaded_file)
#             elif uploaded_file.content_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']:
#                 extracted_data = ocr_functions.read_excel(uploaded_file)

#             # Create a new Document instance
#             document_instance = Document.objects.create(user=user_instance, file=uploaded_file, extracted_data=json.dumps(extracted_data))
            
#             # Serialize Document instance
#             serialized_document = serialize_document_instance(document_instance)

#             # Define the collection name based on the document ID
#             collection_name = f"Document_{serialized_document['id']}"

#             # Connect to MongoDB
#             mongo_client = MongoClient("mongodb+srv://hassankhatri216:QGR5qVUUfdBFe5O1@cluster0.ug7zvx7.mongodb.net/DEA?retryWrites=true&w=majority")
#             db = mongo_client["DEA_API"]
#             collection = db[collection_name]

#             # Insert data into MongoDB
#             collection.insert_many(extracted_data['data'])

#             return JsonResponse({'document_id': serialized_document, 'extracted_data': extracted_data}, status=200)
        
#         else:
#             return JsonResponse({'error': 'User not authenticated'}, status=401)
        
#     return JsonResponse({'error': 'Please provide a file'}, status=400)





# import re
# from django.http import JsonResponse
# from rest_framework.decorators import api_view
# from .models import Document
# from . import ocr_functions
# from django.db import connection
# from django.apps import apps
# from django.db import models

# @api_view(['POST'])
# def upload_and_extract_excel(request):
#     return upload_and_extract(request, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel')

# @api_view(['POST'])
# def upload_and_extract_pdf(request):
#     return upload_and_extract(request, 'application/pdf')

# @api_view(['POST'])
# def upload_and_extract_word(request):
#     return upload_and_extract(request, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')

# @api_view(['POST'])
# def upload_and_extract_image(request):
#     return upload_and_extract(request, 'image')

# def upload_and_extract(request, allowed_content_types):
#     if request.method == 'POST' and request.FILES.get('file'):
#         uploaded_file = request.FILES['file']

#         # Check if the content type is allowed
#         if not uploaded_file.content_type.startswith(allowed_content_types):
#             return JsonResponse({'error': 'Unsupported file format'}, status=400)

#         # Perform extraction
#         extracted_data = None
#         if uploaded_file.content_type.startswith('image'):
#             extracted_data = ocr_functions.ocr_image(uploaded_file)
#         elif uploaded_file.content_type == 'application/pdf':
#             extracted_data = ocr_functions.read_pdf_with_ocr(uploaded_file)
#         elif uploaded_file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
#             extracted_data = ocr_functions.read_word(uploaded_file)
#         elif uploaded_file.content_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']:
#             extracted_data = ocr_functions.read_excel(uploaded_file)

#         # Create a new Document instance
#         document_instance = Document.objects.create(file=uploaded_file, extracted_data=extracted_data)

#         # Dynamically create a new model for the uploaded file
#         model_name = re.sub(r'\W', '_', f"Document_{document_instance.id}")
#         model_fields = {field_name: models.CharField(max_length=255) for field_name in extracted_data['columns']}

#         # Check if the model already exists
#         if not apps.all_models['main_api'].get(model_name):
#             new_model = type(model_name, (models.Model,), {'__module__': 'main_api.models', **model_fields})
#             apps.all_models['main_api'][model_name] = new_model

#             # Create a new collection in MongoDB for the dynamically created model
#             with connection.schema_editor() as schema_editor:
#                 schema_editor.create_model(new_model)

#         # Create instances of the dynamically created model and save the data
#         for row in extracted_data['data']:
#             new_model_instance = apps.get_model('main_api', model_name)(**row)
#             new_model_instance.save()

#         return JsonResponse({'document_id': document_instance.id, 'extracted_data': extracted_data}, status=200)

#     return JsonResponse({'error': 'Please provide a file'}, status=400)




# import re
# import time
# from django.http import JsonResponse
# from rest_framework.decorators import api_view
# from .models import Document
# from django.apps import apps
# from django.db import connection, models
# from . import ocr_functions

# def create_dynamic_model(extracted_data):
#     # Use the file name and a unique identifier for the model name
#     file_name = re.sub(r'\W', '_', extracted_data.get('file_name', 'Unknown'))
#     timestamp = str(int(time.time()))

#     model_name = f"Document_{file_name}_{timestamp}"
#     model_fields = {field_name: models.CharField(max_length=255) for field_name in extracted_data['columns']}

#     # Check if the model already exists
#     if not apps.all_models['main_api'].get(model_name):
#         new_model = type(model_name, (models.Model,), {'__module__': 'main_api.models', **model_fields})
#         apps.all_models['main_api'][model_name] = new_model

#         # Create a new collection in MongoDB for the dynamically created model
#         with connection.schema_editor() as schema_editor:
#             schema_editor.create_model(new_model)

#     return model_name

# def save_data_to_collection(model_name, extracted_data):
#     # Create an instance of the dynamically created model and save the data
#     for row in extracted_data['data']:
#         new_model_instance = apps.get_model('main_api', model_name)(**dict(zip(extracted_data['columns'], row)))
#         new_model_instance.save()

# @api_view(['POST'])
# def upload_and_extract_excel(request):
#     return upload_and_extract(request, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel')

# @api_view(['POST'])
# def upload_and_extract_pdf(request):
#     return upload_and_extract(request, 'application/pdf')

# @api_view(['POST'])
# def upload_and_extract_word(request):
#     return upload_and_extract(request, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')

# @api_view(['POST'])
# def upload_and_extract_image(request):
#     return upload_and_extract(request, 'image')

# def upload_and_extract(request, *allowed_content_types):
#     if request.method == 'POST' and request.FILES.get('file'):
#         uploaded_file = request.FILES['file']

#         # Check if the content type is allowed
#         if not any(uploaded_file.content_type.startswith(content_type) for content_type in allowed_content_types):
#             return JsonResponse({'error': 'Unsupported file format'}, status=400)

#         # Perform extraction
#         extracted_data = None
#         if uploaded_file.content_type.startswith('image'):
#             extracted_data = ocr_functions.ocr_image(uploaded_file)
#         elif uploaded_file.content_type == 'application/pdf':
#             extracted_data = ocr_functions.read_pdf_with_ocr(uploaded_file)
#         elif uploaded_file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
#             extracted_data = ocr_functions.read_word(uploaded_file)
#         elif uploaded_file.content_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']:
#             extracted_data = ocr_functions.read_excel(uploaded_file)

#         # Add the file name to the extracted_data dictionary
#         extracted_data['file_name'] = uploaded_file.name

#         # Create a new Document instance
#         document_instance = Document.objects.create(file=uploaded_file, extracted_data=extracted_data)

#         # Dynamically create a new model for the uploaded file
#         model_name = create_dynamic_model(extracted_data)

#         # Save the extracted data to the dynamically created collection
#         save_data_to_collection(model_name, extracted_data)

#         return JsonResponse({'document_id': document_instance.id, 'extracted_data': extracted_data}, status=200)

#     return JsonResponse({'error': 'Please provide a file'}, status=400)






# from django.db import connection
# from django.db.utils import IntegrityError
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# from .models import Document
# from rest_framework.decorators import api_view
# from . import ocr_functions
# import re

# @api_view(['POST'])
# def upload_and_extract_data(request):
#     if request.method == 'POST' and request.FILES.get('file'):
#         uploaded_file = request.FILES['file']

#         # Perform extraction
#         extracted_data = None
#         if uploaded_file.content_type.startswith('image'):
#             extracted_data = ocr_functions.ocr_image(uploaded_file)
#         elif uploaded_file.content_type == 'application/pdf':
#             extracted_data = ocr_functions.read_pdf_with_ocr(uploaded_file)
#         elif uploaded_file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
#             extracted_data = ocr_functions.read_word(uploaded_file)
#         elif uploaded_file.content_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']:
#             extracted_data = ocr_functions.read_excel(uploaded_file)

#         # Get the modified file name to use as the collection name
#         collection_name = re.sub(r'\W+', '_', uploaded_file.name.lower())

#         # Create a new Document instance and store the extracted data
#         document_instance = Document.objects.create(file=uploaded_file, extracted_data=extracted_data, collection_name=collection_name)

#         return JsonResponse({'document_id': document_instance.id, 'collection_name': collection_name, 'extracted_data': extracted_data}, status=200)

#     return JsonResponse({'error': 'Please provide a file'}, status=400)
