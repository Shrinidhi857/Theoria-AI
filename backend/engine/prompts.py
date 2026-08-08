"""
Reusable prompt templates for Gemini API stages.
Includes detailed problem analysis, parameter extraction, approach reasoning, and Animation DSL generation.
"""

import os

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

LESSON_PLANNER_PROMPT = """You are an elite Computer Science Educator and Algorithm Architect.
Analyze the following teaching request or LeetCode-style problem:

User Request: "{topic}"

{graph_context}

YOUR TASK:
1. Extract or infer concrete problem parameters:
   - Identify the algorithm/topic (e.g. "Binary Search", "Merge Sort", "Dijkstra's Algorithm").
   - Extract any provided sample input array/dataset (e.g. [1, 3, 5, 7, 9]) or infer a clear, simple realistic array if none given.
   - Extract any target/search value (e.g. 7) or infer a suitable target if none given.
   - Classify the problem type ("Algorithmic Walkthrough", "LeetCode Problem", "Conceptual Explanation").

2. Formulate a Detailed Problem & Solution Approach (Thinking Phase):
   - Problem Understanding: What is being asked?
   - Naive vs Optimal Approach: Why use this algorithm over brute force?
   - Step-by-step Execution: Trace every iteration/step on the concrete sample input with low, mid, high pointers or state variables.
   - Time & Space Complexity: O(...) analysis.

3. Extract Educational Knowledge Metadata for Global Knowledge Graph:
   - primary_concept: Main core concept/algorithm
   - concepts: List of computer science concepts involved
   - algorithms: List of specific algorithms mentioned or used
   - data_structures: List of data structures used (e.g. Array, Priority Queue, Graph)
   - prerequisites: Prerequisite concepts needed before this lesson
   - related_concepts: Related algorithms or concepts
   - complexity: Complexity notations e.g. ["O(log n)", "O(1)"]

4. Create a Structured Presentation Script Outline:
   - Scene 1: Hook & Problem Definition (show input array and target).
   - Scene 2: Algorithm Strategy & Pointer Setup.
   - Scene 3: Step-by-step Trace / State Transitions.
   - Scene 4: Conclusion & Complexity Takeaways.

Return a STRICT JSON object conforming to this schema:
{{
  "topic": "{topic}",
  "extracted_parameters": {{
    "algorithm_or_topic": "Binary Search",
    "input_data": [1, 3, 5, 7, 9],
    "target_value": 7,
    "problem_type": "LeetCode / Algorithmic Walkthrough"
  }},
  "approach": {{
    "problem_understanding": "Search for target 7 in sorted array [1, 3, 5, 7, 9] using Binary Search.",
    "naive_vs_optimal": "Linear search takes O(n) time. Binary search reduces search space by half each step, taking O(log n) time.",
    "step_by_step_execution": [
      "Step 1: low=0 (val 1), high=4 (val 9), mid=2 (val 5). Since 5 < 7, move low to mid+1 (index 3).",
      "Step 2: low=3 (val 7), high=4 (val 9), mid=3 (val 7). Since array[3] == 7, target is found at index 3!"
    ],
    "time_and_space_complexity": "Time Complexity: O(log n), Space Complexity: O(1)."
  }},
  "overview": "Comprehensive visual breakdown of Binary Search running on array [1, 3, 5, 7, 9] targeting 7.",
  "learning_objectives": [
    "Understand how pointers (low, mid, high) divide search space.",
    "Trace state changes step-by-step to find target 7."
  ],
  "presentation_script_outline": [
    "Introduce problem: find 7 in sorted array [1, 3, 5, 7, 9]",
    "Initialize low=0, high=4, compute mid=2 (value 5)",
    "Compare 5 with target 7 and shift low pointer to index 3",
    "Compute mid=3 (value 7), match target, return index 3"
  ],
  "knowledge_metadata": {{
    "primary_concept": "Binary Search",
    "concepts": ["Searching", "Divide and Conquer"],
    "algorithms": ["Binary Search"],
    "data_structures": ["Array"],
    "prerequisites": ["Array", "Sorting"],
    "related_concepts": ["Linear Search", "Two Pointer"],
    "complexity": ["O(log n)", "O(1)"]
  }}
}}

Output STRICTLY valid JSON without markdown formatting or introductory text.
"""


