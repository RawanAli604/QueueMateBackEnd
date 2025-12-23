from fastapi import FastAPI
from controllers.users import router as UserRouter
from controllers.venue import router as venuesRouter
from controllers.admin import router as AdminRouter

app = FastAPI()

app.include_router(UserRouter, prefix="/api")
app.include_router(AdminRouter, prefix="/api/admin")
app.include_router(venuesRouter, prefix="/api")

@app.get('/')
def home():
    return 'Hello World!'

