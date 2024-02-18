# main_api/models.py
from django.db import models
from authentication.models import CustomUser


class Document(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    file = models.FileField(upload_to='uploaded_files/')
    extracted_data = models.JSONField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)  # New field for the name of the file or data
    dynamic_collection_name = models.CharField(max_length=255, blank=True, null=True)  # New field for the dynamically created collection name
    upload_date = models.DateTimeField(auto_now_add=True, null=True)  # New field for the date of file upload
    file_type = models.CharField(max_length=10, blank=True, null=True)  # New field for the file type

    def __str__(self):
        return f"{self.file.name}" 
