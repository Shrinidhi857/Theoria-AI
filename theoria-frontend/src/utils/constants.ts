// Using a relative URL so the Vite dev proxy forwards /api/v1 -> http://localhost:8000
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api/v1"
export const BACKEND_SERVER_URL = import.meta.env.VITE_BACKEND_SERVER_URL || ""

export const SAMPLE_PROMPTS = [
  "Explain Binary Search with an array [2, 5, 8, 12, 16, 23, 38, 56, 72] and target 23",
  "Visualize Bubble Sort step by step",
  "How Linked List Reversal works intuitively",
  "Demonstrate Depth First Search (DFS) on a binary tree",
  "Explain Two Pointer Technique for palindromes"
];

export const PIPELINE_STEPS = [
  { id: 1, label: "Parameter Extraction", desc: "Parsing topic & input dataset" },
  { id: 2, label: "Problem Thinking", desc: "Analyzing naive vs optimal strategy" },
  { id: 3, label: "Scene & Animation DSL", desc: "Generating visual layout & script" },
  { id: 4, label: "Manim Code & Render", desc: "Compiling math animations to MP4" },
  { id: 5, label: "Voice Narration & Merge", desc: "Generating TTS audio & final mux" }
];
