from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


_UTILS_PATH = Path(__file__).parents[1] / "VLABench" / "evaluation" / "utils.py"
_SPEC = spec_from_file_location("vlabench_evaluation_utils", _UTILS_PATH)
utils = module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(utils)


def test_get_final_score_includes_all_weighted_metrics(monkeypatch):
    monkeypatch.setattr(
        utils,
        "calculate_skill_and_entity_scores",
        lambda standard, model: {"skill_match_score": 100.0, "entity_match_score": 0.0},
    )
    monkeypatch.setattr(
        utils,
        "calculate_skill_with_entity_scores",
        lambda standard, model: {"skill_with_entity_match_score": 50.0},
    )
    monkeypatch.setattr(utils, "get_exact_match", lambda standard, model, dependency: 0.0)

    result = utils.get_final_score([], [], "Sequential")

    assert result["skill_match_score"] == 100.0
    assert result["entity_match_score"] == 0.0
    assert result["skill_with_entity_match_score"] == 50.0
    assert result["exact_match_score"] == 0.0
    assert result["total_score"] == 45.0


def test_get_final_score_reaches_100_when_every_metric_is_perfect(monkeypatch):
    monkeypatch.setattr(
        utils,
        "calculate_skill_and_entity_scores",
        lambda standard, model: {"skill_match_score": 100.0, "entity_match_score": 100.0},
    )
    monkeypatch.setattr(
        utils,
        "calculate_skill_with_entity_scores",
        lambda standard, model: {"skill_with_entity_match_score": 100.0},
    )
    monkeypatch.setattr(utils, "get_exact_match", lambda standard, model, dependency: 100.0)

    assert utils.get_final_score([], [], "Sequential")["total_score"] == 100.0
