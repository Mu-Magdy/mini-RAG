from fastapi import APIRouter, Depends,FastAPI,UploadFile,File, status,Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings,Settings
from controllers import DataController,ProjectController,ProcessController
from models import ResponseSignal
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemas import DataChunk
from .schemas.data import ProcessRequest
import os
import aiofiles
import logging

logger = logging.getLogger("uvicorn.error")
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"],
)


@data_router.post("/upload/{project_id}")
async def upload_data(request:Request,project_id:str,file:UploadFile=File(...),
                      app_settings:Settings=Depends(get_settings)):
    
    project_model=ProjectModel(db_client=request.app.db_client)
    project= await project_model.get_project_or_create_one(project_id=project_id)
    data_controller = DataController()
    #validate file
    is_valid,message = data_controller.validate_uploaded_file(file=file, settings=app_settings)
    if not is_valid:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"error":message})

    #save file
    project_dir_path = ProjectController().get_project_path(project_id=project_id)
    file_path, file_id = data_controller.generate_unique_filename(original_filename=file.filename,project_id=project_id)
    
    try:
        async with aiofiles.open(file_path,"wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content={"error":str(e)})
         
                
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={
                            "message":ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                            "file_id":file_id
                            }
                        )


@data_router.post("/process/{project_id}")
async def process_endpoint(request:Request,project_id:str,process_request:ProcessRequest):
    
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset
    
    project_model=ProjectModel(db_client=request.app.db_client)
    project= await project_model.get_project_or_create_one(project_id=project_id)
    
    
    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_id=file_id)
    file_chunks = process_controller.process_file_content(file_id=file_id,chunk_size=chunk_size,overlap_size=overlap_size,file_content=file_content)
    
    if file_chunks is None:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"error":ResponseSignal.FILE_PROCESSING_ERROR.value})
    
    file_chunks_records=[
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i+1,
            chunk_project_id=project.id
        )
        for i,chunk in enumerate(file_chunks)
    ]
    
    chunk_model=ChunkModel(db_client=request.app.db_client)
    
    if do_reset==1:
        await chunk_model.delete_chunks_by_project_id(project_id=project.id)
    
    
    no_records=await chunk_model.insert_many_chunks(chunks=file_chunks_records)
    
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":ResponseSignal.FILE_PROCESSING_SUCCESS.value,"inserted_chunks":no_records})