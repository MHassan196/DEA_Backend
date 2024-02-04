# main_api/urls.py
from django.urls import path
from .views import upload_and_extract_data, upload_and_extract_image

urlpatterns = [
    path('upload/', upload_and_extract_data, name='upload_and_extract_data'),
    path('upload/image/', upload_and_extract_image, name='upload_and_extract_image'),
    # Add other URL patterns as needed for your file operations
]


# from django.urls import path
# from . import views

# urlpatterns = [
#     path('upload/excel/', views.upload_and_extract_excel, name='upload_and_extract_excel'),
#     path('upload/pdf/', views.upload_and_extract_pdf, name='upload_and_extract_pdf'),
#     path('upload/word/', views.upload_and_extract_word, name='upload_and_extract_word'),
#     path('upload/image/', views.upload_and_extract_image, name='upload_and_extract_image'),
#     # Add other URL patterns as needed for your file operations
# ]
