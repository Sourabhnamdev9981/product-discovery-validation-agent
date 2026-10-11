const STEPS = [
  {
    title: "Product Idea",
    body: "You describe the product in plain language. This single description is the only input.",
  },
  {
    title: "Research Planning",
    body: "The idea is broken down into what needs to be found out: the problem, the people who have it and the alternatives that already exist.",
  },
  {
    title: "Web Research",
    body: "The agent searches the web for information relevant to the research plan.",
  },
  {
    title: "Source Linking",
    body: "Results without a title, link or snippet are dropped, and each remaining source is linked to the findings it supports. The sources are not fact-checked.",
  },
  {
    title: "Analysis",
    body: "The linked sources are analysed into problems, target users, competitor findings, assumptions and opportunities.",
  },
  {
    title: "Validation",
    body: "Findings are turned into MVP features and validation experiments that test the riskiest assumptions.",
  },
  {
    title: "Final Report",
    body: "A structured, seven-section report is returned to your browser.",
  },
];

function HowItWorks() {
  return (
    <section className="container page">
      <p className="eyebrow">02. How it works</p>
      <h1 className="page-title">
        From idea to insights
        <br />
        in seven steps.
      </h1>
      <p className="lede">
        Every discovery runs the same workflow, from a single description to a
        finished report.
      </p>

      <ol className="flow" aria-label="Workflow overview">
        {STEPS.map((step, index) => (
          <li key={step.title}>
            <span className="index-num">0{index + 1}</span>
            {step.title}
          </li>
        ))}
      </ol>

      <ol className="steps">
        {STEPS.map((step, index) => (
          <li key={step.title}>
            <span className="step-num">0{index + 1}</span>
            <div>
              <h2>{step.title}</h2>
              <p>{step.body}</p>
            </div>
          </li>
        ))}
      </ol>

      <div className="cta-band">
        <h2 className="section-title">Try it on your own idea.</h2>
        <div className="actions">
          <a href="#/discover" className="btn btn-primary">
            Start Discovering <span aria-hidden="true">→</span>
          </a>
          <a href="#/docs/technical" className="btn btn-secondary">
            Technical Docs
          </a>
        </div>
      </div>
    </section>
  );
}

export default HowItWorks;
