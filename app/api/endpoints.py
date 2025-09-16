from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List
import logging
from datetime import datetime
from ..schemas import (
    TokenizeRequest, TokenizeResponse, BatchTokenizeRequest,
    StatisticsResponse, HealthCheckResponse
)
from ..utils.multilang_processor import MultiLanguageProcessor
from ..security.auth import get_current_active_user
from ..core.dependencies import rate_limit_dependency

router = APIRouter()
logger = logging.getLogger(__name__)
text_processor = MultiLanguageProcessor()

@router.post("/tokenize", response_model=TokenizeResponse)
async def tokenize_text(
    request: TokenizeRequest,
    user=Depends(get_current_active_user)
):
    """Tokenize text with cleaning options"""
    try:
        result = await text_processor.tokenize(
            text=request.text,
            language=request.language,
            remove_punctuation=request.remove_punctuation,
            remove_stopwords=request.remove_stopwords
        )
        
        return TokenizeResponse(
            original_text=request.text,
            cleaned_text=result["cleaned_text"],
            tokens=result["tokens"],
            language=request.language,
            user_id=user.id,
            created_at=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Tokenization error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@router.post("/tokenize/batch")
async def batch_tokenize_text(
    request: BatchTokenizeRequest,
    user=Depends(get_current_active_user)
):
    """Tokenize multiple texts in batch"""
    try:
        results = await text_processor.batch_tokenize(
            texts=request.texts,
            language=request.language,
            remove_punctuation=request.remove_punctuation,
            remove_stopwords=request.remove_stopwords
        )
        return {
            "results": [
                {
                    "original_text": text,
                    "cleaned_text": result.get("cleaned_text", ""),
                    "tokens": result.get("tokens", []),
                    "language": request.language,
                    "user_id": user.id,
                    "created_at": datetime.utcnow()
                }
                for text, result in zip(request.texts, results)
            ]
        }
    except Exception as e:
        logger.error(f"Batch tokenization error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch processing error: {str(e)}")

@router.post("/statistics", response_model=StatisticsResponse)
async def get_text_statistics(
    request: TokenizeRequest,
    user=Depends(get_current_active_user)
):
    """Get comprehensive statistics about text"""
    try:
        result = await text_processor.tokenize(
            text=request.text,
            language=request.language,
            remove_punctuation=True,
            remove_stopwords=False
        )
        word_freq = {word: result["tokens"].count(word) for word in set(result["tokens"])}
        statistics = {
            "total_words": len(result["tokens"]),
            "unique_words": len(word_freq),
            "total_characters": len(request.text),
            "language": request.language
        }
        return StatisticsResponse(
            statistics=statistics,
            word_frequency=word_freq
        )
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail=f"Statistics error: {str(e)}")

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test the processor with Shona text
        test_text = "Mhuri yese"
        test_result = text_processor.tokenize(text=test_text, language="sn")
        processor_ready = bool(test_result.get("tokens"))
        
        return HealthCheckResponse(
            status="healthy",
            version="1.0.0",
            processor_ready=processor_ready,
            database_ready=True,  # This will be checked in the main.py health check
            redis_ready=True      # This will be checked in the main.py health check
        )
    except Exception as e:
        return HealthCheckResponse(
            status="degraded",
            version="1.0.0",
            processor_ready=False,
            database_ready=True,  # This will be checked in the main.py health check
            redis_ready=True      # This will be checked in the main.py health check
        )