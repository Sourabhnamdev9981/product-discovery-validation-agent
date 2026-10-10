# Combines discovery analysis and validation results into the final report.

from report.schema import ProductReport


def build_report(
    product_idea: str,
    analysis: dict,
    validation: dict,
) -> ProductReport:
    # Build the report only from data already produced by the workflow.

    key_problems = [
        finding["statement"] for finding in analysis.get("problem_findings", [])
    ]

    target_users = [
        finding["statement"] for finding in analysis.get("user_findings", [])
    ]

    competitor_findings = [
        finding["statement"] for finding in analysis.get("competitor_findings", [])
    ]

    experiments = [
        experiment["experiment"]
        for experiment in validation.get("validation_experiments", [])
    ]

    return ProductReport(
        product_idea=product_idea,
        key_problems=key_problems,
        target_users=target_users,
        competitor_findings=competitor_findings,
        assumptions=validation.get("assumptions", []),
        opportunities=analysis.get("opportunities", []),
        mvp_features=validation.get("mvp_features", []),
        validation_experiments=experiments,
    )
