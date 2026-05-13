from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import Base, engine
from modules.auth.routers import router as auth_router
from modules.users.routers import router as users_router
from modules.friendships.routers import router as friendships_router


Base.metadata.create_all(engine)

app = FastAPI(
    title="Social Network API",
    version="1.0",
    description="Backend API for users and friendships"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"], #?http://localhost:3000?
    allow_credentials = True,
    allow_headers = ["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(friendships_router)

@app.get("/", tags=["Health"])
def root():
    return {"message": "API is running"}




