# main_api/urls.py
from django.urls import path
from .views import fetch_dashboard_stats, fetch_extracted_data, update_document, upload_and_extract_data, upload_and_extract_image, fetch_collection_data, delete_document

urlpatterns = [
    path('upload/', upload_and_extract_data, name='upload_and_extract_data'),
    path('upload/image/', upload_and_extract_image, name='upload_and_extract_image'),
    path('fetch_extracted_data/', fetch_extracted_data, name='fetch_extracted_data'),  # Add this line
    path('fetch_collection_data/<str:collection_name>/', fetch_collection_data, name='fetch_collection_data'),  # Add this line
    path('update_document/<int:id>/', update_document, name='update_document'),  # Add this line
    path('delete_document/<int:document_id>/', delete_document, name='delete_document'),
    path('fetch_dashboard_stats/', fetch_dashboard_stats, name='fetch_dashboard_stats'),

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
