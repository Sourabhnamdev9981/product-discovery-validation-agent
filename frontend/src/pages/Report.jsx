// basis describes how much a section can be trusted at face value:
//   sourced        - model finding with linked web sources
//   inference      - model conclusion drawn from linked sources
//   assumption     - unverified hypothesis, not sourced
//   recommendation - suggested next step, not sourced
const SECTIONS = [
  { key: "key_problems", title: "Key Problems", basis: "sourced" },
  { key: "target_users", title: "Target Users", basis: "sourced" },
  { key: "competitor_findings", title: "Competitor Findings", basis: "sourced" },
  { key: "assumptions", title: "Assumptions", basis: "assumption" },
  { key: "opportunities", title: "Opportunities", basis: "inference" },
  { key: "mvp_features", title: "MVP Features", basis: "recommendation" },
  {
    key: "validation_experiments",
    title: "Validation Experiments",
    basis: "recommendation",
  },
];

const BASIS_LABEL = {
  sourced: "Linked to web sources",
  inference: "Inference from linked sources",
  assumption: "Unverified assumption",
  recommendation: "Recommendation, not sourced",
};

function pad(number) {
  return String(number).padStart(2, "0");
}

function scrollToSection(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
}

// Only http(s) links are rendered as anchors; anything else is shown as text.
function safeHttpUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:"
      ? url.href
      : null;
  } catch {
    return null;
  }
}

// Responses from older backends have no cited_findings; fall back to the
// plain string lists so the report still renders.
function buildSections(report) {
  const cited = report.cited_findings || {};

  return SECTIONS.map(({ key, title, basis }) => {
    const items = cited[key]
      ? cited[key].map((c) => ({
          statement: c.statement,
          sourceIds: c.source_ids || [],
        }))
      : (report[key] || []).map((statement) => ({
          statement,
          sourceIds: [],
        }));

    return { key, title, basis, items };
  });
}

// Buttons, not anchors: the app uses hash routing, so "#source-1" would
// navigate away from the report.
function Citations({ ids }) {
  return ids.map((id) => (
    <button
      key={id}
      type="button"
      className="cite"
      onClick={() => scrollToSection(`source-${id}`)}
      aria-label={`Source ${id}`}
    >
      [{id}]
    </button>
  ));
}

function Report({ report, generatedAt }) {
  if (!report) {
    return (
      <section className="container page narrow">
        <p className="eyebrow">Discovery report</p>
        <h1 className="page-title">No report yet.</h1>
        <p className="lede">
          Reports exist only in this browser tab. Run a discovery to generate
          one.
        </p>
        <div className="actions">
          <a href="#/discover" className="btn btn-primary">
            Start Discovering <span aria-hidden="true">→</span>
          </a>
        </div>
      </section>
    );
  }

  const sections = buildSections(report);
  const sources = report.sources || [];
  const totalFindings = sections.reduce((sum, s) => sum + s.items.length, 0);

  return (
    <section className="container page">
      <div className="report-actions">
        <a href="#/discover" className="back-link">
          <span aria-hidden="true">←</span> New discovery
        </a>
        <button
          type="button"
          className="btn btn-secondary btn-sm"
          onClick={() => window.print()}
        >
          Print / Save PDF
        </button>
      </div>

      <header className="report-header">
        <p className="eyebrow">Discovery report</p>
        <h1 className="page-title">{report.product_idea}</h1>
        <p className="meta">
          {generatedAt &&
            `Generated ${generatedAt.toLocaleDateString(undefined, {
              day: "numeric",
              month: "short",
              year: "numeric",
            })} · `}
          {sections.length} sections · {totalFindings} findings ·{" "}
          {sources.length} sources
        </p>
        <p className="report-note">
          Findings are written by a language model from search-result excerpts.
          Linked sources show what the model was given. They do not confirm that
          a claim is true, and they do not establish customer demand, willingness
          to pay or product-market fit.
        </p>
      </header>

      <div className="doc-layout">
        <nav className="toc" aria-label="Report sections">
          <p className="eyebrow">Contents</p>
          {sections.map((section, index) => (
            <button
              key={section.key}
              type="button"
              onClick={() => scrollToSection(section.key)}
            >
              <span className="index-num">{pad(index + 1)}</span>
              <span className="toc-label">{section.title}</span>
              <span className="toc-count">{section.items.length}</span>
            </button>
          ))}
          <button type="button" onClick={() => scrollToSection("sources")}>
            <span className="index-num">{pad(sections.length + 1)}</span>
            <span className="toc-label">Sources</span>
            <span className="toc-count">{sources.length}</span>
          </button>
        </nav>

        <div className="doc-body">
          {sections.map((section, index) => (
            <section
              key={section.key}
              id={section.key}
              className="report-section"
            >
              <header className="report-section-head">
                <span className="index-num">{pad(index + 1)}</span>
                <h2>{section.title}</h2>
                <span className="meta">
                  {BASIS_LABEL[section.basis]} · {section.items.length}{" "}
                  {section.items.length === 1 ? "item" : "items"}
                </span>
              </header>

              {section.items.length > 0 ? (
                <ol className="findings">
                  {section.items.map((item, itemIndex) => (
                    <li key={`${section.key}-${itemIndex}`}>
                      <span className="finding-num">
                        {index + 1}.{itemIndex + 1}
                      </span>
                      <p>
                        {item.statement}
                        {item.sourceIds.length > 0 && (
                          <span className="cites">
                            {" "}
                            <Citations ids={item.sourceIds} />
                          </span>
                        )}
                        {item.sourceIds.length === 0 &&
                          (section.basis === "sourced" ||
                            section.basis === "inference") && (
                            <span className="meta cite-missing">
                              {" "}
                              · no source linked
                            </span>
                          )}
                      </p>
                    </li>
                  ))}
                </ol>
              ) : (
                <p className="muted">
                  No findings were returned for this section.
                </p>
              )}
            </section>
          ))}

          <section id="sources" className="report-section">
            <header className="report-section-head">
              <span className="index-num">{pad(sections.length + 1)}</span>
              <h2>Sources</h2>
              <span className="meta">
                {sources.length} {sources.length === 1 ? "page" : "pages"}
              </span>
            </header>

            {sources.length > 0 ? (
              <ol className="findings">
                {sources.map((source) => {
                  const href = safeHttpUrl(source.url);

                  return (
                    <li key={source.id} id={`source-${source.id}`}>
                      <span className="finding-num">[{source.id}]</span>
                      <div>
                        <p>{source.title}</p>
                        {href ? (
                          <a
                            className="text-link"
                            href={href}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            {source.domain || href}
                          </a>
                        ) : (
                          <p className="muted">{source.url}</p>
                        )}
                      </div>
                    </li>
                  );
                })}
              </ol>
            ) : (
              <p className="muted">No web sources are linked to this report.</p>
            )}
          </section>
        </div>
      </div>
    </section>
  );
}

export default Report;
