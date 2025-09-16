from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Optional
from datetime import datetime

# Authentication and User schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Text Processing schemas
class TokenizeRequest(BaseModel):
    text: str = Field(..., description="Text to process")
    language: str = Field(..., description="Language of the text")
    remove_punctuation: bool = Field(True, description="Remove punctuation from tokens")
    remove_stopwords: bool = Field(False, description="Remove stopwords")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Mhuri yese yakaungana pamba pavakuru. Vakuru vakataura nyaya dzechinyakare.",
                "language": "sn",  # ISO 639-1 code for Shona
                "remove_punctuation": True,
                "remove_stopwords": False
            }
        }

class BatchTokenizeRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to process")
    language: str = Field(..., description="Language of the texts")
    remove_punctuation: bool = Field(True, description="Remove punctuation from tokens")
    remove_stopwords: bool = Field(False, description="Remove stopwords")

class TokenizeResponse(BaseModel):
    original_text: str
    cleaned_text: str
    tokens: List[str]
    language: str
    statistics: Optional[Dict] = None
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class StatisticsResponse(BaseModel):
    statistics: Dict
    word_frequency: Dict[str, int]

class HealthCheckResponse(BaseModel):
    status: str
    version: str
    processor_ready: bool
    database_ready: bool
    redis_ready: bool