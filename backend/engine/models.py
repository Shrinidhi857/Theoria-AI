import os
from enum import Enum
from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field

# ── Model Cascade Configuration ───────────────────────────────────────────────
_DEFAULT_CASCADE = "gemini-2.0-flash,gemini-1.5-flash,gemini-flash-latest"
GEMINI_MODEL_CASCADE: List[str] = [
    m.strip()
    for m in os.getenv("GEMINI_MODELS", _DEFAULT_CASCADE).split(",")
    if m.strip()
]


class ObjectType(str, Enum):
    CIRCLE = "circle"
    SQUARE = "square"
    ARROW = "arrow"
    TEXT = "text"
    ARRAY = "array"
    POINTER = "pointer"


class AnimationType(str, Enum):
    HIGHLIGHT = "Highlight"
    MOVE = "Move"
    TRANSFORM = "Transform"
    FADE_IN = "FadeIn"
    FADE_OUT = "FadeOut"
    WRITE = "Write"
    WAIT = "Wait"
    MOVE_POINTER = "MovePointer"


class DSLObject(BaseModel):
    id: str = Field(..., description="Unique identifier for the object")
    type: str = Field(..., description="Type of object (circle, square, arrow, text, array, pointer)")
    values: Optional[List[Union[int, float, str]]] = Field(default=None, description="Array values if type is array")
    text: Optional[str] = Field(default=None, description="Text string if type is text")
    color: Optional[str] = Field(default="WHITE", description="Color of object (e.g. BLUE, RED, GREEN, YELLOW)")
    position: Optional[List[float]] = Field(default=[0.0, 0.0, 0.0], description="[x, y, z] coordinate position")
    radius: Optional[float] = Field(default=1.0, description="Radius if object is a circle")
    side_length: Optional[float] = Field(default=1.0, description="Side length if object is a square")
    label: Optional[str] = Field(default=None, description="Optional text label")


class DSLAnimation(BaseModel):
    type: str = Field(..., description="Animation type (Highlight, Move, Transform, FadeIn, FadeOut, Write, Wait, MovePointer)")
    target: Optional[str] = Field(default=None, description="Target object ID for single-object animations")
    pointer: Optional[str] = Field(default=None, description="Pointer object ID or label for MovePointer")
    to: Optional[Union[int, float, List[float]]] = Field(default=None, description="Target index or coordinate for Move/MovePointer")
    index: Optional[int] = Field(default=None, description="Array element index for Highlight")
    duration: Optional[float] = Field(default=1.0, description="Animation duration in seconds")
    color: Optional[str] = Field(default="YELLOW", description="Highlight or color override")
    position: Optional[List[float]] = Field(default=None, description="Target position for Move animation")
    transform_to: Optional[str] = Field(default=None, description="Target object ID for Transform animation")


class SceneDSL(BaseModel):
    scene_title: str = Field(..., description="Title of the scene")
    objects: List[DSLObject] = Field(default_factory=list, description="List of objects in the scene")
    animations: List[DSLAnimation] = Field(default_factory=list, description="Sequence of animations")
    voice: str = Field(default="", description="Narration text spoken during the scene")


class ExtractedParameters(BaseModel):
    algorithm_or_topic: str = Field(default="Binary Search", description="Extracted algorithm or core topic")
    input_data: Optional[List[Union[int, float, str]]] = Field(default=None, description="Extracted input array or dataset if provided")
    target_value: Optional[Union[int, float, str]] = Field(default=None, description="Extracted target or goal value if provided")
    problem_type: str = Field(default="Algorithmic Explanation", description="Conceptual / Problem Walkthrough / LeetCode style")


class ProblemApproach(BaseModel):
    problem_understanding: str = Field(..., description="Deep breakdown of what the question is asking")
    naive_vs_optimal: str = Field(..., description="Comparison of brute-force vs optimal algorithm")
    step_by_step_execution: List[str] = Field(default_factory=list, description="Step-by-step state changes for the sample input")
    time_and_space_complexity: str = Field(..., description="Time and space complexity explanation")


class KnowledgeMetadata(BaseModel):
    primary_concept: str = Field(default="Computer Science Concept", description="Main concept taught in lesson")
    concepts: List[str] = Field(default_factory=list, description="General concepts involved in lesson")
    algorithms: List[str] = Field(default_factory=list, description="Specific algorithms demonstrated")
    data_structures: List[str] = Field(default_factory=list, description="Data structures used or explained")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisite concepts needed before this lesson")
    related_concepts: List[str] = Field(default_factory=list, description="Related algorithms or concepts")
    complexity: List[str] = Field(default_factory=list, description="Time and space complexity notations (e.g. O(log n))")


class LessonPlan(BaseModel):
    topic: str
    extracted_parameters: ExtractedParameters
    approach: ProblemApproach
    overview: str
    learning_objectives: List[str]
    presentation_script_outline: List[str]
    knowledge_metadata: Optional[KnowledgeMetadata] = None



class ScenePlan(BaseModel):
    scene_number: int
    title: str
    phase: str = Field(default="Explanation", description="Hook / Problem Setup / Approach Walkthrough / Conclusion")
    explanation: str
    visual_description: str
    voiceover_script: str


class PipelineResult(BaseModel):
    video: str
    topic: str
    extracted_parameters: Optional[ExtractedParameters] = None
    approach: Optional[ProblemApproach] = None
    scene_title: Optional[str] = None
    manim_code: Optional[str] = None
    narration_audio: Optional[str] = None
    status: str = "success"
    error: Optional[str] = None


# ── Multi-Agent Evolution Schemas (v2) ────────────────────────────────────────

class RenderError(BaseModel):
    kind: str = Field(default="unknown", description="syntax, manim_api_misuse, geometry_out_of_bounds, timeout, missing_asset, unknown")
    raw_stderr: str = Field(default="", description="Compiler stderr traceback output")
    suspected_source: str = Field(default="code_generator", description="code_generator, dsl, or renderer_env")


class RepairTranscript(BaseModel):
    scene_number: int
    attempt: int
    dsl_snapshot: SceneDSL
    code_before: str
    error: RenderError
    code_after: Optional[str] = None
    outcome: str = Field(default="repair_attempted", description="success, repair_attempted, budget_exhausted")
    timestamp: str = ""


class VisualIssue(BaseModel):
    description: str
    likely_cause: str = Field(default="code_gen", description="dsl, code_gen, or renderer")
    suggested_fix: str
    severity: str = Field(default="cosmetic", description="blocking or cosmetic")


class VisualQAReport(BaseModel):
    scene_number: int
    passed: bool
    issues: List[VisualIssue] = Field(default_factory=list)


class StyleGuide(BaseModel):
    palette: Dict[str, str] = Field(
        default_factory=lambda: {
            "background": "#121212",
            "primary": "BLUE",
            "accent": "YELLOW",
            "highlight": "GREEN",
            "text": "WHITE"
        }
    )
    font_scale: float = Field(default=1.0)
    camera_margin: float = Field(default=0.5)
    pointer_color: str = Field(default="YELLOW")
    highlight_color: str = Field(default="GREEN")


class PedagogicalScore(BaseModel):
    clarity: int = Field(default=5, ge=1, le=5)
    accuracy: int = Field(default=5, ge=1, le=5)
    pacing: int = Field(default=5, ge=1, le=5)
    engagement: int = Field(default=5, ge=1, le=5)
    weakest_scene: Optional[int] = None
    notes: str = ""

