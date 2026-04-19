from fastapi import FastAPI
from api.routes import router
from uvicorn import run
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi import docs


app = FastAPI()


CORSMiddleware(
    app=app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    router=router
)

app.get("/", openapi_extra=docs.get_swagger_ui_html)


# i need to :
# - list programs
# - start/stop/restarr programs
# - view program status (name, processes Num, status, stop signal, exit codes)






if __name__ == "__main__":
    run(app, host="0.0.0.0", port = 8000)