SCENE_PLANNER_PROMPT = """You are a visual scene director for educational computer science animations.
Given the following Lesson Plan and Problem Approach, break it down into sequential visual presentation scenes for Manim animation.

Lesson Plan:
Topic: {topic}
Extracted Parameters: {extracted_parameters}
Problem Approach: {approach}
Presentation Outline: {presentation_script_outline}

YOUR TASK:
Create a JSON list of detailed visual scenes:
- Ensure the concrete sample input array (e.g. [1, 3, 5, 7, 9]) and target (e.g. 7) are prominently featured.
- Include explicit visual descriptions (arrays, pointer arrows, highlighted elements, text annotations).
- Include complete, natural voiceover scripts for voice synthesis.

Return a STRICT JSON list with this schema:
[
  {{
    "scene_number": 1,
    "title": "Problem Setup & Goal",
    "phase": "Problem Setup",
    "explanation": "Display the input array [1, 3, 5, 7, 9] and target 7.",
    "visual_description": "Display array [1, 3, 5, 7, 9] centered. Show text label 'Target: 7' above array.",
    "voiceover_script": "We are given a sorted array 1, 3, 5, 7, 9 and want to search for target value 7 using Binary Search."
  }},
  {{
    "scene_number": 2,
    "title": "Step-by-Step Search Execution",
    "phase": "Approach Walkthrough",
    "explanation": "Initialize pointers low=0, high=4, mid=2. Value 5 is smaller than 7, so move low pointer to index 3.",
    "visual_description": "Show pointers 'low' at index 0, 'high' at index 4, 'mid' at index 2. Highlight index 2 value 5 in yellow. Move pointer to index 3.",
    "voiceover_script": "We set low at index 0 and high at index 4. The middle index is 2 with value 5. Since 5 is less than 7, we search the right half by moving low to index 3."
  }},
  {{
    "scene_number": 3,
    "title": "Target Match & Conclusion",
    "phase": "Conclusion",
    "explanation": "Compute mid=3. Value at index 3 is 7, matching target. Return index 3.",
    "visual_description": "Move mid pointer to index 3. Highlight element 7 in green. Show text 'Target 7 Found at Index 3!'.",
    "voiceover_script": "Now mid points to index 3 with value 7. We found our target! Binary search completes in just 2 steps with O(log n) time complexity."
  }}
]

Output STRICTLY valid JSON without markdown backticks or commentary.
"""

ANIMATION_PLANNER_PROMPT = """You are an Animation DSL Generator for Manim animations.
Convert the visual scene description and voiceover into a strict Animation DSL JSON.

Scene Info:
Title: {title}
Phase: {phase}
Explanation: {explanation}
Visual Description: {visual_description}
Voiceover Script: {voiceover_script}

ALLOWED OBJECT TYPES:
- circle (fields: id, type="circle", radius, color, position)
- square (fields: id, type="square", side_length, color, position)
- arrow (fields: id, type="arrow", color, position)
- text (fields: id, type="text", text, color, position)
- array (fields: id, type="array", values=[...], color, position)
- pointer (fields: id, type="pointer", label, color, position)

ALLOWED ANIMATION TYPES:
- Highlight (target: object_id, index: integer_for_array, color: color_str, duration: float)
- Move (target: object_id, position: [x, y, z], duration: float)
- Transform (target: source_object_id, transform_to: target_object_id, duration: float)
- FadeIn (target: object_id, duration: float)
- FadeOut (target: object_id, duration: float)
- Write (target: object_id, duration: float)
- Wait (duration: float)
- MovePointer (pointer: pointer_id, to: index_or_position, duration: float)

Return a STRICT JSON object matching this schema:
{{
  "scene_title": "{title}",
  "objects": [
    {{
      "id": "target_txt",
      "type": "text",
      "text": "Target: 7",
      "color": "GREEN",
      "position": [0.0, 2.0, 0.0]
    }},
    {{
      "id": "array1",
      "type": "array",
      "values": [1, 3, 5, 7, 9],
      "position": [0.0, 0.5, 0.0],
      "color": "BLUE"
    }},
    {{
      "id": "mid_ptr",
      "type": "pointer",
      "label": "mid",
      "position": [0.0, -1.2, 0.0],
      "color": "YELLOW"
    }}
  ],
  "animations": [
    {{
      "type": "FadeIn",
      "target": "target_txt",
      "duration": 0.8
    }},
    {{
      "type": "FadeIn",
      "target": "array1",
      "duration": 1.0
    }},
    {{
      "type": "FadeIn",
      "target": "mid_ptr",
      "duration": 0.8
    }},
    {{
      "type": "Highlight",
      "target": "array1",
      "index": 2,
      "color": "YELLOW",
      "duration": 1.2
    }},
    {{
      "type": "MovePointer",
      "pointer": "mid_ptr",
      "to": 3,
      "duration": 1.0
    }},
    {{
      "type": "Highlight",
      "target": "array1",
      "index": 3,
      "color": "GREEN",
      "duration": 1.5
    }},
    {{
      "type": "Wait",
      "duration": 1.0
    }}
  ],
  "voice": "{voiceover_script}"
}}

Output STRICTLY raw JSON without markdown backticks or commentary.
"""
