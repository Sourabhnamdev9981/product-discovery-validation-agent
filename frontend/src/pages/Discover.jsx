const EXAMPLES = [
  "An AI study planner that adapts to university exam schedules",
  "A local event discovery app for people who just moved to a new city",
  "A marketplace for buying and selling second-hand sustainable fashion",
];

function Discover({ productIdea, setProductIdea, onSubmit, loading, error }) {
  return (
    <section className="container page narrow">
      <p className="eyebrow">01. Product discovery</p>
      <h1 className="page-title">
        Describe your
        <br />
        product idea.
      </h1>
      <p className="lede">
        One description is all it takes. Say who it is for and what problem it
        solves — the more specific, the sharper the research.
      </p>

      <form className="discover-form" onSubmit={onSubmit}>
        <label htmlFor="product-idea" className="sr-only">
          Product idea
        </label>
        <textarea
          id="product-idea"
          value={productIdea}
          onChange={(event) => setProductIdea(event.target.value)}
          placeholder="e.g. An AI tool that helps students prepare for job interviews…"
          rows={7}
          disabled={loading}
        />
        <button
          type="submit"
          className="btn btn-primary btn-block"
          disabled={loading}
        >
          {loading ? (
            "Researching…"
          ) : (
            <>
              Start Discovery <span aria-hidden="true">→</span>
            </>
          )}
        </button>
      </form>

      {loading && (
        <div className="status" role="status">
          <div className="progress" aria-hidden="true" />
          <p>
            <strong>Research in progress.</strong> The agent is researching
            your idea on the web and writing the report. This may take a few
            minutes — keep this tab open.
          </p>
        </div>
      )}

      {error && (
        <div className="alert" role="alert">
          <strong>Discovery failed</strong>
          <p>{error}</p>
        </div>
      )}

      <div className="examples">
        <p className="eyebrow">Example ideas</p>
        <div className="chips">
          {EXAMPLES.map((example) => (
            <button
              key={example}
              type="button"
              className="chip"
              onClick={() => setProductIdea(example)}
              disabled={loading}
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Discover;
