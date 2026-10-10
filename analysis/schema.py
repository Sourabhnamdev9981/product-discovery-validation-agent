# Defines the strict structured output expected from
# the product-discovery analysis stage.

from pydantic import BaseModel, ConfigDict


class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    statement: str
    evidence_indexes: list[int]


class DiscoveryAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    problem_findings: list[Finding]
    user_findings: list[Finding]
    competitor_findings: list[Finding]
    assumptions: list[str]
    opportunities: list[Finding]
