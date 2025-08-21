from .BaseController import BaseController
from fastapi import UploadFile
from models import ResponseSignal
import os

class ProjectController(BaseController):
    
    def __init__(self):
        super().__init__()

    def get_project_path(self, project_id: str):
        project_dir = os.path.join(
            self.files_dir,
<<<<<<< HEAD
            str(project_id)
=======
            project_id
>>>>>>> d73c391 (Merge pull request #1 from Mu-Magdy/feat-semantic-search)
        )

        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        return project_dir

    
