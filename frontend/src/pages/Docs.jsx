const REPORT_FIELDS = [
  ["Key Problems", "The pain points the research found evidence for."],
  ["Target Users", "Who experiences those problems and is most likely to care."],
  ["Competitor Findings", "Existing products and alternatives, and how they fall short."],
  ["Assumptions", "What has to be true for the idea to work — and has not been proven yet."],
  ["Opportunities", "Gaps and openings where a new product could win."],
  ["MVP Features", "The smallest feature set worth building first."],
  ["Validation Experiments", "Concrete tests to check the riskiest assumptions before building."],
];

const USER_GUIDE = {
  label: "User Guide",
  title: "Using the Product Discovery Agent",
  summary:
    "Learn how to describe a product idea, what happens while research runs, and how to read the report.",
  sections: [
    {
      id: "introduction",
      title: "Introduction",
      content: (
        <>
          <p>
            The Product Discovery Agent turns a product idea into a structured,
            evidence-backed report using AI and live web research. This guide
            explains how to use it effectively.
          </p>
          <div className="callout">
            <p className="eyebrow">What you can do</p>
            <ul className="checklist">
              <li>Research the problems and needs behind an idea</li>
              <li>Identify target users and existing competitors</li>
              <li>Surface assumptions and opportunities</li>
              <li>Get MVP feature suggestions and validation experiments</li>
            </ul>
          </div>
          <h3>Who is this for?</h3>
          <p>
            Students, founders, product managers and anyone who wants to test
            a product idea before building it.
          </p>
        </>
      ),
    },
    {
      id: "getting-started",
      title: "Getting Started",
      content: (
        <ol className="numbered">
          <li>
            Open <a href="#/discover">Discover</a>.
          </li>
          <li>Describe your product idea in the text area.</li>
          <li>
            Select <strong>Start Discovery</strong> and keep the tab open while
            the research runs.
          </li>
          <li>
            When it finishes, the report opens automatically. Use{" "}
            <strong>Print / Save PDF</strong> to keep a copy.
          </li>
        </ol>
      ),
    },
    {
      id: "writing-ideas",
      title: "Writing Product Ideas",
      content: (
        <>
          <p>
            The idea is the only input, so its quality shapes the whole report.
            A good description names three things: the user, the problem and
            the approach.
          </p>
          <div className="compare">
            <div>
              <p className="eyebrow">Vague</p>
              <p>An app for students.</p>
            </div>
            <div>
              <p className="eyebrow">Specific</p>
              <p>
                An AI tool that helps final-year students practise job
                interviews with realistic mock questions and feedback.
              </p>
            </div>
          </div>
        </>
      ),
    },
    {
      id: "understanding-reports",
      title: "Understanding Reports",
      content: (
        <>
          <p>Every report contains the same seven sections:</p>
          <dl className="definitions">
            {REPORT_FIELDS.map(([term, description]) => (
              <div key={term}>
                <dt>{term}</dt>
                <dd>{description}</dd>
              </div>
            ))}
          </dl>
        </>
      ),
    },
    {
      id: "best-practices",
      title: "Best Practices",
      content: (
        <ul className="bullets">
          <li>Start with one idea per discovery rather than several at once.</li>
          <li>Treat Assumptions as a to-do list: each one is a risk to check.</li>
          <li>Run the Validation Experiments before committing to the MVP.</li>
          <li>
            Re-run discovery with a sharper description when the results feel
            too generic.
          </li>
        </ul>
      ),
    },
    {
      id: "faq",
      title: "FAQ",
      content: (
        <dl className="definitions">
          <div>
            <dt>How long does a discovery take?</dt>
            <dd>
              It depends on the research involved. Expect it to take a few
              minutes.
            </dd>
          </div>
          <div>
            <dt>Are reports saved?</dt>
            <dd>
              No. A report lives in the current browser tab only. Refreshing or
              closing the tab clears it, so save a PDF if you need it later.
            </dd>
          </div>
          <div>
            <dt>Why did my discovery fail?</dt>
            <dd>
              The error message on the Discover page explains the cause. The
              most common one is that the backend service is not running.
            </dd>
          </div>
        </dl>
      ),
    },
  ],
};

