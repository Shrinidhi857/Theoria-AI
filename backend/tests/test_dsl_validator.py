import pytest
from engine.models import SceneDSL, DSLObject, DSLAnimation
from engine.dsl_validator import DSLValidator, DSLValidationError


def test_valid_dsl():
    validator = DSLValidator()
    dsl = SceneDSL(
        scene_title="Binary Search",
        objects=[
            DSLObject(id="array1", type="array", values=[2, 5, 8, 10, 15]),
            DSLObject(id="mid", type="pointer", label="mid", position=[0, -1, 0])
        ],
        animations=[
            DSLAnimation(type="FadeIn", target="array1"),
            DSLAnimation(type="Highlight", target="array1", index=2),
            DSLAnimation(type="MovePointer", pointer="mid", to=2)
        ],
        voice="Binary Search begins by checking the middle element."
    )
    assert validator.validate(dsl) is True


def test_unknown_object_type():
    validator = DSLValidator()
    dsl = SceneDSL(
        scene_title="Test Unknown Object",
        objects=[DSLObject(id="obj1", type="hypercube")],
        animations=[],
        voice=""
    )
    with pytest.raises(DSLValidationError) as excinfo:
        validator.validate(dsl)
    assert "Unknown object type 'hypercube'" in str(excinfo.value)


def test_unknown_animation_type():
    validator = DSLValidator()
    dsl = SceneDSL(
        scene_title="Test Unknown Animation",
        objects=[DSLObject(id="arr1", type="array", values=[1, 2])],
        animations=[DSLAnimation(type="SpinAndExplode", target="arr1")],
        voice=""
    )
    with pytest.raises(DSLValidationError) as excinfo:
        validator.validate(dsl)
    assert "Unknown animation type 'SpinAndExplode'" in str(excinfo.value)


def test_duplicate_object_ids():
    validator = DSLValidator()
    dsl = SceneDSL(
        scene_title="Duplicate IDs",
        objects=[
            DSLObject(id="box", type="square"),
            DSLObject(id="box", type="circle")
        ],
        animations=[],
        voice=""
    )
    with pytest.raises(DSLValidationError) as excinfo:
        validator.validate(dsl)
    assert "Duplicate object ID detected: 'box'" in str(excinfo.value)


def test_invalid_target_reference():
    validator = DSLValidator()
    dsl = SceneDSL(
        scene_title="Invalid Reference",
        objects=[DSLObject(id="sq", type="square")],
        animations=[DSLAnimation(type="FadeIn", target="non_existent_id")],
        voice=""
    )
    with pytest.raises(DSLValidationError) as excinfo:
        validator.validate(dsl)
    assert "references unknown target ID: 'non_existent_id'" in str(excinfo.value)


def test_negative_duration():
    validator = DSLValidator()
    dsl = SceneDSL(
        scene_title="Negative Duration",
        objects=[DSLObject(id="sq", type="square")],
        animations=[DSLAnimation(type="FadeIn", target="sq", duration=-2.5)],
        voice=""
    )
    with pytest.raises(DSLValidationError) as excinfo:
        validator.validate(dsl)
    assert "negative duration" in str(excinfo.value)


def test_array_index_out_of_bounds():
    validator = DSLValidator()
    dsl = SceneDSL(
        scene_title="Index Out of Bounds",
        objects=[DSLObject(id="arr1", type="array", values=[10, 20, 30])],
        animations=[DSLAnimation(type="Highlight", target="arr1", index=5)],
        voice=""
    )
    with pytest.raises(DSLValidationError) as excinfo:
        validator.validate(dsl)
    assert "Highlight index 5 out of bounds" in str(excinfo.value)
