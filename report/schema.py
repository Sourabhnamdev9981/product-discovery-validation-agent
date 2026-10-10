# Defines the structured final product-discovery report.

from pydantic import BaseModel, ConfigDict


class ProductReport(BaseModel):
    # Represents the final output assembled from validated workflow data.
    model_config = ConfigDict(extra="forbid")

    product_idea: str
    key_problems: list[str]
    target_users: list[str]
    competitor_findings: list[str]
    assumptions: list[str]
    opportunities: list[str]
    mvp_features: list[str]
    validation_experiments: list[str]
