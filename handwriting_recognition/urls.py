# handwriting_recognition/urls.py
from django.urls import path
from .views import fetch_handwriting_stats, process_uploaded_image, fetch_extracted_data, update_hand_document, delete_hand_document

urlpatterns = [
    path('process_image/', process_uploaded_image, name='process_uploaded_image'),
    path('fetch_handwritten_data/', fetch_extracted_data, name='fetch_extracted_data'),
    path('update_handwritten_data/<int:id>/', update_hand_document, name='update_hand_document'),
    path('delete_hand_document/<int:document_id>/', delete_hand_document, name='delete_hand_document'),
    path('fetch_handwriting_stats/', fetch_handwriting_stats, name='fetch_handwriting_stats'),

]
