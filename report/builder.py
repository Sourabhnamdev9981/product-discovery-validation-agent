# Combines discovery analysis and validation results into the final report.

from report.schema import CitedFindings, CitedStatement, ProductReport, ReportSource


def build_report(
    product_idea: str,
    analysis: dict,
    validation: dict,
    evidence: list[dict] | None = None,
) -> ProductReport:
    # Build the report only from data already produced by the workflow.
    #
    # evidence is the linked evidence list the analysis indexes refer to
    # (state["evidence"]). When it is None, citations cannot be resolved and
    # findings are returned with no linked sources.

    sources: list[ReportSource] = []
    source_id_by_url: dict[str, int] = {}

    def cite(finding: dict) -> CitedStatement:
        source_ids: list[int] = []

        if evidence is not None:
            for index in finding.get("evidence_indexes", []):
                if not 0 <= index < len(evidence):
                    raise ValueError(
                        f"Finding cites evidence index {index}, which does not "
                        f"exist in the {len(evidence)} evidence items."
                    )

                item = evidence[index]

                # The same page can be returned for several research questions;
                # show it once and let every citation point at that entry.
                if item["url"] not in source_id_by_url:
                    sources.append(
                        ReportSource(
                            id=len(sources) + 1,
                            title=item["title"],
                            url=item["url"],
                            domain=item.get("domain", ""),
                        )
                    )
                    source_id_by_url[item["url"]] = len(sources)

                source_id = source_id_by_url[item["url"]]

                if source_id not in source_ids:
                    source_ids.append(source_id)

        return CitedStatement(
            statement=finding["statement"],
            source_ids=source_ids,
        )

    cited = CitedFindings(
        key_problems=[cite(f) for f in analysis.get("problem_findings", [])],
        target_users=[cite(f) for f in analysis.get("user_findings", [])],
        competitor_findings=[
            cite(f) for f in analysis.get("competitor_findings", [])
        ],
        opportunities=[cite(f) for f in analysis.get("opportunities", [])],
    )

    experiments = [
        experiment["experiment"]
        for experiment in validation.get("validation_experiments", [])
    ]

    return ProductReport(
        product_idea=product_idea,
        key_problems=[c.statement for c in cited.key_problems],
        target_users=[c.statement for c in cited.target_users],
        competitor_findings=[c.statement for c in cited.competitor_findings],
        assumptions=validation.get("assumptions", []),
        opportunities=[c.statement for c in cited.opportunities],
        mvp_features=validation.get("mvp_features", []),
        validation_experiments=experiments,
        sources=sources,
        cited_findings=cited,
    )
