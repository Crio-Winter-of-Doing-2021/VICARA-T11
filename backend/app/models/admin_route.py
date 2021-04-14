from pydantic import BaseModel, Field, EmailStr


class StorageLimitModel(BaseModel):
    email: EmailStr
    storage_limit: int = Field(..., ge=1)
