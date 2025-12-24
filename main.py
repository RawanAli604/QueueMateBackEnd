from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.venue import router as venue_router
from controllers.waitlistEntry import router as waitlist_router
from controllers.users import router as user_router
from controllers.notifications import router as notifications_router

app = FastAPI()

origins = [
"http://127.0.0.1:5174"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(venue_router, prefix="/api")
app.include_router(waitlist_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")

@app.get('/')
def home():
    # Hello world function
    return {'message': 'Hello World!'}