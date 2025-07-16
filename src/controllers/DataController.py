from .BaseController import BaseController  
from fastapi import UploadFile
from .ProjectController import ProjectController
from models import ResponseSignal
from helpers.config import Settings
import re 
import os

class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1024*1024 #1MB
        
    def validate_uploaded_file(self, file: UploadFile, settings: Settings):
        if file.content_type not in settings.FILE_ALLOWED_TYPES:
            return False, {"error":ResponseSignal.FILE_TYPE_NOT_ALLOWED.value}
        if file.size > settings.FILE_MAX_SIZE*self.size_scale:
            return False , {"error":ResponseSignal.FILE_SIZE_EXCEEDS_MAX_SIZE.value}
        return True, {"message":ResponseSignal.FILE_UPLOAD_SUCCESS.value}

    def generate_unique_filename(self,original_filename:str,project_id:str):
        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)
        clean_filename = self.get_clean_filename(original_filename=original_filename)
        unique_filename = f"{random_key}_{clean_filename}"
        new_file_path = os.path.join(project_path,unique_filename)
        
        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            unique_filename = f"{random_key}_{clean_filename}"
            new_file_path = os.path.join(project_path,unique_filename)
        
        return new_file_path, unique_filename
        
    def get_clean_filename(self,original_filename:str):
        clean_filename = re.sub(r'[^\w. ]', '', original_filename.strip())
        clean_filename = clean_filename.replace(" ","_")
        return clean_filename