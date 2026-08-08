import re
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from app.db.neo4j import get_neo4j_session, is_neo4j_available
from app.schemas.graph import (
    KnowledgeMetadata,
    GraphNode,
    GraphEdge,
    GraphVisualizationResponse,
    LearningPathResponse,
    RelatedConceptsResponse,
    ConceptRecommendation
)

logger = logging.getLogger(__name__)


def normalize_concept_name(name: str) -> str:
    """
    Canonical concept normalizer to prevent duplicate nodes.
    Converts "Binary Search", "binary search", "binary-search", "Binary search algorithm" -> "binary_search".
    """
    if not name or not isinstance(name, str):
        return ""
    
    clean = name.strip()
    # Remove common word suffixes like "algorithm", "data structure" if present as fluff, or sanitize
    clean = re.sub(r'[\s\-]+', '_', clean)
    clean = re.sub(r'[^a-zA-Z0-9\_]', '', clean)
    return clean.lower()


def validate_and_clean_metadata(raw: Dict[str, Any]) -> KnowledgeMetadata:
    """Validates raw Gemini extracted dict and cleans metadata arrays."""
    if not isinstance(raw, dict):
        return KnowledgeMetadata(primary_concept="General Concept")

    def clean_str_list(lst: Any) -> List[str]:
        if not isinstance(lst, list):
            return []
        cleaned = []
        for item in lst:
            if item and isinstance(item, str) and item.strip():
                val = item.strip()
                if len(val) <= 100 and val not in cleaned:
                    cleaned.append(val)
        return cleaned

    primary = str(raw.get("primary_concept") or "General Concept").strip()
    return KnowledgeMetadata(
        primary_concept=primary,
        concepts=clean_str_list(raw.get("concepts")),
        algorithms=clean_str_list(raw.get("algorithms")),
        data_structures=clean_str_list(raw.get("data_structures")),
        prerequisites=clean_str_list(raw.get("prerequisites")),
        related_concepts=clean_str_list(raw.get("related_concepts")),
        complexity=clean_str_list(raw.get("complexity"))
    )


def init_neo4j_constraints():
    """Initializes uniqueness constraints and indexes in Neo4j."""
    if not is_neo4j_available():
        return

    queries = [
        "CREATE CONSTRAINT concept_norm_name IF NOT EXISTS FOR (c:Concept) REQUIRE c.normalized_name IS UNIQUE",
        "CREATE CONSTRAINT algorithm_norm_name IF NOT EXISTS FOR (a:Algorithm) REQUIRE a.normalized_name IS UNIQUE",
        "CREATE CONSTRAINT datastructure_norm_name IF NOT EXISTS FOR (d:DataStructure) REQUIRE d.normalized_name IS UNIQUE",
        "CREATE CONSTRAINT complexity_notation IF NOT EXISTS FOR (cx:Complexity) REQUIRE cx.notation IS UNIQUE",
        "CREATE CONSTRAINT lesson_id IF NOT EXISTS FOR (l:Lesson) REQUIRE l.id IS UNIQUE",
        "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE"
    ]

    with get_neo4j_session() as session:
        if not session:
            return
        for q in queries:
            try:
                session.run(q)
            except Exception as e:
                logger.debug(f"[Neo4j] Constraint setup note: {e}")
        logger.info("[Neo4j] Graph constraints verified/created.")


