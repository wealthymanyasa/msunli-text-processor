from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import logging
from ..schemas import (
    TokenizeRequest, TokenizeResponse, BatchTokenizeRequest,
    StatisticsResponse, HealthCheckResponse
)
from ..utils.shona_processor import shona_processor

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/tokenize", response_model=TokenizeResponse)
async def tokenize_text(request: TokenizeRequest):
    """Tokenize Shona text with cleaning options"""
    try:
        cleaned_text = await shona_processor.clean_text(request.text)
        tokens = await shona_processor.tokenize(
            request.text, 
            remove_punctuation=request.remove_punctuation,
            remove_stopwords=request.remove_stopwords
        )
        
        return TokenizeResponse(
            original_text=request.text,
            cleaned_text=cleaned_text,
            tokens=tokens
        )
    except Exception as e:
        logger.error(f"Tokenization error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@router.post("/tokenize/batch")
async def batch_tokenize_text(request: BatchTokenizeRequest):
    """Tokenize multiple Shona texts in batch"""
    try:
        results = await shona_processor.process_batch(
            request.texts,
            remove_punctuation=request.remove_punctuation,
            remove_stopwords=request.remove_stopwords
        )
        return {"results": results}
    except Exception as e:
        logger.error(f"Batch tokenization error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch processing error: {str(e)}")

@router.post("/statistics", response_model=StatisticsResponse)
async def get_text_statistics(request: TokenizeRequest):
    """Get comprehensive statistics about Shona text"""
    try:
        statistics = await shona_processor.get_statistics(request.text)
        return StatisticsResponse(
            statistics=statistics,
            word_frequency=statistics.get("word_frequency", {})
        )
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail=f"Statistics error: {str(e)}")

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test the processor
        test_text = "Mhuri yese"
        await shona_processor.clean_text(test_text)
        return HealthCheckResponse(
            status="healthy",
            version="1.0.0",
            processor_ready=True
        )
    except Exception as e:
        return HealthCheckResponse(
            status="degraded",
            version="1.0.0",
            processor_ready=False
        )