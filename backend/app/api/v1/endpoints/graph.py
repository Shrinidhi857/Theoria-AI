from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status

from app.api.deps import get_current_active_user, get_optional_current_user
from app.models.user import User
from app.schemas.graph import (
    LearningPathResponse,
    RelatedConceptsResponse,
    GraphVisualizationResponse,
    ConceptRecommendation
)
from app.services.graph_service import GraphService

router = APIRouter(prefix="/graph", tags=["Knowledge Graph"])


@router.get("/learning-path/{concept}", response_model=LearningPathResponse)
def get_learning_path_endpoint(concept: str):
    """
    Get graph learning path for a concept (prerequisites, related concepts, next concepts).
    """
    return GraphService.get_learning_path(concept)


@router.get("/concepts/{concept}/related", response_model=RelatedConceptsResponse)
def get_related_concepts_endpoint(concept: str):
    """
    Get detailed graph traversal breakdown for a concept (prerequisites, dependent, related, algorithms, data structures, complexity).
    """
    return GraphService.get_related_concepts(concept)


@router.get("/visualization", response_model=GraphVisualizationResponse)
def get_graph_visualization_endpoint(
    center_concept: Optional[str] = Query(default=None, description="Optional center concept for subgraph extraction"),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Get graph representation (nodes & edges) suitable for frontend visualizer rendering.
    """
    user_id = current_user.id if current_user else None
    return GraphService.get_subgraph_visualization(center_concept=center_concept, user_id=user_id)


@router.get("/recommendations", response_model=List[ConceptRecommendation])
def get_user_recommendations_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get personalized concept recommendations based on concepts the user has completed.
    """
    return GraphService.get_user_recommendations(user_id=current_user.id)


@router.post("/concepts/{concept}/complete")
def mark_concept_completed_endpoint(
    concept: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Mark a concept as completed for the authenticated user in the Neo4j Knowledge Graph.
    """
    success = GraphService.record_user_completed_concept(user_id=current_user.id, concept_name=concept)
    if not success:
        return {"status": "ok", "message": f"Concept '{concept}' completion status acknowledged."}
    return {"status": "ok", "message": f"Concept '{concept}' marked as completed."}
