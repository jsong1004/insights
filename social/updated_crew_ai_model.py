# Update your core/crew_ai.py to include social features in the GeneratedInsights model

from crewai import Agent, Task, Crew, Process
from crewai_tools.tools.tavily_search_tool.tavily_search_tool import TavilySearchTool
from crewai_tools.tools.serper_dev_tool.serper_dev_tool import SerperDevTool
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import os
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

# Enhanced Pydantic models for structured output with social features
class InsightItem(BaseModel):
    title: str = Field(description="Compelling insight title")
    summary: str = Field(description="Detailed insight summary")
    key_points: List[str] = Field(description="Key bullet points")
    detailed_report: str = Field(description="Comprehensive detailed analysis (500-800 words)")
    significance: str = Field(description="Why this insight matters")
    sources: List[str] = Field(description="Source URLs")
    confidence_score: float = Field(description="Confidence score 0-1")
    research_quality: str = Field(description="Quality assessment")

class GeneratedInsights(BaseModel):
    id: str = Field(description="Unique insight ID")
    topic: str = Field(description="Research topic")
    instructions: str = Field(description="User instructions")
    source_type: str = Field(description="Search source type (general/news/finance)", default="general")
    time_range: Optional[str] = Field(description="Search time range filter", default=None)
    timestamp: str = Field(description="Generation timestamp")
    insights: List[InsightItem] = Field(description="Generated insights")
    total_insights: int = Field(description="Total number of insights")
    processing_time: float = Field(description="Time taken to generate")
    total_tokens: int = Field(description="Total tokens used", default=0)
    agent_notes: str = Field(description="Notes from AI agents")
    
    # Enhanced Social features
    author_id: Optional[str] = Field(description="User ID of the author", default=None)
    author_name: Optional[str] = Field(description="Display name of the author", default="Anonymous")
    author_email: Optional[str] = Field(description="Email of the author", default=None)
    is_shared: bool = Field(description="Whether this insight is publicly shared", default=True)
    likes: int = Field(description="Number of likes", default=0)
    liked_by: List[str] = Field(description="List of user IDs who liked this", default_factory=list)
    
    # Admin features
    is_pinned: bool = Field(description="Whether this insight is pinned by admin", default=False)
    pinned_by: Optional[str] = Field(description="Admin user ID who pinned this", default=None)
    pinned_at: Optional[str] = Field(description="When this insight was pinned", default=None)
    
    # Enhanced metadata
    view_count: int = Field(description="Number of times viewed", default=0)
    featured: bool = Field(description="Whether featured on homepage", default=False)
    category: Optional[str] = Field(description="Category/tag for the insight", default=None)
    language: str = Field(description="Language of the content", default="en")
    
    # Quality metrics
    quality_score: Optional[float] = Field(description="Overall quality score 0-1", default=None)
    engagement_score: Optional[float] = Field(description="Engagement score based on likes/views", default=None)

# Rest of your AIInsightsCrew class remains the same...