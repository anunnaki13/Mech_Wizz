from typing import Literal


DATA_STATUS_VALUES = ("actual", "estimated", "benchmark", "user_assumption", "unknown", "partner_supplied")
CONFIDENCE_LEVEL_VALUES = ("high", "medium", "low", "unknown")

DataStatus = Literal["actual", "estimated", "benchmark", "user_assumption", "unknown", "partner_supplied"]
ConfidenceLevel = Literal["high", "medium", "low", "unknown"]
