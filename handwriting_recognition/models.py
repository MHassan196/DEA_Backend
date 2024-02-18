# handwriting_recognition/models.py
from django.db import models

from authentication.models import CustomUser

class ProcessedImage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    file = models.FileField(upload_to='handwritten_files/')    
    processed_text = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)  # New field for the name of the file or data
    upload_date = models.DateTimeField(auto_now_add=True, null=True)  # New field for the date of file upload
    file_type = models.CharField(max_length=10, blank=True, null=True)  # New field for the file type

