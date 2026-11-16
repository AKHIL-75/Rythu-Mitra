"""Deployment models must not serialize machine-specific training caches."""
import joblib
import pytest

@pytest.mark.parametrize("filename", ["best_model.joblib", "problem_models.joblib"])
def test_deployment_models_have_no_training_cache(root, filename):
    saved = joblib.load(root / "ml/models" / filename)
    models = saved.values() if isinstance(saved, dict) else [saved]
    for model in models:
        assert model.memory is None
