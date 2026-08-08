import pytest
from app.services.graph_service import (
    normalize_concept_name,
    validate_and_clean_metadata,
    GraphService
)
from app.schemas.graph import KnowledgeMetadata, LearningPathResponse, GraphVisualizationResponse
from app.db.neo4j import is_neo4j_available


def test_normalize_concept_name():
    """Verify canonical normalization removes spaces, hyphens, and casing variations."""
    assert normalize_concept_name("Binary Search") == "binary_search"
    assert normalize_concept_name("binary search") == "binary_search"
    assert normalize_concept_name("Binary-Search") == "binary_search"
    assert normalize_concept_name("binary_search") == "binary_search"
    assert normalize_concept_name("Dijkstra's Algorithm") == "dijkstras_algorithm"
    assert normalize_concept_name("O(log n)") == "olog_n"
    assert normalize_concept_name("") == ""



def test_validate_and_clean_metadata():
    """Verify raw dict metadata validation and cleaning."""
    raw = {
        "primary_concept": "  Binary Search  ",
        "concepts": ["Searching", "Searching", "", 123, "Divide and Conquer"],
        "algorithms": ["Binary Search"],
        "data_structures": ["Array"],
        "prerequisites": ["Sorting"],
        "related_concepts": ["Linear Search"],
        "complexity": ["O(log n)"]
    }
    meta = validate_and_clean_metadata(raw)
    assert meta.primary_concept == "Binary Search"
    assert meta.concepts == ["Searching", "Divide and Conquer"]
    assert meta.algorithms == ["Binary Search"]
    assert meta.data_structures == ["Array"]
    assert meta.prerequisites == ["Sorting"]
    assert meta.complexity == ["O(log n)"]


def test_neo4j_graceful_fallback_when_disabled():
    """Verify that graph service functions return valid fallback responses when Neo4j is disabled or offline."""
    # When Neo4j is not connected, get_graph_context_for_prompt should return empty string cleanly
    ctx = GraphService.get_graph_context_for_prompt("Binary Search")
    assert isinstance(ctx, str)

    # Learning path should return structured model without crashing
    lp = GraphService.get_learning_path("Binary Search")
    assert isinstance(lp, LearningPathResponse)
    assert lp.concept == "Binary Search"

    # Visualization should return GraphVisualizationResponse with nodes/edges
    vis = GraphService.get_subgraph_visualization("Binary Search")
    assert isinstance(vis, GraphVisualizationResponse)
    assert isinstance(vis.nodes, list)
    assert isinstance(vis.edges, list)


def test_ingest_knowledge_metadata_safety():
    """Verify ingesting knowledge metadata does not raise exceptions when Neo4j is unavailable."""
    meta = KnowledgeMetadata(
        primary_concept="Merge Sort",
        concepts=["Sorting", "Divide and Conquer"],
        algorithms=["Merge Sort"],
        data_structures=["Array"],
        prerequisites=["Array", "Recursion"],
        related_concepts=["Quick Sort"],
        complexity=["O(n log n)"]
    )
    # Must not raise an exception even if Neo4j driver is not active
    GraphService.ingest_knowledge_metadata(
        lesson_id="test_lesson_123",
        title="Merge Sort Lesson",
        user_id=1,
        metadata=meta
    )