const TECHNICAL = {
  label: "Technical Documentation",
  title: "Technical Documentation",
  summary:
    "The system architecture, the discovery workflow, the API contract and local development setup.",
  sections: [
    {
      id: "architecture",
      title: "Architecture",
      content: (
        <>
          <p>The project has two parts:</p>
          <dl className="definitions">
            <div>
              <dt>Frontend</dt>
              <dd>
                A React single-page app built with Vite, located in{" "}
                <code>frontend/</code>. It collects the product idea, calls the
                API and renders the report.
              </dd>
            </div>
            <div>
              <dt>Backend</dt>
              <dd>
                A Python service that runs the discovery workflow and exposes it
                over HTTP at <code>http://localhost:8000</code>.
              </dd>
            </div>
          </dl>
        </>
      ),
    },
    {
      id: "workflow",
      title: "Discovery Workflow",
      content: (
        <>
          <p>Each request runs through the same sequence of steps:</p>
          <ol className="numbered">
            <li>Product Idea</li>
            <li>Research Planning</li>
            <li>Web Research</li>
            <li>Evidence Verification</li>
            <li>Analysis</li>
            <li>Validation</li>
            <li>Final Report</li>
          </ol>
          <p>
            See <a href="#/how-it-works">How It Works</a> for a description of
            each step.
          </p>
        </>
      ),
    },
    {
      id: "api",
      title: "API Reference",
      content: (
        <>
          <p>
            <code>POST /discover</code> — runs a discovery for one product
            idea.
          </p>
          <h3>Request</h3>
          <pre>
            <code>{`{
  "product_idea": "string"
}`}</code>
          </pre>
          <h3>Response</h3>
          <p>Fields read by the frontend:</p>
          <pre>
            <code>{`{
  "report": {
    "product_idea": "string",
    "key_problems": ["string"],
    "target_users": ["string"],
    "competitor_findings": ["string"],
    "assumptions": ["string"],
    "opportunities": ["string"],
    "mvp_features": ["string"],
    "validation_experiments": ["string"]
  }
}`}</code>
          </pre>
          <h3>Errors</h3>
          <p>
            A non-2xx response is treated as a failure. If the body contains a
            string <code>detail</code> field, it is shown to the user.
          </p>
        </>
      ),
    },
    {
      id: "frontend",
      title: "Frontend Structure",
      content: (
        <>
          <pre>
            <code>{`frontend/src/
├── main.jsx            entry point
├── App.jsx             routing, navigation, API call
├── index.css           design system
└── pages/
    ├── Home.jsx
    ├── Discover.jsx
    ├── Report.jsx
    ├── HowItWorks.jsx
    └── Docs.jsx`}</code>
          </pre>
          <p>
            Routing is hash-based (<code>#/discover</code>,{" "}
            <code>#/report</code>, …) and needs no extra dependencies. The
            report is held in React state and is not persisted.
          </p>
        </>
      ),
    },
    {
      id: "development",
      title: "Development Setup",
      content: (
        <>
          <p>From the <code>frontend/</code> directory:</p>
          <pre>
            <code>{`npm install
npm run dev     # start the dev server
npm run lint    # run ESLint
npm run build   # production build`}</code>
          </pre>
          <p>
            The backend must be running on <code>http://localhost:8000</code>.
            The URL is set by <code>API_URL</code> in{" "}
            <code>src/App.jsx</code>.
          </p>
        </>
      ),
    },
  ],
};

const DOCS = {
  "user-guide": USER_GUIDE,
  technical: TECHNICAL,
};

function scrollToSection(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
}

function Docs({ route }) {
  const doc = DOCS[route.split("/")[2]];
  return doc ? <DocDetail doc={doc} /> : <DocsOverview />;
}

function DocsOverview() {
  return (
    <section className="container page">
      <p className="eyebrow">03. Documentation</p>
      <h1 className="page-title">
        Everything you need to use
        <br />
        and understand the agent.
      </h1>
      <p className="lede">
        Guides and technical details for the Product Discovery Agent.
      </p>

      <div className="doc-preview-grid">
        {Object.entries(DOCS).map(([slug, doc]) => (
          <article key={slug} className="doc-preview">
            <p className="eyebrow">{doc.label}</p>
            <h2 className="card-title">{doc.title}</h2>
            <p className="card-body">{doc.summary}</p>
            <ul className="bullets compact">
              {doc.sections.map((section) => (
                <li key={section.id}>{section.title}</li>
              ))}
            </ul>
            <a href={`#/docs/${slug}`} className="btn btn-primary">
              Read the {doc.label.toLowerCase()}{" "}
              <span aria-hidden="true">→</span>
            </a>
          </article>
        ))}
      </div>
    </section>
  );
}

function DocDetail({ doc }) {
  return (
    <section className="container page">
      <a href="#/docs" className="back-link">
        <span aria-hidden="true">←</span> Back to Docs
      </a>

      <div className="doc-layout">
        <nav className="toc" aria-label={`${doc.label} sections`}>
          <p className="eyebrow">{doc.label}</p>
          {doc.sections.map((section, index) => (
            <button
              key={section.id}
              type="button"
              onClick={() => scrollToSection(section.id)}
            >
              <span className="index-num">0{index + 1}</span>
              <span className="toc-label">{section.title}</span>
            </button>
          ))}
        </nav>

        <article className="doc-body prose">
          <header className="report-header">
            <p className="eyebrow">{doc.label}</p>
            <h1 className="page-title">{doc.title}</h1>
            <p className="lede">{doc.summary}</p>
          </header>

          {doc.sections.map((section) => (
            <section key={section.id} id={section.id} className="prose-section">
              <h2>{section.title}</h2>
              {section.content}
            </section>
          ))}
        </article>
      </div>
    </section>
  );
}

export default Docs;
