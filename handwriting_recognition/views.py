# handwriting_recognition/views.py
from django.http import JsonResponse
from .models import ProcessedImage
from .recognition_model import process_image, process_images, ImageToWordModel, save_image_names_to_text_file
from authentication.models import CustomUser
from rest_framework.decorators import api_view
from datetime import datetime
from rest_framework import status
from rest_framework.response import Response
from mltu.configs import BaseModelConfigs
import json
import re

# @api_view(['POST'])
# def process_uploaded_image(request):
#     if request.method == 'POST' and request.FILES.get('file') and request.data.get('name'):
#         uploaded_file = request.FILES['file']
#         user = request.user  # Assuming the user is authenticated

#         if user.is_authenticated:
#             try:
#                 user_instance = CustomUser.objects.get(username=user.username)
#             except CustomUser.DoesNotExist:
#                 user_instance = CustomUser.objects.create(username=user.username)

#             name = request.data['name']  # Extracting the name from the request data

#             # Extract file type from file name extension
#             file_type = uploaded_file.name.split('.')[-1].lower() if '.' in uploaded_file.name else None

#             # Read image data from the uploaded file
#             image_data = uploaded_file.read()

#             # # Perform extraction using the recognition model
#             # extracted_text = process_images_from_bytes(image_data)

#             # # Check if the extraction is successful
#             # if not extracted_text:
#             #     return JsonResponse({'error': 'Failed to extract text from the image'}, status=400)

#              # Save image names to the text file
#             save_image_names_to_text_file(image_data)

#             # Perform image processing using the existing logic
#             configs = BaseModelConfigs.load("D:/Hassan/FYP/model/configs.yaml")
#             model_path = "D:/Hassan/FYP/model/model.onnx"
#             model = ImageToWordModel(model_path=model_path, char_list=configs.vocab)
#             formatted_output = process_images(image_data, model)

#             # Create a new ProcessedImage instance
#             processed_image = ProcessedImage.objects.create(
#                 user=user_instance,
#                 file=uploaded_file,
#                 processed_text=formatted_output,
#                 name=name,
#                 upload_date=datetime.now(),
#                 file_type=file_type,
#             )

#             return JsonResponse({'processed_image_id': processed_image.id, 'extracted_text': formatted_output}, status=200)

#         else:
#             return JsonResponse({'error': 'User not authenticated'}, status=401)

#     return JsonResponse({'error': 'Please provide a file'}, status=400)


# @api_view(['POST'])
# def process_uploaded_image(request):
#     if request.method == 'POST' and request.FILES.get('file') and request.data.get('name'):
#         uploaded_file = request.FILES['file']
#         user = request.user  # Assuming the user is authenticated

#         if user.is_authenticated:
#             try:
#                 user_instance = CustomUser.objects.get(username=user.username)
#             except CustomUser.DoesNotExist:
#                 user_instance = CustomUser.objects.create(username=user.username)

#             name = request.data['name']  # Extracting the name from the request data

#             file_type = uploaded_file.name.split('.')[-1].lower() if '.' in uploaded_file.name else None

#             # Read image data from the uploaded file
#             image_data = uploaded_file.read()

#             # Perform image processing using the existing logic
#             configs = BaseModelConfigs.load("D:/Hassan/FYP/model/configs.yaml")
#             model_path = "D:/Hassan/FYP/model/model.onnx"
#             model = ImageToWordModel(model_path=model_path, char_list=configs.vocab)
#             formatted_output = process_images(image_data, model)

#             # Create a new ProcessedImage instance
#             processed_image = ProcessedImage.objects.create(
#                 user=user_instance,
#                 file=uploaded_file,
#                 processed_text=formatted_output,
#                 name=name,
#                 upload_date=datetime.now(),
#                 file_type=file_type,  # Replace with the actual file type
#             )

#             return JsonResponse({'processed_image_id': processed_image.id, 'extracted_text': formatted_output}, status=200)

#         else:
#             return JsonResponse({'error': 'User not authenticated'}, status=401)

#     return JsonResponse({'error': 'Please provide a file'}, status=400)
from django.core.files.storage import default_storage

