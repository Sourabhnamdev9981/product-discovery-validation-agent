import { useEffect, useState } from "react";
import Home from "./pages/Home.jsx";
import Discover from "./pages/Discover.jsx";
import Report from "./pages/Report.jsx";
import HowItWorks from "./pages/HowItWorks.jsx";
import Docs from "./pages/Docs.jsx";

const API_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000";

const NAV = [
  ["/", "Home"],
  ["/discover", "Discover"],
  ["/how-it-works", "How It Works"],
  ["/docs", "Docs"],
];

function currentRoute() {
  return window.location.hash.slice(1) || "/";
}

function initialTheme() {
  return (
    localStorage.getItem("theme") ||
    (window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light")
  );
}

function App() {
  const [route, setRoute] = useState(currentRoute);
  const [theme, setTheme] = useState(initialTheme);
  const [productIdea, setProductIdea] = useState("");
  const [report, setReport] = useState(null);
  const [generatedAt, setGeneratedAt] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    function handleHashChange() {
      setRoute(currentRoute());
      window.scrollTo(0, 0);
    }

    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("theme", theme);
  }, [theme]);

  async function handleSubmit(event) {
    event.preventDefault();

    if (!productIdea.trim()) {
      setError("Please enter a product idea.");
      return;
    }

    setLoading(true);
    setError("");
    setReport(null);

    try {
      const response = await fetch(`${API_URL}/discover`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          product_idea: productIdea,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Discovery request failed.",
        );
      }

      setReport(data.report);
      setGeneratedAt(new Date());
      window.location.hash = "/report";
    } catch (err) {
      setError(
        err instanceof TypeError
          ? `Could not reach the discovery service at ${API_URL}. Make sure the backend is running.`
          : err.message,
      );
    } finally {
      setLoading(false);
    }
  }

  function isActive(path) {
    return path === "/" ? route === "/" : route.startsWith(path);
  }

  let page;
  if (route === "/discover") {
    page = (
      <Discover
        productIdea={productIdea}
        setProductIdea={setProductIdea}
        onSubmit={handleSubmit}
        loading={loading}
        error={error}
      />
    );
  } else if (route === "/report") {
    page = <Report report={report} generatedAt={generatedAt} />;
  } else if (route === "/how-it-works") {
    page = <HowItWorks />;
  } else if (route.startsWith("/docs")) {
    page = <Docs route={route} />;
  } else {
    page = <Home />;
  }

  const links = report ? [...NAV, ["/report", "Report"]] : NAV;

  return (
    <>
      <header className="nav">
        <div className="container nav-inner">
          <a href="#/" className="brand">
            <span className="brand-mark" aria-hidden="true" />
            Product Discovery Agent
          </a>

          <nav className="nav-links" aria-label="Primary">
            {links.map(([path, label]) => (
              <a
                key={path}
                href={`#${path}`}
                className={isActive(path) ? "active" : undefined}
                aria-current={isActive(path) ? "page" : undefined}
              >
                {label}
              </a>
            ))}
          </nav>

          <button
            type="button"
            role="switch"
            aria-checked={theme === "dark"}
            aria-label="Dark mode"
            title="Toggle dark mode"
            className="theme-switch"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            <span className="theme-switch-knob" />
          </button>

          <a href="#/discover" className="btn btn-primary btn-sm nav-cta">
            Get Started
          </a>
        </div>
      </header>

      <main>{page}</main>

      <footer className="footer">
        <div className="container footer-inner">
          <span className="brand">
            <span className="brand-mark" aria-hidden="true" />
            Product Discovery Agent
          </span>
          <nav aria-label="Footer">
            {NAV.map(([path, label]) => (
              <a key={path} href={`#${path}`}>
                {label}
              </a>
            ))}
          </nav>
        </div>
      </footer>
    </>
  );
}

export default App;
