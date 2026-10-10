# Defines the structured output for product validation.

from pydantic import BaseModel, ConfigDict


class ValidationExperiment(BaseModel):
    # Describes one practical way to test a product assumption.
    model_config = ConfigDict(extra="forbid")

    assumption: str
    experiment: str
    success_signal: str
    priority: str


class ProductValidation(BaseModel):
    # Defines actionable validation recommendations.
    model_config = ConfigDict(extra="forbid")

    assumptions: list[str]
    mvp_features: list[str]
    validation_experiments: list[ValidationExperiment]
