import { apiFetch } from "@/services/api";

export interface GraphNode {
  id: string;
  label: string;
  type: string; // Concept, Algorithm, DataStructure, Complexity, Lesson
  description?: string;
  category?: string;
  notation?: string;
  completed?: boolean;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string; // PREREQUISITE_FOR, RELATED_TO, USES, SOLVES, HAS_COMPLEXITY, COVERS, VISUALIZES
}

export interface GraphVisualizationResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface LearningPathResponse {
  concept: string;
  normalized_name: string;
  prerequisites: string[];
  related: string[];
  next_concepts: string[];
}

export interface RelatedConceptsResponse {
  concept: string;
  prerequisites: string[];
  dependent: string[];
  related: string[];
  algorithms: string[];
  data_structures: string[];
  complexity: string[];
}

export interface ConceptRecommendation {
  concept: string;
  normalized_name: string;
  reason: string;
  prerequisites_met: string[];
}

export async function getGraphVisualization(centerConcept?: string): Promise<GraphVisualizationResponse> {
  const query = centerConcept ? `?center_concept=${encodeURIComponent(centerConcept)}` : "";
  return apiFetch<GraphVisualizationResponse>(`/graph/visualization${query}`, { requiresAuth: false });
}

export async function getLearningPath(concept: string): Promise<LearningPathResponse> {
  return apiFetch<LearningPathResponse>(`/graph/learning-path/${encodeURIComponent(concept)}`, { requiresAuth: false });
}

export async function getRelatedConcepts(concept: string): Promise<RelatedConceptsResponse> {
  return apiFetch<RelatedConceptsResponse>(`/graph/concepts/${encodeURIComponent(concept)}/related`, { requiresAuth: false });
}

export async function getUserRecommendations(): Promise<ConceptRecommendation[]> {
  return apiFetch<ConceptRecommendation[]>("/graph/recommendations", { requiresAuth: true });
}

export async function markConceptCompleted(concept: string): Promise<{ status: string; message: string }> {
  return apiFetch<{ status: string; message: string }>(`/graph/concepts/${encodeURIComponent(concept)}/complete`, {
    method: "POST",
    requiresAuth: true,
  });
}
