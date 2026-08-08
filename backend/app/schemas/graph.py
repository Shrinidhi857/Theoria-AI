from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


# ── Gemini Extracted Metadata Schema ──────────────────────────────────────────
class KnowledgeMetadata(BaseModel):
    """Structured educational knowledge metadata extracted by Gemini during lesson planning."""
    primary_concept: str = Field(default="Computer Science Concept", description="Main concept taught in lesson")
    concepts: List[str] = Field(default_factory=list, description="General concepts involved in lesson")
    algorithms: List[str] = Field(default_factory=list, description="Specific algorithms demonstrated")
    data_structures: List[str] = Field(default_factory=list, description="Data structures used or explained")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisite concepts needed before this lesson")
    related_concepts: List[str] = Field(default_factory=list, description="Related algorithms or concepts")
    complexity: List[str] = Field(default_factory=list, description="Time and space complexity notations (e.g. O(log n))")


# ── Graph Entity Schemas ──────────────────────────────────────────────────────
class ConceptNode(BaseModel):
    id: str
    name: str
    normalized_name: str
    description: Optional[str] = None
    category: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AlgorithmNode(BaseModel):
    id: str
    name: str
    normalized_name: str
    description: Optional[str] = None
    category: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class DataStructureNode(BaseModel):
    id: str
    name: str
    normalized_name: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ComplexityNode(BaseModel):
    notation: str
    description: Optional[str] = None


class LessonNode(BaseModel):
    id: str
    title: str
    user_id: Optional[int] = None
    video_id: Optional[int] = None
    created_at: Optional[str] = None


# ── Graph API Response Schemas ────────────────────────────────────────────────
class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # Concept, Algorithm, DataStructure, Complexity, Lesson
    description: Optional[str] = None
    category: Optional[str] = None
    notation: Optional[str] = None
    completed: Optional[bool] = False


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str  # PREREQUISITE_FOR, RELATED_TO, USES, SOLVES, HAS_COMPLEXITY, COVERS, VISUALIZES


class GraphVisualizationResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class LearningPathResponse(BaseModel):
    concept: str
    normalized_name: str
    prerequisites: List[str] = Field(default_factory=list)
    related: List[str] = Field(default_factory=list)
    next_concepts: List[str] = Field(default_factory=list)


class RelatedConceptsResponse(BaseModel):
    concept: str
    prerequisites: List[str] = Field(default_factory=list)
    related: List[str] = Field(default_factory=list)
    dependent: List[str] = Field(default_factory=list)
    algorithms: List[str] = Field(default_factory=list)
    data_structures: List[str] = Field(default_factory=list)
    complexity: List[str] = Field(default_factory=list)


class ConceptRecommendation(BaseModel):
    concept: str
    normalized_name: str
    reason: str
    prerequisites_met: List[str] = Field(default_factory=list)