@api_view(['POST'])
def process_uploaded_image(request):
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
            # image_data = uploaded_file.read()

            # Save the uploaded file
            file_path = default_storage.save(uploaded_file.name, uploaded_file)
            image_data = default_storage.open(file_path).read() 
            
            # Save image names to the dynamic text file
            save_image_names_to_text_file(image_data, file_path)

            # Perform image processing using the existing logic
            configs = BaseModelConfigs.load("D:/Hassan/FYP/model/configs.yaml")
            model_path = "D:/Hassan/FYP/model/model.onnx"
            model = ImageToWordModel(model_path=model_path, char_list=configs.vocab)
            # formatted_output = process_image(image_data, 25, 11, 5, 100, 1000)
            formatted_output = process_images(file_path, model)


            # Create a new ProcessedImage instance
            processed_image = ProcessedImage.objects.create(
                user=user_instance,
                file=uploaded_file,
                processed_text=formatted_output,
                name=name,
                upload_date=datetime.now(),
                file_type=file_type,
            )

            return JsonResponse({'processed_image_id': processed_image.id, 'extracted_text': formatted_output.replace('\n',' ')}, status=200)

        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

    return JsonResponse({'error': 'Please provide a file'}, status=400)


# def process_images_from_bytes(image_data):
#     # Load model configurations
#     configs = BaseModelConfigs.load("D:/Hassan/FYP/model/configs.yaml")

#     # Set the path to the ONNX model
#     model_path = "D:/Hassan/FYP/model/model.onnx"

#     # Create an instance of the ImageToWordModel
#     model = ImageToWordModel(model_path=model_path, char_list=configs.vocab)

#     # Process the image and return the extracted text
#     return process_images(image_data, model)


@api_view(['GET'])
def fetch_extracted_data(request):
    user = request.user  # Assuming the user is authenticated
    if user.is_authenticated:
        try:
            user_instance = CustomUser.objects.get(username=user.username)
        except CustomUser.DoesNotExist:
            user_instance = CustomUser.objects.create(username=user.username)

        # Fetch all fields for the user
        extracted_data = ProcessedImage.objects.filter(user=user_instance).values()
        
        return JsonResponse({'extracted_data': list(extracted_data)}, status=200)
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)
         
   

@api_view(['PATCH'])
def update_hand_document(request, id): 
    user = request.user
    if user.is_authenticated:  
        try:
            hand_document = ProcessedImage.objects.get(id=id)
        except ProcessedImage.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

        hand_updated_data = request.data  # Assuming the API receives a list of objects

        print("Received Data:", hand_updated_data)
 
        hand_document.processed_text = hand_updated_data
        hand_document.save() 
    
        return JsonResponse({'message': 'Data updated successfully'}, status=status.HTTP_200_OK)
    else:     
        return JsonResponse({'error': 'User not authenticated'}, status=401)
    

@api_view(['DELETE'])
def delete_hand_document(request, document_id):
    user = request.user
    if user.is_authenticated: 
        try:
            # Retrieve the document based on the provided ID
            document = ProcessedImage.objects.get(id=document_id)

            # Check if the user is the owner of the document
            if document.user == request.user:
                # Delete the document
                document.delete()

                return JsonResponse({'message': 'Document deleted successfully'}, status=200)
            else:
                return JsonResponse({'error': 'Unauthorized to delete this document'}, status=401)

        except ProcessedImage.DoesNotExist:
            return JsonResponse({'error': 'Document not found'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        

@api_view(['GET'])
def fetch_handwriting_stats(request):
    user = request.user
    if user.is_authenticated:
        try:
            user_instance = CustomUser.objects.get(username=user.username)
        except CustomUser.DoesNotExist:
            user_instance = CustomUser.objects.create(username=user.username)

        # Fetch stats for handwriting_recognition
        handwriting_stats = {
            'handwrittenDocumentsCount': ProcessedImage.objects.filter(user=user_instance).count(),
            'handwrittenDocuments': ProcessedImage.objects.filter(user=user_instance, file_type__in=['png', 'jpg']).count(),

        }

        return JsonResponse(handwriting_stats, status=200)
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)