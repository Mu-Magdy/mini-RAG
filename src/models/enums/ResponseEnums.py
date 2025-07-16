from enum import Enum

class ResponseSignal(Enum):
    SUCCESS = "success" 
    ERROR = "error"
    WARNING = "warning"
    FILE_UPLOAD_SUCCESS = "file_upload_success"
    FILE_SIZE_EXCEEDS_MAX_SIZE = "file_size_exceeds_max_size"
    FILE_TYPE_NOT_ALLOWED = "file_type_not_allowed"
    FILE_PROCESSING_ERROR = "file_processing_error"
    FILE_PROCESSING_SUCCESS = "file_processing_success"