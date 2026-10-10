# Defines the strict structured output expected from
# the product-discovery analysis stage.

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator


class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    statement: str = Field(description="A concise finding or opportunity.")
    evidence_indexes: list[int] = Field(
        description=(
            "Indexes of the supplied evidence items that directly support "
            "the statement."
        )
    )

    @field_validator("evidence_indexes")
    @classmethod
    def check_evidence_indexes(
        cls,
        indexes: list[int],
        info: ValidationInfo,
    ) -> list[int]:
        # Only enforced when the caller passes the indexes of the evidence
        # the model actually saw, i.e. when validating real model output.
        valid_indexes = (info.context or {}).get("valid_indexes")

        if valid_indexes is None:
            return indexes

        if not indexes:
            raise ValueError("A finding must cite at least one evidence index.")

        invalid = [index for index in indexes if index not in valid_indexes]

        if invalid:
            raise ValueError(
                f"Evidence indexes {invalid} do not refer to evidence "
                "supplied to the model."
            )

        return indexes


class DiscoveryAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    problem_findings: list[Finding] = Field(
        description="Evidence-backed user problems."
    )
    user_findings: list[Finding] = Field(
        description="Evidence-backed findings about who has the problem."
    )
    competitor_findings: list[Finding] = Field(
        description="Evidence-backed findings about existing alternatives."
    )
    assumptions: list[str] = Field(
        description="Unverified hypotheses as plain strings."
    )
    opportunities: list[Finding] = Field(
        description=(
            "Evidence-backed opportunities. Each item is an object with "
            "statement and evidence_indexes, never a plain string."
        )
    )
