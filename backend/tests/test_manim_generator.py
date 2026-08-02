from engine.models import SceneDSL, DSLObject, DSLAnimation
from engine.manim_generator import ManimCodeGenerator


def test_manim_code_generation():
    generator = ManimCodeGenerator()
    dsl = SceneDSL(
        scene_title="Binary Search",
        objects=[
            DSLObject(id="array1", type="array", values=[2, 5, 8, 10, 15]),
            DSLObject(id="mid_ptr", type="pointer", label="mid", position=[0, -1, 0])
        ],
        animations=[
            DSLAnimation(type="FadeIn", target="array1"),
            DSLAnimation(type="Highlight", target="array1", index=2),
            DSLAnimation(type="MovePointer", pointer="mid_ptr", to=2)
        ],
        voice="Checking middle element."
    )

    code = generator.generate_code(dsl)

    assert "from manim import *" in code
    assert "class GeneratedScene(Scene):" in code
    assert "objects['array1']" in code
    assert "objects['mid_ptr']" in code
    assert "Indicate(" in code
    assert "FadeIn(" in code
