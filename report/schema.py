# Defines the structured final product-discovery report.

from pydantic import BaseModel, ConfigDict, Field


class ReportSource(BaseModel):
    # A web page that supports at least one finding in this report.
    model_config = ConfigDict(extra="forbid")

    id: int
    title: str
    url: str
    domain: str


class CitedStatement(BaseModel):
    # A finding plus the ids of the report sources that support it.
    # An empty source_ids list means no source is linked.
    model_config = ConfigDict(extra="forbid")

    statement: str
    source_ids: list[int]


class CitedFindings(BaseModel):
    # Evidence-backed sections only. Assumptions and recommendations are
    # not sourced and stay as plain string lists on ProductReport.
    model_config = ConfigDict(extra="forbid")

    key_problems: list[CitedStatement] = Field(default_factory=list)
    target_users: list[CitedStatement] = Field(default_factory=list)
    competitor_findings: list[CitedStatement] = Field(default_factory=list)
    opportunities: list[CitedStatement] = Field(default_factory=list)


class ProductReport(BaseModel):
    # Represents the final output assembled from validated workflow data.
    # The first eight fields are the original contract; sources and
    # cited_findings were added for traceability and are purely additive.
    model_config = ConfigDict(extra="forbid")

    product_idea: str
    key_problems: list[str]
    target_users: list[str]
    competitor_findings: list[str]
    assumptions: list[str]
    opportunities: list[str]
    mvp_features: list[str]
    validation_experiments: list[str]
    sources: list[ReportSource] = Field(default_factory=list)
    cited_findings: CitedFindings = Field(default_factory=CitedFindings)
