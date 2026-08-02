from typing import Dict, Any, List, Set
from engine.models import SceneDSL, DSLObject, DSLAnimation, ObjectType, AnimationType


class DSLValidationError(Exception):
    """Custom exception raised when an Animation DSL fails validation."""
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or [message]


class DSLValidator:
    """Validates Animation DSL JSON data structures for correctness and safety."""

    ALLOWED_OBJECT_TYPES = {t.value for t in ObjectType}
    ALLOWED_ANIMATION_TYPES = {a.value for a in AnimationType}

    def validate(self, dsl: SceneDSL) -> bool:
        """
        Validates a SceneDSL instance.
        Raises DSLValidationError if any validation check fails.
        Returns True if valid.
        """
        errors = []
        object_ids: Set[str] = set()
        array_lengths: Dict[str, int] = {}

        if not dsl.scene_title or not isinstance(dsl.scene_title, str):
            errors.append("Scene title is missing or invalid.")

        # 1. Validate Objects
        for idx, obj in enumerate(dsl.objects):
            if not obj.id or not isinstance(obj.id, str):
                errors.append(f"Object at index {idx} is missing a valid 'id'.")
            elif obj.id in object_ids:
                errors.append(f"Duplicate object ID detected: '{obj.id}'.")
            else:
                object_ids.add(obj.id)

            if not obj.type or obj.type.lower() not in self.ALLOWED_OBJECT_TYPES:
                errors.append(
                    f"Unknown object type '{obj.type}' for object ID '{obj.id}'. "
                    f"Allowed types: {sorted(list(self.ALLOWED_OBJECT_TYPES))}"
                )

            if obj.type.lower() == ObjectType.ARRAY.value:
                if obj.values is None or not isinstance(obj.values, list):
                    errors.append(f"Array object '{obj.id}' must provide a list of 'values'.")
                else:
                    array_lengths[obj.id] = len(obj.values)

        # 2. Validate Animations
        for idx, anim in enumerate(dsl.animations):
            if not anim.type or anim.type not in self.ALLOWED_ANIMATION_TYPES:
                errors.append(
                    f"Unknown animation type '{anim.type}' at animation index {idx}. "
                    f"Allowed animations: {sorted(list(self.ALLOWED_ANIMATION_TYPES))}"
                )
                continue

            # Check for negative duration
            if anim.duration is not None and anim.duration < 0:
                errors.append(f"Animation '{anim.type}' at index {idx} has negative duration: {anim.duration}")

            # Check target object reference
            if anim.type in [
                AnimationType.HIGHLIGHT.value,
                AnimationType.MOVE.value,
                AnimationType.FADE_IN.value,
                AnimationType.FADE_OUT.value,
                AnimationType.WRITE.value,
            ]:
                if not anim.target:
                    errors.append(f"Animation '{anim.type}' at index {idx} requires a 'target' object ID.")
                elif anim.target not in object_ids:
                    errors.append(f"Animation '{anim.type}' references unknown target ID: '{anim.target}'.")

            # Check Transform references
            if anim.type == AnimationType.TRANSFORM.value:
                if not anim.target or anim.target not in object_ids:
                    errors.append(f"Transform animation at index {idx} references unknown source target: '{anim.target}'.")
                if not anim.transform_to or anim.transform_to not in object_ids:
                    errors.append(f"Transform animation at index {idx} references unknown transform_to target: '{anim.transform_to}'.")

            # Check MovePointer references
            if anim.type == AnimationType.MOVE_POINTER.value:
                if anim.pointer and anim.pointer not in object_ids:
                    errors.append(f"MovePointer animation at index {idx} references unknown pointer ID: '{anim.pointer}'.")

            # Check array index bounds for Highlight
            if anim.type == AnimationType.HIGHLIGHT.value and anim.target in array_lengths:
                arr_len = array_lengths[anim.target]
                if anim.index is not None:
                    if anim.index < 0 or anim.index >= arr_len:
                        errors.append(
                            f"Highlight index {anim.index} out of bounds for array '{anim.target}' (length {arr_len})."
                        )

        if errors:
            raise DSLValidationError(
                f"DSL Validation Failed with {len(errors)} error(s):\n" + "\n".join(f"- {e}" for e in errors),
                errors=errors,
            )

        return True
