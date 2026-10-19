import { useEffect, useId, useState } from "react";

let mermaidPromise: Promise<(typeof import("mermaid"))["default"]> | undefined;

function loadMermaid() {
  mermaidPromise ??= import("mermaid").then(({ default: mermaid }) => {
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: "strict",
      theme: "base",
      themeVariables: {
        darkMode: true,
        background: "#080e17",
        primaryColor: "#14243a",
        primaryTextColor: "#f3f6fa",
        primaryBorderColor: "#536a84",
        lineColor: "#a8b8ca",
        secondaryColor: "#0e1928",
        tertiaryColor: "#1a2b40",
        clusterBkg: "#0c1624",
        clusterBorder: "#455a73",
        edgeLabelBackground: "#0b1320",
        fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
      },
      flowchart: { htmlLabels: false, curve: "linear", useMaxWidth: false },
    });
    return mermaid;
  });
  return mermaidPromise;
}

export default function MermaidDiagram({
  source,
  label,
}: {
  source: string;
  label: string;
}) {
  const reactId = useId();
  const [svg, setSvg] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);
  const id = `diagram-${reactId.replace(/[^a-zA-Z0-9_-]/g, "")}`;

  useEffect(() => {
    let active = true;
    loadMermaid()
      .then((mermaid) => mermaid.render(id, source))
      .then(({ svg: rendered }) => {
        if (active) setSvg(rendered);
      })
      .catch(() => {
        if (active) setFailed(true);
      });
    return () => {
      active = false;
    };
  }, [id, source]);

  if (failed) {
    return (
      <div className="diagram-fallback" role="alert">
        <p>
          This diagram could not be rendered. Its original source is shown
          below.
        </p>
        <pre className="code-block">
          <code>{source}</code>
        </pre>
      </div>
    );
  }

  if (!svg)
    return (
      <p className="diagram-loading" role="status">
        Rendering diagram…
      </p>
    );

  return (
    <div className="mermaid-frame">
      <p className="diagram-hint">
        Scroll sideways to explore the full diagram.
      </p>
      <div
        className="mermaid-scroll"
        role="region"
        aria-label={`${label} diagram. Scroll horizontally to view all content.`}
        tabIndex={0}
      >
        <div
          className="mermaid-diagram"
          role="img"
          aria-label={label}
          dangerouslySetInnerHTML={{ __html: svg }}
        />
      </div>
    </div>
  );
}
