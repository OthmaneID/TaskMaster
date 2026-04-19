from fastapi.routing import APIRouter
from services.program import listPrograms, restartProgram, startProgram, statusProgram, stopProgram  

router = APIRouter(prefix="/programs")


@router.get("/list")
async def list_programs():
    return listPrograms()

@router.get("/status/{service_name}")
async def status_program(service_name: str):
    return statusProgram(service_name)


@router.post("/start/{service_name}")
async def start_program(service_name: str):
    return startProgram(service_name)


@router.post("/stop/{service_name}")
async def stop_program(service_name: str):
    return stopProgram(service_name)

@router.post("/restart/{service_name}")
async def restart_program(service_name: str):
    return restartProgram(service_name)

@router.get("/resources")
async def get_resources(): # to impliment later
    return {"cpu": "N/A", "ram": "N/A"}
