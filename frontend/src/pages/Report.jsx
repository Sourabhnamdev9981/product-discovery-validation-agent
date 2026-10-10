const SECTIONS = [
  ["key_problems", "Key Problems"],
  ["target_users", "Target Users"],
  ["competitor_findings", "Competitor Findings"],
  ["assumptions", "Assumptions"],
  ["opportunities", "Opportunities"],
  ["mvp_features", "MVP Features"],
  ["validation_experiments", "Validation Experiments"],
];

function pad(number) {
  return String(number).padStart(2, "0");
}

function scrollToSection(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
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

  const sections = SECTIONS.map(([key, title]) => ({
    key,
    title,
    items: report[key] || [],
  }));
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
          {sections.length} sections · {totalFindings} findings
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
                  {section.items.length}{" "}
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
                      <p>{item}</p>
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
        </div>
      </div>
    </section>
  );
}

export default Report;
