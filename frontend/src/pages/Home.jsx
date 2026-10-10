import { useEffect, useState } from "react";

const HEROES = [
  {
    title: "Turn a product idea\ninto real insights.",
    lede: "Research problems, users, competitors and opportunities using live web data and AI. Get a clear, structured report to validate and plan your idea.",
  },
  {
    title: "Validate the idea\nbefore you build it.",
    lede: "Surface the assumptions behind your idea and get concrete experiments to test them — before you spend months writing code.",
  },
  {
    title: "Find the problem\nworth solving.",
    lede: "Discover the real pain points, who has them, and how existing products fall short, backed by evidence gathered from the web.",
  },
  {
    title: "From one sentence\nto a research report.",
    lede: "Describe your idea once. Get key problems, target users, competitor findings, opportunities and an MVP plan in a single document.",
  },
];

// Pick a headline different from the one shown on the previous visit.
function pickHero() {
  const previous = Number(localStorage.getItem("heroIndex"));
  const options = HEROES.map((_, index) => index).filter(
    (index) => index !== previous,
  );
  const next = options[Math.floor(Math.random() * options.length)];
  localStorage.setItem("heroIndex", String(next));
  return HEROES[next];
}

const START_INDEX = HEROES.indexOf(pickHero());
const TYPE_MS = 40;
const DELETE_MS = 30;
const HOLD_MS = 5000;

// Types, holds, deletes, then moves to the next headline. Exactly one timer is
// pending at any time, so rotation can never overlap a running animation.
function Typewriter() {
  const [index, setIndex] = useState(START_INDEX);
  const [count, setCount] = useState(0);
  const [deleting, setDeleting] = useState(false);
  const { title, lede } = HEROES[index];

  useEffect(() => {
    let delay;
    let step;
    if (!deleting && count < title.length) {
      delay = TYPE_MS;
      step = () => setCount(count + 1);
    } else if (!deleting) {
      delay = HOLD_MS;
      step = () => setDeleting(true);
    } else if (count > 0) {
      delay = DELETE_MS;
      step = () => setCount(count - 1);
    } else {
      delay = TYPE_MS;
      step = () => {
        setDeleting(false);
        setIndex((index + 1) % HEROES.length);
      };
    }
    const id = setTimeout(step, delay);
    return () => clearTimeout(id);
  }, [count, deleting, index, title.length]);

  const done = !deleting && count === title.length;

  // Hidden copies of every headline/lede share one grid cell, reserving the
  // largest size so switching headlines never shifts the layout.
  return (
    <>
      <h1 className="display typed" aria-label={title.replace("\n", " ")}>
        {HEROES.map((hero) => (
          <span key={hero.title} className="typed-ghost" aria-hidden="true">
            {hero.title}
            <span className="cursor">_</span>
          </span>
        ))}
        <span aria-hidden="true">
          {title.slice(0, count)}
          <span className="cursor">_</span>
        </span>
      </h1>
      <p className="lede hero-lede typed">
        {HEROES.map((hero) => (
          <span key={hero.title} className="typed-ghost" aria-hidden="true">
            {hero.lede}
          </span>
        ))}
        <span className={`reveal${done ? " shown" : ""}`}>{lede}</span>
      </p>
    </>
  );
}

const FEATURES = [
  {
    title: "Real research",
    body: "Plans what needs to be known about your idea, then gathers and verifies evidence from the web before drawing conclusions.",
    href: "#/docs/technical",
  },
  {
    title: "Structured report",
    body: "Problems, users, competitors, assumptions, opportunities, MVP features and experiments — in one readable document.",
    href: "#/docs/user-guide",
  },
  {
    title: "Built for builders",
    body: "Go from a one-line idea to a validation plan you can act on before writing a single line of product code.",
    href: "#/docs/user-guide",
  },
];

const REPORT_SECTIONS = [
  "Key Problems",
  "Target Users",
  "Competitor Findings",
  "Assumptions",
  "Opportunities",
  "MVP Features",
  "Validation Experiments",
];

const DOC_PREVIEWS = [
  {
    label: "User Guide",
    title: "Using the agent",
    body: "How to write a strong product idea, what to expect while research runs, and how to read each section of the report.",
    href: "#/docs/user-guide",
  },
  {
    label: "Technical Documentation",
    title: "How it is built",
    body: "The discovery workflow, the /discover API contract, the frontend structure and how to run everything locally.",
    href: "#/docs/technical",
  },
];

function Home() {
  return (
    <>
      <section className="container hero">
        <p className="eyebrow">AI Product Discovery</p>
        <Typewriter />
        <div className="actions">
          <a href="#/discover" className="btn btn-primary">
            Start Discovering <span aria-hidden="true">→</span>
          </a>
          <a href="#/how-it-works" className="btn btn-secondary">
            Learn How It Works
          </a>
        </div>
      </section>

      <section className="container">
        <div className="card-grid">
          {FEATURES.map((feature, index) => (
            <article key={feature.title} className="card">
              <span className="card-index">0{index + 1}</span>
              <h2 className="card-title">{feature.title}</h2>
              <p className="card-body">{feature.body}</p>
              <a href={feature.href} className="text-link">
                Read more <span aria-hidden="true">→</span>
              </a>
            </article>
          ))}
        </div>
      </section>

      <section className="container band">
        <div className="band-head">
          <p className="eyebrow">The report</p>
          <h2 className="section-title">Seven sections. One document.</h2>
        </div>
        <ol className="index-list">
          {REPORT_SECTIONS.map((title, index) => (
            <li key={title}>
              <span className="index-num">0{index + 1}</span>
              {title}
            </li>
          ))}
        </ol>
      </section>

      <section className="container band">
        <div className="band-head">
          <p className="eyebrow">Documentation</p>
          <h2 className="section-title">Learn the agent.</h2>
        </div>
        <div className="doc-preview-grid">
          {DOC_PREVIEWS.map((doc) => (
            <article key={doc.label} className="doc-preview">
              <p className="eyebrow">{doc.label}</p>
              <h3>{doc.title}</h3>
              <p className="card-body">{doc.body}</p>
              <a href={doc.href} className="text-link">
                Read more <span aria-hidden="true">→</span>
              </a>
            </article>
          ))}
        </div>
      </section>
    </>
  );
}

export default Home;
