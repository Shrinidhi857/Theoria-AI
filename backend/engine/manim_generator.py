from typing import List, Dict, Any
from engine.models import SceneDSL, DSLObject, DSLAnimation, ObjectType, AnimationType


class ManimCodeGenerator:
    """Converts a validated SceneDSL object into executable Python Manim script code."""

    def generate_code(self, dsl: SceneDSL, scene_class_name: str = "GeneratedScene") -> str:
        """
        Generates Python Manim code from SceneDSL.
        """
        lines: List[str] = [
            "# Auto-generated Manim Code from Animation DSL",
            "from manim import *",
            "",
            f"class {scene_class_name}(Scene):",
            "    def construct(self):",
            "        # Color Mapping Helper",
            "        color_map = {",
            "            'BLUE': BLUE, 'RED': RED, 'GREEN': GREEN, 'YELLOW': YELLOW,",
            "            'WHITE': WHITE, 'ORANGE': ORANGE, 'PURPLE': PURPLE, 'TEAL': TEAL",
            "        }",
            "",
            "        objects = {}",
            "        array_elements = {}",
            "",
        ]

        # 1. Generate object instantiation code
        lines.append("        # Initialize Objects")
        for obj in dsl.objects:
            obj_type = obj.type.lower()
            pos = obj.position or [0.0, 0.0, 0.0]
            color_str = obj.color.upper() if obj.color else "WHITE"

            if obj_type == ObjectType.CIRCLE.value:
                rad = obj.radius or 1.0
                lines.append(
                    f"        objects['{obj.id}'] = Circle(radius={rad}, color=color_map.get('{color_str}', WHITE))"
                    f".move_to([{pos[0]}, {pos[1]}, {pos[2]}])"
                )

            elif obj_type == ObjectType.SQUARE.value:
                side = obj.side_length or 1.0
                lines.append(
                    f"        objects['{obj.id}'] = Square(side_length={side}, color=color_map.get('{color_str}', WHITE))"
                    f".move_to([{pos[0]}, {pos[1]}, {pos[2]}])"
                )

            elif obj_type == ObjectType.TEXT.value:
                txt = obj.text or obj.id
                lines.append(
                    f"        objects['{obj.id}'] = Text('{txt}', color=color_map.get('{color_str}', WHITE))"
                    f".move_to([{pos[0]}, {pos[1]}, {pos[2]}])"
                )

            elif obj_type == ObjectType.ARROW.value:
                lines.append(
                    f"        objects['{obj.id}'] = Arrow(start=[{pos[0]}, {pos[1]}+1, {pos[2]}], end=[{pos[0]}, {pos[1]}, {pos[2]}], color=color_map.get('{color_str}', WHITE))"
                )

            elif obj_type == ObjectType.POINTER.value:
                lbl = obj.label or "ptr"
                lines.append(
                    f"        ptr_arrow = Arrow(start=[0, -0.8, 0], end=[0, -0.1, 0], color=color_map.get('{color_str}', YELLOW), buff=0.1)"
                )
                lines.append(
                    f"        ptr_txt = Text('{lbl}', font_size=20, color=color_map.get('{color_str}', YELLOW)).next_to(ptr_arrow, DOWN, buff=0.1)"
                )
                lines.append(
                    f"        objects['{obj.id}'] = VGroup(ptr_arrow, ptr_txt).move_to([{pos[0]}, {pos[1]}, {pos[2]}])"
                )

            elif obj_type == ObjectType.ARRAY.value:
                vals = obj.values or []
                lines.append(f"        # Create Array '{obj.id}'")
                lines.append(f"        arr_vgroup = VGroup()")
                lines.append(f"        array_elements['{obj.id}'] = []")
                lines.append(f"        for i, val in enumerate({vals}):")
                lines.append(
                    f"            sq = Square(side_length=1.0, color=color_map.get('{color_str}', BLUE))"
                )
                lines.append(f"            txt = Text(str(val), font_size=24)")
                lines.append(f"            cell = VGroup(sq, txt)")
                lines.append(f"            if i > 0:")
                lines.append(f"                cell.next_to(arr_vgroup[-1], RIGHT, buff=0.0)")
                lines.append(f"            arr_vgroup.add(cell)")
                lines.append(f"            array_elements['{obj.id}'].append(cell)")
                lines.append(f"        arr_vgroup.move_to([{pos[0]}, {pos[1]}, {pos[2]}])")
                lines.append(f"        objects['{obj.id}'] = arr_vgroup")

        lines.append("")
        lines.append("        # Execute Animations")

        # 2. Generate animation code
        for anim in dsl.animations:
            anim_type = anim.type
            dur = anim.duration or 1.0
            col = anim.color.upper() if anim.color else "YELLOW"

            if anim_type == AnimationType.FADE_IN.value:
                lines.append(f"        self.play(FadeIn(objects['{anim.target}']), run_time={dur})")

            elif anim_type == AnimationType.FADE_OUT.value:
                lines.append(f"        self.play(FadeOut(objects['{anim.target}']), run_time={dur})")

            elif anim_type == AnimationType.WRITE.value:
                lines.append(f"        self.play(Write(objects['{anim.target}']), run_time={dur})")

            elif anim_type == AnimationType.WAIT.value:
                lines.append(f"        self.wait({dur})")

            elif anim_type == AnimationType.MOVE.value:
                target_pos = anim.position or [0.0, 0.0, 0.0]
                lines.append(
                    f"        self.play(objects['{anim.target}'].animate.move_to([{target_pos[0]}, {target_pos[1]}, {target_pos[2]}]), run_time={dur})"
                )

            elif anim_type == AnimationType.TRANSFORM.value:
                lines.append(
                    f"        self.play(Transform(objects['{anim.target}'], objects['{anim.transform_to}']), run_time={dur})"
                )

            elif anim_type == AnimationType.HIGHLIGHT.value:
                if anim.target in [o.id for o in dsl.objects if o.type == ObjectType.ARRAY.value] and anim.index is not None:
                    lines.append(
                        f"        self.play(Indicate(array_elements['{anim.target}'][{anim.index}], color=color_map.get('{col}', YELLOW)), run_time={dur})"
                    )
                else:
                    lines.append(
                        f"        self.play(Indicate(objects['{anim.target}'], color=color_map.get('{col}', YELLOW)), run_time={dur})"
                    )

            elif anim_type == AnimationType.MOVE_POINTER.value:
                ptr_id = anim.pointer or anim.target
                if isinstance(anim.to, int):
                    # Move pointer to array element index
                    lines.append(
                        f"        target_cell = array_elements['array1'][{anim.to}] if 'array1' in array_elements else objects['{ptr_id}']"
                    )
                    lines.append(
                        f"        self.play(objects['{ptr_id}'].animate.next_to(target_cell, DOWN, buff=0.3), run_time={dur})"
                    )
                elif isinstance(anim.to, list):
                    lines.append(
                        f"        self.play(objects['{ptr_id}'].animate.move_to([{anim.to[0]}, {anim.to[1]}, {anim.to[2]}]), run_time={dur})"
                    )

        lines.append("        self.wait(1)")
        return "\n".join(lines)