class GraphService:
    """Service layer managing all Neo4j Cypher queries and Knowledge Graph interactions."""

    @staticmethod
    def create_or_get_concept(name: str, category: str = "Concept", description: str = "") -> Optional[str]:
        """Creates or gets a Concept node using canonical normalized_name."""
        norm = normalize_concept_name(name)
        if not norm:
            return None

        query = """
        MERGE (c:Concept {normalized_name: $norm})
        ON CREATE SET c.id = $norm, c.name = $name, c.category = $category,
                      c.description = $description, c.created_at = datetime(), c.updated_at = datetime()
        ON MATCH SET c.updated_at = datetime()
        RETURN c.normalized_name AS norm
        """
        with get_neo4j_session() as session:
            if not session:
                return None
            try:
                res = session.run(query, norm=norm, name=name, category=category, description=description)
                rec = res.single()
                logger.info(f"[Neo4j] Created/Retrieved concept node: {name} ({norm})")
                return rec["norm"] if rec else norm
            except Exception as e:
                logger.warning(f"[Neo4j] Failed to create concept '{name}': {e}")
                return None

    @staticmethod
    def create_or_get_algorithm(name: str, category: str = "Algorithm", description: str = "") -> Optional[str]:
        """Creates or gets an Algorithm node."""
        norm = normalize_concept_name(name)
        if not norm:
            return None

        query = """
        MERGE (a:Algorithm {normalized_name: $norm})
        ON CREATE SET a.id = $norm, a.name = $name, a.category = $category,
                      a.description = $description, a.created_at = datetime(), a.updated_at = datetime()
        RETURN a.normalized_name AS norm
        """
        with get_neo4j_session() as session:
            if not session:
                return None
            try:
                res = session.run(query, norm=norm, name=name, category=category, description=description)
                rec = res.single()
                return rec["norm"] if rec else norm
            except Exception as e:
                logger.warning(f"[Neo4j] Failed to create algorithm '{name}': {e}")
                return None

    @staticmethod
    def create_or_get_data_structure(name: str, description: str = "") -> Optional[str]:
        """Creates or gets a DataStructure node."""
        norm = normalize_concept_name(name)
        if not norm:
            return None

        query = """
        MERGE (d:DataStructure {normalized_name: $norm})
        ON CREATE SET d.id = $norm, d.name = $name, d.description = $description,
                      d.created_at = datetime(), d.updated_at = datetime()
        RETURN d.normalized_name AS norm
        """
        with get_neo4j_session() as session:
            if not session:
                return None
            try:
                res = session.run(query, norm=norm, name=name, description=description)
                rec = res.single()
                return rec["norm"] if rec else norm
            except Exception as e:
                logger.warning(f"[Neo4j] Failed to create data structure '{name}': {e}")
                return None

    @staticmethod
    def create_or_get_complexity(notation: str, description: str = "") -> Optional[str]:
        """Creates or gets a Complexity node e.g. O(log n)."""
        notation = notation.strip()
        if not notation:
            return None

        query = """
        MERGE (cx:Complexity {notation: $notation})
        ON CREATE SET cx.description = $description
        RETURN cx.notation AS notation
        """
        with get_neo4j_session() as session:
            if not session:
                return None
            try:
                res = session.run(query, notation=notation, description=description)
                rec = res.single()
                return rec["notation"] if rec else notation
            except Exception as e:
                logger.warning(f"[Neo4j] Failed to create complexity '{notation}': {e}")
                return None

    @staticmethod
    def add_prerequisite(prereq_name: str, target_name: str):
        """Creates relationship: (prereq)-[:PREREQUISITE_FOR]->(target)."""
        p_norm = normalize_concept_name(prereq_name)
        t_norm = normalize_concept_name(target_name)
        if not p_norm or not t_norm or p_norm == t_norm:
            return

        GraphService.create_or_get_concept(prereq_name)
        GraphService.create_or_get_concept(target_name)

        query = """
        MATCH (p {normalized_name: $p_norm})
        MATCH (t {normalized_name: $t_norm})
        MERGE (p)-[r:PREREQUISITE_FOR]->(t)
        RETURN count(r)
        """
        with get_neo4j_session() as session:
            if session:
                try:
                    session.run(query, p_norm=p_norm, t_norm=t_norm)
                    logger.info(f"[Neo4j] Created relationship: {prereq_name} -> PREREQUISITE_FOR -> {target_name}")
                except Exception as e:
                    logger.warning(f"[Neo4j] Failed to link prerequisite {prereq_name} -> {target_name}: {e}")

    @staticmethod
    def add_related_concept(concept_a: str, concept_b: str):
        """Creates relationship: (a)-[:RELATED_TO]->(b)."""
        a_norm = normalize_concept_name(concept_a)
        b_norm = normalize_concept_name(concept_b)
        if not a_norm or not b_norm or a_norm == b_norm:
            return

        GraphService.create_or_get_concept(concept_a)
        GraphService.create_or_get_concept(concept_b)

        query = """
        MATCH (a {normalized_name: $a_norm})
        MATCH (b {normalized_name: $b_norm})
        MERGE (a)-[r:RELATED_TO]->(b)
        RETURN count(r)
        """
        with get_neo4j_session() as session:
            if session:
                try:
                    session.run(query, a_norm=a_norm, b_norm=b_norm)
                    logger.info(f"[Neo4j] Created relationship: {concept_a} -> RELATED_TO -> {concept_b}")
                except Exception as e:
                    logger.warning(f"[Neo4j] Failed to link related {concept_a} <-> {concept_b}: {e}")

    @staticmethod
    def add_uses_relationship(algo_name: str, ds_name: str):
        """Creates relationship: (Algorithm)-[:USES]->(DataStructure)."""
        a_norm = normalize_concept_name(algo_name)
        d_norm = normalize_concept_name(ds_name)
        if not a_norm or not d_norm:
            return

        GraphService.create_or_get_algorithm(algo_name)
        GraphService.create_or_get_data_structure(ds_name)

        query = """
        MATCH (a:Algorithm {normalized_name: $a_norm})
        MATCH (d:DataStructure {normalized_name: $d_norm})
        MERGE (a)-[r:USES]->(d)
        RETURN count(r)
        """
        with get_neo4j_session() as session:
            if session:
                try:
                    session.run(query, a_norm=a_norm, d_norm=d_norm)
                except Exception as e:
                    logger.warning(f"[Neo4j] Failed to link uses {algo_name} -> {ds_name}: {e}")

    @staticmethod
    def add_solves_relationship(algo_name: str, concept_name: str):
        """Creates relationship: (Algorithm)-[:SOLVES]->(Concept)."""
        a_norm = normalize_concept_name(algo_name)
        c_norm = normalize_concept_name(concept_name)
        if not a_norm or not c_norm:
            return

        GraphService.create_or_get_algorithm(algo_name)
        GraphService.create_or_get_concept(concept_name)

        query = """
        MATCH (a:Algorithm {normalized_name: $a_norm})
        MATCH (c:Concept {normalized_name: $c_norm})
        MERGE (a)-[r:SOLVES]->(c)
        RETURN count(r)
        """
        with get_neo4j_session() as session:
            if session:
                try:
                    session.run(query, a_norm=a_norm, c_norm=c_norm)
                except Exception as e:
                    logger.warning(f"[Neo4j] Failed to link solves {algo_name} -> {concept_name}: {e}")

    @staticmethod
    def add_complexity_relationship(target_name: str, complexity_notation: str):
        """Creates relationship: (Concept/Algorithm)-[:HAS_COMPLEXITY]->(Complexity)."""
        t_norm = normalize_concept_name(target_name)
        notation = complexity_notation.strip()
        if not t_norm or not notation:
            return

        GraphService.create_or_get_complexity(notation)

        query = """
        MATCH (t {normalized_name: $t_norm})
        MATCH (cx:Complexity {notation: $notation})
        MERGE (t)-[r:HAS_COMPLEXITY]->(cx)
        RETURN count(r)
        """
        with get_neo4j_session() as session:
            if session:
                try:
                    session.run(query, t_norm=t_norm, notation=notation)
                except Exception as e:
                    logger.warning(f"[Neo4j] Failed to link complexity {target_name} -> {notation}: {e}")

    @staticmethod
    def ingest_knowledge_metadata(lesson_id: str, title: str, user_id: Optional[int], metadata: KnowledgeMetadata):
        """
        Ingests Gemini extracted knowledge metadata into Neo4j graph in a structured, idempotent manner.
        """
        if not is_neo4j_available():
            logger.info("[Neo4j] Graph unavailable; skipping metadata ingestion.")
            return

        logger.info(f"[Neo4j] Ingesting knowledge metadata for lesson '{title}' (ID: {lesson_id})...")

        # 1. Create Lesson Node
        les_query = """
        MERGE (l:Lesson {id: $lesson_id})
        ON CREATE SET l.title = $title, l.user_id = $user_id, l.created_at = datetime()
        """
        with get_neo4j_session() as session:
            if session:
                try:
                    session.run(les_query, lesson_id=str(lesson_id), title=title, user_id=user_id)
                except Exception as e:
                    logger.warning(f"[Neo4j] Failed creating lesson node: {e}")

        # 2. Primary Concept
        primary_norm = GraphService.create_or_get_concept(metadata.primary_concept)

        # 3. Link Lesson -> Primary Concept (COVERS, VISUALIZES)
        if primary_norm:
            link_query = """
            MATCH (l:Lesson {id: $lesson_id})
            MATCH (c:Concept {normalized_name: $primary_norm})
            MERGE (l)-[:COVERS]->(c)
            MERGE (l)-[:VISUALIZES]->(c)
            """
            with get_neo4j_session() as session:
                if session:
                    try:
                        session.run(link_query, lesson_id=str(lesson_id), primary_norm=primary_norm)
                    except Exception as e:
                        logger.warning(f"[Neo4j] Failed linking lesson to concept: {e}")

        # 4. Ingest Algorithms & Data Structures
        for algo in metadata.algorithms:
            a_norm = GraphService.create_or_get_algorithm(algo)
            if a_norm and primary_norm:
                GraphService.add_related_concept(algo, metadata.primary_concept)

        for ds in metadata.data_structures:
            d_norm = GraphService.create_or_get_data_structure(ds)
            if d_norm and metadata.algorithms:
                for algo in metadata.algorithms:
                    GraphService.add_uses_relationship(algo, ds)

        # 5. Ingest Prerequisites
        for prereq in metadata.prerequisites:
            GraphService.add_prerequisite(prereq, metadata.primary_concept)

        # 6. Ingest Related Concepts
        for rel in metadata.related_concepts:
            GraphService.add_related_concept(metadata.primary_concept, rel)

        # 7. Ingest Complexity
        for cx in metadata.complexity:
            GraphService.add_complexity_relationship(metadata.primary_concept, cx)

        logger.info(f"✅ [Neo4j] Knowledge metadata ingestion completed for lesson '{title}'.")

    @staticmethod
    def get_graph_context_for_prompt(topic: str, user_id: Optional[int] = None) -> str:
        """
        Retrieves relevant graph context (prerequisites, related concepts, complexities, user progress)
        for Gemini prompt enhancement before lesson generation.
        """
        if not is_neo4j_available():
            return ""

        norm = normalize_concept_name(topic)
        if not norm:
            return ""

        query = """
        MATCH (c {normalized_name: $norm})
        OPTIONAL MATCH (p)-[:PREREQUISITE_FOR]->(c)
        OPTIONAL MATCH (c)-[:RELATED_TO]-(r)
        OPTIONAL MATCH (c)-[:HAS_COMPLEXITY]->(cx:Complexity)
        OPTIONAL MATCH (u:User {id: $user_id})-[:COMPLETED]->(comp:Concept)
        RETURN c.name AS concept_name,
               collect(DISTINCT p.name) AS prerequisites,
               collect(DISTINCT r.name) AS related,
               collect(DISTINCT cx.notation) AS complexities,
               collect(DISTINCT comp.normalized_name) AS completed_user_concepts
        """

        with get_neo4j_session() as session:
            if not session:
                return ""
            try:
                res = session.run(query, norm=norm, user_id=user_id or 0)
                rec = res.single()
                if not rec or not rec["concept_name"]:
                    return ""

                concept_name = rec["concept_name"]
                prereqs = [p for p in rec["prerequisites"] if p]
                related = [r for r in rec["related"] if r]
                complexities = [cx for cx in rec["complexities"] if cx]
                user_comp = set(rec["completed_user_concepts"] or [])

                lines = ["GRAPH KNOWLEDGE CONTEXT (Retrieved from Persistent Graph):"]
                lines.append(f"- Primary Concept: {concept_name}")
                if prereqs:
                    prereq_str = ", ".join([f"{p} ({'completed' if normalize_concept_name(p) in user_comp else 'not completed'})" for p in prereqs])
                    lines.append(f"- Prerequisites: {prereq_str}")
                if related:
                    lines.append(f"- Related Concepts/Algorithms: {', '.join(related)}")
                if complexities:
                    lines.append(f"- Known Complexity: {', '.join(complexities)}")

                ctx_str = "\n".join(lines)
                logger.info(f"[Neo4j] Retrieved graph context for '{topic}': {len(prereqs)} prereqs, {len(related)} related.")
                return ctx_str
            except Exception as e:
                logger.warning(f"[Neo4j] Error fetching prompt graph context for '{topic}': {e}")
                return ""

    @staticmethod
    def get_learning_path(concept_name: str) -> LearningPathResponse:
        """Retrieves learning path (prerequisites, related concepts, next concepts) for a requested concept."""
        norm = normalize_concept_name(concept_name)
        if not is_neo4j_available() or not norm:
            return LearningPathResponse(concept=concept_name, normalized_name=norm)

        query = """
        MATCH (c {normalized_name: $norm})
        OPTIONAL MATCH (p)-[:PREREQUISITE_FOR]->(c)
        OPTIONAL MATCH (c)-[:RELATED_TO]-(r)
        OPTIONAL MATCH (c)-[:PREREQUISITE_FOR]->(nxt)
        RETURN c.name AS name,
               c.normalized_name AS norm,
               collect(DISTINCT p.name) AS prereqs,
               collect(DISTINCT r.name) AS related,
               collect(DISTINCT nxt.name) AS next_concepts
        """

        with get_neo4j_session() as session:
            if not session:
                return LearningPathResponse(concept=concept_name, normalized_name=norm)
            try:
                res = session.run(query, norm=norm)
                rec = res.single()
                if not rec or not rec["name"]:
                    return LearningPathResponse(concept=concept_name, normalized_name=norm)

                return LearningPathResponse(
                    concept=rec["name"],
                    normalized_name=rec["norm"],
                    prerequisites=[p for p in rec["prereqs"] if p],
                    related=[r for r in rec["related"] if r],
                    next_concepts=[n for n in rec["next_concepts"] if n]
                )
            except Exception as e:
                logger.warning(f"[Neo4j] Error getting learning path for '{concept_name}': {e}")
                return LearningPathResponse(concept=concept_name, normalized_name=norm)

    @staticmethod
    def get_related_concepts(concept_name: str) -> RelatedConceptsResponse:
        """Retrieves comprehensive related nodes (prerequisites, dependent, algorithms, data structures, complexity)."""
        norm = normalize_concept_name(concept_name)
        if not is_neo4j_available() or not norm:
            return RelatedConceptsResponse(concept=concept_name)

        query = """
        MATCH (c {normalized_name: $norm})
        OPTIONAL MATCH (p)-[:PREREQUISITE_FOR]->(c)
        OPTIONAL MATCH (c)-[:PREREQUISITE_FOR]->(dep)
        OPTIONAL MATCH (c)-[:RELATED_TO]-(r)
        OPTIONAL MATCH (a:Algorithm)-[:SOLVES|RELATED_TO]-(c)
        OPTIONAL MATCH (a)-[:USES]->(d:DataStructure)
        OPTIONAL MATCH (c)-[:HAS_COMPLEXITY]->(cx:Complexity)
        RETURN c.name AS name,
               collect(DISTINCT p.name) AS prereqs,
               collect(DISTINCT dep.name) AS dependents,
               collect(DISTINCT r.name) AS related,
               collect(DISTINCT a.name) AS algos,
               collect(DISTINCT d.name) AS dss,
               collect(DISTINCT cx.notation) AS cxs
        """

        with get_neo4j_session() as session:
            if not session:
                return RelatedConceptsResponse(concept=concept_name)
            try:
                res = session.run(query, norm=norm)
                rec = res.single()
                if not rec or not rec["name"]:
                    return RelatedConceptsResponse(concept=concept_name)

                return RelatedConceptsResponse(
                    concept=rec["name"],
                    prerequisites=[p for p in rec["prereqs"] if p],
                    dependent=[d for d in rec["dependents"] if d],
                    related=[r for r in rec["related"] if r],
                    algorithms=[a for a in rec["algos"] if a],
                    data_structures=[d for d in rec["dss"] if d],
                    complexity=[c for c in rec["cxs"] if c]
                )
            except Exception as e:
                logger.warning(f"[Neo4j] Error fetching related concepts for '{concept_name}': {e}")
                return RelatedConceptsResponse(concept=concept_name)

    @staticmethod
    def record_user_completed_concept(user_id: int, concept_name: str) -> bool:
        """Records user learning completion: (User)-[:COMPLETED]->(Concept)."""
        norm = normalize_concept_name(concept_name)
        if not is_neo4j_available() or not norm:
            return False

        GraphService.create_or_get_concept(concept_name)

        query = """
        MERGE (u:User {id: $user_id})
        WITH u
        MATCH (c {normalized_name: $norm})
        MERGE (u)-[r:COMPLETED]->(c)
        RETURN count(r) AS cnt
        """
        with get_neo4j_session() as session:
            if not session:
                return False
            try:
                session.run(query, user_id=user_id, norm=norm)
                logger.info(f"[Neo4j] Recorded user {user_id} completed concept: {concept_name}")
                return True
            except Exception as e:
                logger.warning(f"[Neo4j] Failed recording completed concept for user {user_id}: {e}")
                return False

    @staticmethod
    def get_user_recommendations(user_id: int) -> List[ConceptRecommendation]:
        """Recommends next concepts to learn based on user's completed concepts graph traversal."""
        if not is_neo4j_available():
            return []

        query = """
        MATCH (u:User {id: $user_id})-[:COMPLETED]->(completed:Concept)
        MATCH (completed)-[:PREREQUISITE_FOR]->(next_concept:Concept)
        WHERE NOT (u)-[:COMPLETED]->(next_concept)
        OPTIONAL MATCH (prereq:Concept)-[:PREREQUISITE_FOR]->(next_concept)
        WITH next_concept, collect(prereq) AS reqs, u
        WHERE ALL(r IN reqs WHERE (u)-[:COMPLETED]->(r))
        RETURN next_concept.name AS name,
               next_concept.normalized_name AS norm,
               collect(DISTINCT [r IN reqs | r.name]) AS prereqs_met
        LIMIT 10
        """

        with get_neo4j_session() as session:
            if not session:
                return []
            try:
                res = session.run(query, user_id=user_id)
                recs = []
                for row in res:
                    recs.append(ConceptRecommendation(
                        concept=row["name"],
                        normalized_name=row["norm"],
                        reason="Prerequisites satisfied by your completed lessons",
                        prerequisites_met=[p for sub in row["prereqs_met"] for p in sub if p]
                    ))
                return recs
            except Exception as e:
                logger.warning(f"[Neo4j] Error generating recommendations for user {user_id}: {e}")
                return []

    @staticmethod
    def get_subgraph_visualization(center_concept: Optional[str] = None, user_id: Optional[int] = None) -> GraphVisualizationResponse:
        """
        Retrieves graph nodes and edges representation suitable for React frontend visualization.
        """
        nodes_dict: Dict[str, GraphNode] = {}
        edges_list: List[GraphEdge] = []

        if not is_neo4j_available():
            # Return a default fallback mock graph if Neo4j is offline or disabled
            return GraphVisualizationResponse(
                nodes=[
                    GraphNode(id="array", label="Array", type="DataStructure", description="Contiguous memory array"),
                    GraphNode(id="binary_search", label="Binary Search", type="Algorithm", description="O(log n) search in sorted arrays"),
                    GraphNode(id="o_log_n", label="O(log n)", type="Complexity", notation="O(log n)")
                ],
                edges=[
                    GraphEdge(source="array", target="binary_search", type="PREREQUISITE_FOR"),
                    GraphEdge(source="binary_search", target="o_log_n", type="HAS_COMPLEXITY")
                ]
            )

        norm = normalize_concept_name(center_concept) if center_concept else None

        if norm:
            cypher = """
            MATCH (center {normalized_name: $norm})
            OPTIONAL MATCH (center)-[r]-(neighbor)
            OPTIONAL MATCH (u:User {id: $user_id})-[:COMPLETED]->(comp)
            RETURN center, r, neighbor, collect(DISTINCT comp.normalized_name) AS completed_set
            LIMIT 50
            """
        else:
            cypher = """
            MATCH (n)
            OPTIONAL MATCH (n)-[r]->(m)
            OPTIONAL MATCH (u:User {id: $user_id})-[:COMPLETED]->(comp)
            RETURN n AS center, r, m AS neighbor, collect(DISTINCT comp.normalized_name) AS completed_set
            LIMIT 100
            """

        with get_neo4j_session() as session:
            if not session:
                return GraphVisualizationResponse(nodes=[], edges=[])
            try:
                res = session.run(cypher, norm=norm, user_id=user_id or 0)
                user_comp_set = set()

                for record in res:
                    c_node = record.get("center")
                    r_rel = record.get("r")
                    n_node = record.get("neighbor")
                    comp_list = record.get("completed_set") or []
                    user_comp_set.update(comp_list)

                    def extract_node(node) -> Optional[GraphNode]:
                        if not node:
                            return None
                        labels = list(node.labels) if hasattr(node, 'labels') else ["Concept"]
                        node_type = labels[0] if labels else "Concept"
                        props = dict(node)
                        node_id = props.get("normalized_name") or props.get("notation") or props.get("id") or str(node.element_id)
                        label = props.get("name") or props.get("title") or props.get("notation") or node_id
                        desc = props.get("description")
                        cat = props.get("category")
                        notation = props.get("notation")
                        is_completed = node_id in user_comp_set

                        return GraphNode(
                            id=node_id,
                            label=label,
                            type=node_type,
                            description=desc,
                            category=cat,
                            notation=notation,
                            completed=is_completed
                        )

                    c_obj = extract_node(c_node)
                    if c_obj and c_obj.id not in nodes_dict:
                        nodes_dict[c_obj.id] = c_obj

                    n_obj = extract_node(n_node)
                    if n_obj and n_obj.id not in nodes_dict:
                        nodes_dict[n_obj.id] = n_obj

                    if r_rel and c_obj and n_obj:
                        rel_type = r_rel.type if hasattr(r_rel, 'type') else "RELATED_TO"
                        src_id = c_obj.id if r_rel.start_node == c_node else n_obj.id
                        tgt_id = n_obj.id if r_rel.start_node == c_node else c_obj.id
                        edges_list.append(GraphEdge(source=src_id, target=tgt_id, type=rel_type))

                return GraphVisualizationResponse(
                    nodes=list(nodes_dict.values()),
                    edges=edges_list
                )
            except Exception as e:
                logger.warning(f"[Neo4j] Error retrieving subgraph visualization: {e}")
                return GraphVisualizationResponse(nodes=[], edges=[])
