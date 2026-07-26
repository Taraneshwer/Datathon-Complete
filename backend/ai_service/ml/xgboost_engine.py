import logging
from typing import Any

logger = logging.getLogger(__name__)

def refine_with_xgboost(base_score: float, context: dict[str, Any]) -> float:
    """
    Optionally refine the risk score using an XGBoost model.
    In production: load a pre-trained model from disk.
    This function adjusts the base score using context feature signals.
    """
    try:
        import numpy as np
        
        # Feature signals that increase / decrease risk
        modifiers = {
            "repeat_offender": 0.10,
            "gang_affiliated": 0.12,
            "prior_violence": 0.08,
            "high_crime_area": 0.06,
            "nighttime": 0.04,
            "cctv_absent": 0.05,
        }
        adjustment = sum(
            delta for key, delta in modifiers.items()
            if context.get(key, False)
        )
        return float(np.clip(base_score + adjustment, 0.0, 1.0))
    except Exception as exc:
        logger.warning(f"XGBoost refinement failed: {exc}")
        return base_score
