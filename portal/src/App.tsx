import {
  Children,
  isValidElement,
  lazy,
  Suspense,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import remarkGfm from "remark-gfm";
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Boxes,
  Check,
  ChevronRight,
  CircleHelp,
  Command,
  Compass,
  Copy,
  FileCode2,
  FileText,
  Github,
  Layers3,
  Menu,
  Search,
  Sparkles,
  Workflow,
  X,
} from "lucide-react";
import {
  catalog,
  categoryCounts,
  categoryTitles,
  describeMarkdown,
  loadGuide,
  loadMarkdown,
  type CatalogItem,
  type CategoryId,
} from "./content";
import MermaidDiagram from "./MermaidDiagram";

type View = "overview" | "readme" | "workflows" | CategoryId;

const repository = "https://github.com/ehuerta6/ai-setup";
const ReactMarkdown = lazy(() => import("react-markdown"));
const categoryIcons = {
  skills: Sparkles,
  agents: Boxes,
  rules: Layers3,
  templates: FileText,
  "project-instructions": BookOpen,
};
const categories = Object.keys(categoryTitles) as CategoryId[];

function slugify(value: string) {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/\s+/g, "-");
}

function headingText(value: string) {
  return value
    .replace(/`([^`]*)`/g, "$1")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/<[^>]+>/g, "")
    .replace(/\\(.)/g, "$1");
}

function nodeText(node: React.ReactNode): string {
  if (typeof node === "string" || typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(nodeText).join("");
  if (isValidElement<{ children?: React.ReactNode }>(node))
    return nodeText(node.props.children);
  return "";
}

function extractHeadings(content: string) {
  const markdown = content.replace(/```[\s\S]*?```/g, "");
  return [...markdown.matchAll(/^##\s+(.+)$/gm)].map((match) => {
    const title = match[1].trim();
    return { title, id: slugify(headingText(title)) };
  });
}

function githubUrl(path: string) {
  return `${repository}/blob/main/${path}`;
}

function Markdown({
  content,
  path,
  onOpen,
  onOpenGuide,
}: {
  content: string;
  path: string;
  onOpen: (item: CatalogItem) => void;
  onOpenGuide: (path: "README.md" | "WORKFLOWS.md", hash: string) => void;
}) {
  const linkBase = githubUrl(path);
  const preview = content
    .replace(/^---\s*\r?\n[\s\S]*?\r?\n---\s*(?:\r?\n|$)/, "")
    .replace(/^\s*# [^\r\n]+\r?\n+/, "");
  return (
    <div className="markdown-body">
      <Suspense fallback={<p role="status">Rendering Markdown…</p>}>
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({ children, ...props }) => (
              <h1 id={slugify(nodeText(children))} {...props}>
                {children}
              </h1>
            ),
            h2: ({ children, ...props }) => (
              <h2 id={slugify(nodeText(children))} {...props}>
                {children}
              </h2>
            ),
            h3: ({ children, ...props }) => (
              <h3 id={slugify(nodeText(children))} {...props}>
                {children}
              </h3>
            ),
            a: ({ href = "", children, ...props }) => {
              if (href.startsWith("#"))
                return (
                  <a href={href} {...props}>
                    {children}
                  </a>
                );
              let destination = href;
              try {
                destination = new URL(href, linkBase).href;
              } catch {
                /* keep the original href */
              }
              const linkedPath = destination.match(
                /github\.com\/ehuerta6\/ai-setup\/blob\/main\/(.+?)(?:#.*)?$/,
              )?.[1];
              const linkedItem =
                linkedPath &&
                catalog.find(
                  (item) => item.path === decodeURIComponent(linkedPath),
                );
              const guidePath =
                linkedPath === "README.md" || linkedPath === "WORKFLOWS.md"
                  ? linkedPath
                  : null;
              if (guidePath && guidePath !== path)
                return (
                  <a
                    href={`#${new URL(destination).hash.slice(1)}`}
                    {...props}
                    onClick={(event) => {
                      event.preventDefault();
                      onOpenGuide(guidePath, new URL(destination).hash.slice(1));
                    }}
                  >
                    {children}
                  </a>
                );
              if (linkedPath === path && new URL(destination).hash) {
                return (
                  <a href={new URL(destination).hash} {...props}>
                    {children}
                  </a>
                );
              }
              if (linkedItem)
                return (
                  <a
                    href="#"
                    {...props}
                    onClick={(event) => {
                      event.preventDefault();
                      onOpen(linkedItem);
                    }}
                  >
                    {children}
                  </a>
                );
              const external = /^https?:/.test(destination);
              return (
                <a
                  href={destination}
                  {...props}
                  {...(external ? { target: "_blank", rel: "noreferrer" } : {})}
                >
                  {children}
                </a>
              );
            },
            table: ({ children }) => (
              <div className="table-scroll">
                <table>{children}</table>
              </div>
            ),
            pre: ({ children }) => {
              const child = Children.only(children);
              if (
                isValidElement<{
                  className?: string;
                  children?: React.ReactNode;
                }>(child) &&
                child.props.className?.split(" ").includes("language-mermaid")
              ) {
                return (
                  <MermaidDiagram
                    source={String(child.props.children ?? "").replace(
                      /\n$/,
                      "",
                    )}
                    label={
                      path === "README.md"
                        ? "Repository responsibilities and relationships"
                        : "Workflow selection"
                    }
                  />
                );
              }
              return <pre className="code-block">{children}</pre>;
            },
          }}
        >
          {preview}
        </ReactMarkdown>
      </Suspense>
    </div>
  );
}

function MarkdownDocument({
  content,
  path,
  onOpen,
  onOpenGuide,
}: {
  content: string;
  path: string;
  onOpen: (item: CatalogItem) => void;
  onOpenGuide: (path: "README.md" | "WORKFLOWS.md", hash: string) => void;
}) {
  const headings = useMemo(() => extractHeadings(content), [content]);
  const articleRef = useRef<HTMLElement>(null);
  const [activeHeading, setActiveHeading] = useState(headings[0]?.id ?? "");

  useEffect(() => {
    const article = articleRef.current;
    if (!article || !headings.length) return;
    let observer: IntersectionObserver | undefined;
    const observeHeadings = () => {
      observer?.disconnect();
      observer = new IntersectionObserver(
        (entries) => {
          const visible = entries
            .filter((entry) => entry.isIntersecting)
            .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
          if (visible[0]) setActiveHeading(visible[0].target.id);
        },
        { rootMargin: "0px 0px -78% 0px", threshold: 0 },
      );
      article
        .querySelectorAll("h2[id]")
        .forEach((heading) => observer?.observe(heading));
    };
    observeHeadings();
    const mutations = new MutationObserver(observeHeadings);
    mutations.observe(article, { childList: true, subtree: true });
    return () => {
      mutations.disconnect();
      observer?.disconnect();
    };
  }, [content, headings]);

  useEffect(() => {
    function restoreAnchor() {
      const id = decodeURIComponent(window.location.hash.slice(1));
      if (!id) return;
      setActiveHeading(id);
      document.getElementById(id)?.scrollIntoView({
        behavior: "instant",
        block: "start",
      });
    }
    window.addEventListener("popstate", restoreAnchor);
    return () => window.removeEventListener("popstate", restoreAnchor);
  }, []);

  const links = (
    <nav aria-label="Document sections">
      {headings.map((heading) => (
        <a
          key={heading.id}
          href={`#${heading.id}`}
          aria-current={activeHeading === heading.id ? "location" : undefined}
          onClick={(event) => {
            event.preventDefault();
            setActiveHeading(heading.id);
            if (window.location.hash !== `#${heading.id}`)
              window.history.pushState(null, "", `#${heading.id}`);
            document.getElementById(heading.id)?.scrollIntoView({
              behavior: "instant",
              block: "start",
            });
          }}
        >
          {heading.title}
        </a>
      ))}
    </nav>
  );

  return (
    <div className="document-layout">
      <article className="document-article" ref={articleRef}>
        <Markdown
          content={content}
          path={path}
          onOpen={onOpen}
          onOpenGuide={onOpenGuide}
        />
      </article>
      {headings.length > 0 && (
        <>
          <aside className="document-toc" aria-label="On this page">
            <p>On this page</p>
            {links}
          </aside>
          <details className="document-toc-mobile">
            <summary>
              On this page <span>{headings.length} sections</span>
            </summary>
            {links}
          </details>
        </>
      )}
    </div>
  );
}

function App() {
  const [view, setView] = useState<View>("overview");
  const [selected, setSelected] = useState<CatalogItem | null>(null);
  const [query, setQuery] = useState("");
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [copyMessage, setCopyMessage] = useState("");
  const [selectedContent, setSelectedContent] = useState<string | null>(null);
  const [contentError, setContentError] = useState("");
  const [workflowsContent, setWorkflowsContent] = useState<string | null>(null);
  const [workflowsError, setWorkflowsError] = useState("");
  const [readmeContent, setReadmeContent] = useState<string | null>(null);
  const [readmeError, setReadmeError] = useState("");
  const selectionRequest = useRef(0);
  const mobileMenuButton = useRef<HTMLButtonElement>(null);
  const mobileSidebar = useRef<HTMLElement>(null);
  const mainContent = useRef<HTMLElement>(null);
  const pendingGuideAnchor = useRef("");

  const currentCatalogView = categories.includes(view as CategoryId);
  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return catalog.filter((item) => {
      const matchesCategory = !currentCatalogView || item.category === view;
      const matchesQuery =
        !normalized ||
        `${item.title} ${item.description} ${item.path}`
          .toLowerCase()
          .includes(normalized);
      return matchesCategory && matchesQuery;
    });
  }, [query, view, currentCatalogView]);

  useEffect(() => {
    function handleShortcut(event: KeyboardEvent) {
      const target = event.target as HTMLElement | null;
      const typing =
        target?.isContentEditable ||
        ["INPUT", "TEXTAREA", "SELECT"].includes(target?.tagName ?? "");
      if (event.key === "Escape" && mobileNavOpen) {
        setMobileNavOpen(false);
        mobileMenuButton.current?.focus();
      }
      if (
        event.key === "/" &&
        !mobileNavOpen &&
        !typing &&
        !event.metaKey &&
        !event.ctrlKey &&
        !event.altKey
      ) {
        event.preventDefault();
        if (!currentCatalogView) setView("skills");
        window.setTimeout(
          () =>
            document
              .querySelector<HTMLInputElement>("#catalog-search")
              ?.focus(),
          0,
        );
      }
    }
    window.addEventListener("keydown", handleShortcut);
    return () => window.removeEventListener("keydown", handleShortcut);
  }, [currentCatalogView, mobileNavOpen]);

  useEffect(() => {
    function restoreGuide(event: PopStateEvent) {
      const previousView = (event.state as { portalView?: View } | null)
        ?.portalView;
      if (previousView !== "readme" && previousView !== "workflows") return;
      selectionRequest.current += 1;
      setView(previousView);
      setSelected(null);
      setSelectedContent(null);
      setContentError("");
      setQuery("");
      setMobileNavOpen(false);
    }
    window.addEventListener("popstate", restoreGuide);
    return () => window.removeEventListener("popstate", restoreGuide);
  }, []);

  useEffect(() => {
    const main = mainContent.current;
    if (main) main.inert = mobileNavOpen;
    if (!mobileNavOpen) return;

    const sidebar = mobileSidebar.current;
    if (!sidebar) return;
    const getFocusable = () =>
      Array.from(
        sidebar.querySelectorAll<HTMLElement>(
          "a[href], button:not([disabled]), input:not([disabled])",
        ),
      );
    getFocusable()[0]?.focus();

    function containFocus(event: KeyboardEvent) {
      if (event.key !== "Tab") return;
      const focusable = getFocusable();
      const first = focusable[0];
      const last = focusable.at(-1);
      if (!first || !last) {
        event.preventDefault();
        return;
      }
      const active = document.activeElement;
      if (!sidebar?.contains(active)) {
        event.preventDefault();
        (event.shiftKey ? last : first).focus();
      } else if (event.shiftKey && active === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && active === last) {
        event.preventDefault();
        first.focus();
      }
    }
    document.addEventListener("keydown", containFocus);
    return () => document.removeEventListener("keydown", containFocus);
  }, [mobileNavOpen]);

  useEffect(() => {
    if (!mobileNavOpen) return;
    const desktop = window.matchMedia("(min-width: 901px)");
    function closeOnDesktop(event: MediaQueryListEvent) {
      if (!event.matches) return;
      const closeButton = mobileSidebar.current?.querySelector(
        ".mobile-drawer-close",
      );
      if (document.activeElement === closeButton) {
        mobileSidebar.current
          ?.querySelector<HTMLElement>(".sidebar-brand .brand-button")
          ?.focus();
      }
      setMobileNavOpen(false);
    }
    if (desktop.matches) {
      setMobileNavOpen(false);
      return;
    }
    desktop.addEventListener("change", closeOnDesktop);
    return () => desktop.removeEventListener("change", closeOnDesktop);
  }, [mobileNavOpen]);

  useEffect(() => {
    if (view !== "workflows") return;
    let active = true;
    setWorkflowsContent(null);
    setWorkflowsError("");
    loadGuide("WORKFLOWS.md")
      .then((content) => {
        if (active) setWorkflowsContent(content);
      })
      .catch(() => {
        if (active)
          setWorkflowsError(
            "The workflow guide could not be loaded. Open its canonical source on GitHub.",
          );
      });
    return () => {
      active = false;
    };
  }, [view]);

  useEffect(() => {
    if (view !== "readme") return;
    let active = true;
    setReadmeContent(null);
    setReadmeError("");
    loadGuide("README.md")
      .then((content) => {
        if (active) setReadmeContent(content);
      })
      .catch(() => {
        if (active)
          setReadmeError(
            "The repository guide could not be loaded. Open its canonical source on GitHub.",
          );
      });
    return () => {
      active = false;
    };
  }, [view]);

  useEffect(() => {
    const content =
      view === "readme"
        ? readmeContent
        : view === "workflows"
          ? workflowsContent
          : null;
    if (!content || !pendingGuideAnchor.current) return;
    const anchor = pendingGuideAnchor.current;
    pendingGuideAnchor.current = "";
    requestAnimationFrame(() => {
      document.getElementById(decodeURIComponent(anchor))?.scrollIntoView({
        behavior: "instant",
        block: "start",
      });
    });
  }, [readmeContent, view, workflowsContent]);

  function navigate(next: View) {
    if (window.location.hash)
      window.history.replaceState(
        window.history.state,
        "",
        `${window.location.pathname}${window.location.search}`,
      );
    selectionRequest.current += 1;
    setView(next);
    setSelected(null);
    setSelectedContent(null);
    setContentError("");
    setQuery("");
    setCopyMessage("");
    setMobileNavOpen(false);
    if (mobileNavOpen) mobileMenuButton.current?.focus();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function openGuide(path: "README.md" | "WORKFLOWS.md", hash: string) {
    window.history.replaceState(
      { ...(window.history.state ?? {}), portalView: view },
      "",
      `${window.location.pathname}${window.location.search}${window.location.hash}`,
    );
    pendingGuideAnchor.current = hash;
    const nextView = path === "README.md" ? "readme" : "workflows";
    navigate(nextView);
    window.history.pushState(
      { portalView: nextView },
      "",
      hash ? `#${hash}` : window.location.pathname + window.location.search,
    );
  }

  async function openItem(item: CatalogItem) {
    const requestId = ++selectionRequest.current;
    setView(item.category);
    setSelected(item);
    setSelectedContent(null);
    setContentError("");
    setCopyMessage("");
    setMobileNavOpen(false);
    if (mobileNavOpen) mobileMenuButton.current?.focus();
    window.scrollTo({ top: 0, behavior: "smooth" });
    try {
      const content = await loadMarkdown(item);
      if (selectionRequest.current !== requestId) return;
      setSelected({ ...item, ...describeMarkdown(content, item) });
      setSelectedContent(content);
    } catch {
      if (selectionRequest.current === requestId)
        setContentError(
          "This canonical file could not be loaded. Use the GitHub link to read its source.",
        );
    }
  }

  async function copyMarkdown(item: CatalogItem) {
    try {
      await navigator.clipboard.writeText(await loadMarkdown(item));
      setCopyMessage("Markdown copied to clipboard.");
    } catch {
      setCopyMessage("Copy failed. Check clipboard access and try again.");
    }
  }

  const pageTitle =
    selected?.title ??
    (view === "overview"
      ? "Overview"
      : view === "readme"
        ? "Repository guide"
        : view === "workflows"
          ? "Workflows"
          : categoryTitles[view as CategoryId]);

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <header className="mobile-header">
        <button
          ref={mobileMenuButton}
          className="icon-button"
          aria-label={mobileNavOpen ? "Close navigation" : "Open navigation"}
          aria-expanded={mobileNavOpen}
          aria-controls="main-navigation"
          onClick={() => setMobileNavOpen(!mobileNavOpen)}
        >
          {mobileNavOpen ? <X size={19} /> : <Menu size={19} />}
        </button>
        <Brand onClick={() => navigate("overview")} />
        <a
          className="icon-button"
          aria-label="View repository on GitHub"
          href={repository}
          target="_blank"
          rel="noreferrer"
        >
          <Github size={18} />
        </a>
      </header>

      <aside
        ref={mobileSidebar}
        id="main-navigation"
        className={`sidebar ${mobileNavOpen ? "sidebar-open" : ""}`}
        aria-label="Main navigation"
        role={mobileNavOpen ? "dialog" : undefined}
        aria-modal={mobileNavOpen ? true : undefined}
      >
        <div className="sidebar-brand">
          <Brand onClick={() => navigate("overview")} />
          <button
            className="mobile-drawer-close icon-button"
            aria-label="Close navigation"
            onClick={() => {
              setMobileNavOpen(false);
              mobileMenuButton.current?.focus();
            }}
          >
            <X size={19} />
          </button>
        </div>
        <button
          className="search-trigger"
          onClick={() => {
            navigate("skills");
            window.setTimeout(
              () =>
                document
                  .querySelector<HTMLInputElement>("#catalog-search")
                  ?.focus(),
              0,
            );
          }}
        >
          <Search size={15} />
          <span>Search catalog</span>
          <kbd>/</kbd>
        </button>
        <nav className="nav-groups">
          <div className="nav-group-label">EXPLORE</div>
          <NavButton
            active={view === "overview" && !selected}
            icon={<Compass size={17} />}
            label="Overview"
            onClick={() => navigate("overview")}
          />
          <NavButton
            active={view === "readme"}
            icon={<FileText size={17} />}
            label="Repository guide"
            onClick={() => navigate("readme")}
          />
          <NavButton
            active={view === "workflows"}
            icon={<Workflow size={17} />}
            label="Workflows"
            onClick={() => navigate("workflows")}
          />
          <div className="nav-group-label catalog-label">
            THE CATALOG <span>·</span>
          </div>
          {categories.map((id) => {
            const Icon = categoryIcons[id];
            return (
              <NavButton
                key={id}
                active={view === id}
                icon={<Icon size={17} />}
                label={categoryTitles[id]}
                count={categoryCounts[id]}
                onClick={() => navigate(id)}
              />
            );
          })}
        </nav>
        <div className="sidebar-bottom">
          <a
            className="github-link"
            href={repository}
            target="_blank"
            rel="noreferrer"
          >
            <Github size={16} /> <span>Source on GitHub</span>
            <ArrowRight size={14} />
          </a>
        </div>
      </aside>
      {mobileNavOpen && (
        <button
          className="nav-backdrop"
          aria-label="Close navigation"
          onClick={() => {
            setMobileNavOpen(false);
            mobileMenuButton.current?.focus();
          }}
        />
      )}

      <main ref={mainContent} id="main-content" className="main-content">
        <div className="topbar">
          <div className="breadcrumbs">
            <span>ai-setup</span>
            <ChevronRight size={13} />
            <span>
              {selected ? categoryTitles[selected.category] : pageTitle}
            </span>
          </div>
          <a
            className="topbar-github"
            href={repository}
            target="_blank"
            rel="noreferrer"
          >
            <Github size={15} /> <span>GitHub</span>
          </a>
        </div>
        {view === "overview" && !selected && <Overview onNavigate={navigate} />}
        {view === "workflows" && !selected && (
          <WorkflowPage
            content={workflowsContent}
            error={workflowsError}
            onOpen={openItem}
            onOpenGuide={openGuide}
          />
        )}
        {view === "readme" && !selected && (
          <ReadmePage
            content={readmeContent}
            error={readmeError}
            onOpen={openItem}
            onOpenGuide={openGuide}
          />
        )}
        {currentCatalogView && (
          <CatalogPage
            category={view as CategoryId}
            items={filtered}
            query={query}
            onQuery={setQuery}
            selected={selected}
            selectedContent={selectedContent}
            contentError={contentError}
            onOpen={openItem}
            onOpenGuide={openGuide}
            onBack={() => setSelected(null)}
            onCopy={copyMarkdown}
            copyMessage={copyMessage}
          />
        )}
        <footer className="page-footer">
          <span>Canonical content lives in the repository.</span>
          <a href={`${repository}/tree/main`} target="_blank" rel="noreferrer">
            Browse source <ArrowRight size={13} />
          </a>
        </footer>
      </main>
    </div>
  );
}

function Brand({ onClick }: { onClick: () => void }) {
  return (
    <button className="brand-button" onClick={onClick}>
      <span className="brand-mark">
        <Command size={17} strokeWidth={2.5} />
      </span>
      <span className="brand-name">ai-setup</span>
    </button>
  );
}

function NavButton({
  active,
  icon,
  label,
  count,
  onClick,
}: {
  active: boolean;
  icon: React.ReactNode;
  label: string;
  count?: number;
  onClick: () => void;
}) {
  return (
    <button
      className={`nav-item ${active ? "nav-active" : ""}`}
      aria-current={active ? "page" : undefined}
      onClick={onClick}
    >
      {icon}
      <span>{label}</span>
      {count !== undefined && <span className="nav-count">{count}</span>}
    </button>
  );
}

function Overview({ onNavigate }: { onNavigate: (view: View) => void }) {
  const types = [
    {
      id: "skills" as const,
      label: "Skills",
      icon: Sparkles,
      note: "Repeatable workflows for focused tasks",
    },
    {
      id: "agents" as const,
      label: "Agents",
      icon: Boxes,
      note: "Focused roles for specialized work",
    },
    {
      id: "rules" as const,
      label: "Rules",
      icon: Layers3,
      note: "Stable constraints across tasks",
    },
    {
      id: "templates" as const,
      label: "Templates",
      icon: FileText,
      note: "Starting points for recurring artifacts",
    },
    {
      id: "project-instructions" as const,
      label: "Project instructions",
      icon: BookOpen,
      note: "Context for long-running workspaces",
    },
  ];
  return (
    <div className="page-wrap overview-page">
      <section className="overview-intro">
        <p className="eyebrow">AI-SETUP / CANONICAL CONFIGURATION</p>
        <h1>A field guide to reusable engineering.</h1>
        <p className="intro-description">
          Browse focused workflows, project guidance, and reusable artifacts.
          Each project adopts only what fits its needs.
        </p>
        <div className="hero-actions">
          <button
            className="primary-button"
            onClick={() => onNavigate("skills")}
          >
            Browse the catalog <ArrowRight size={16} />
          </button>
          <button
            className="text-button"
            onClick={() => onNavigate("workflows")}
          >
            Choose a workflow <Workflow size={15} />
          </button>
        </div>
      </section>

      <section className="overview-section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">THE CATALOG</p>
            <h2>Find the right kind of guidance.</h2>
          </div>
        </div>
        <div className="category-list">
          {types.map(({ id, label, icon: Icon, note }) => (
            <button
              className="category-row"
              key={id}
              onClick={() => onNavigate(id)}
            >
              <Icon size={18} aria-hidden="true" />
              <span className="category-copy">
                <strong>{label}</strong>
                <span>{note}</span>
              </span>
              <span className="category-count">{categoryCounts[id]}</span>
              <ChevronRight size={16} aria-hidden="true" />
            </button>
          ))}
        </div>
      </section>

      <section className="guide-links" aria-label="Repository guides">
        <button className="guide-link" onClick={() => onNavigate("readme")}>
          <BookOpen size={18} aria-hidden="true" />
          <span>
            <strong>Repository guide</strong>
            <small>How the canonical configuration fits together</small>
          </span>
          <ArrowRight size={16} aria-hidden="true" />
        </button>
        <button className="guide-link" onClick={() => onNavigate("workflows")}>
          <Workflow size={18} aria-hidden="true" />
          <span>
            <strong>Workflow guide</strong>
            <small>Choose a route for the work at hand</small>
          </span>
          <ArrowRight size={16} aria-hidden="true" />
        </button>
      </section>
    </div>
  );
}

function CatalogPage({
  category,
  items,
  query,
  onQuery,
  selected,
  selectedContent,
  contentError,
  onOpen,
  onOpenGuide,
  onBack,
  onCopy,
  copyMessage,
}: {
  category: CategoryId;
  items: CatalogItem[];
  query: string;
  onQuery: (value: string) => void;
  selected: CatalogItem | null;
  selectedContent: string | null;
  contentError: string;
  onOpen: (item: CatalogItem) => void;
  onOpenGuide: (path: "README.md" | "WORKFLOWS.md", hash: string) => void;
  onBack: () => void;
  onCopy: (item: CatalogItem) => void;
  copyMessage: string;
}) {
  const Icon = categoryIcons[category];
  if (selected)
    return (
      <div className="page-wrap reading-page">
        <button className="back-link" onClick={onBack}>
          <ArrowLeft size={15} /> Back to {categoryTitles[category]}
        </button>
        <div className="reading-heading">
          <div className="reading-title-line">
            <span className="type-icon reading-icon">
              <Icon size={18} />
            </span>
            <span className="eyebrow">
              {categoryTitles[category].toUpperCase()}
            </span>
          </div>
          <h1>{selected.title}</h1>
          <p>{selected.description}</p>
          <div className="reading-actions">
            {(category === "templates" ||
              category === "project-instructions") && (
              <button className="copy-button" onClick={() => onCopy(selected)}>
                <Copy size={15} /> Copy Markdown
              </button>
            )}
            <a
              className="source-button"
              href={githubUrl(selected.path)}
              target="_blank"
              rel="noreferrer"
            >
              <Github size={15} /> View on GitHub <ArrowRight size={13} />
            </a>
          </div>
          {copyMessage && (
            <div
              className={`copy-feedback ${copyMessage.startsWith("Markdown") ? "feedback-success" : "feedback-error"}`}
              role={copyMessage.startsWith("Markdown") ? "status" : "alert"}
              aria-live={
                copyMessage.startsWith("Markdown") ? "polite" : "assertive"
              }
            >
              {copyMessage.startsWith("Markdown") ? (
                <Check size={15} />
              ) : (
                <CircleHelp size={15} />
              )}
              <span>{copyMessage}</span>
            </div>
          )}
          {(category === "templates" ||
            category === "project-instructions") && (
            <p className="copy-note">
              Copied text preserves the original file. Templates and presets may
              need customization for your project.
            </p>
          )}
        </div>
        <div className="reading-content">
          {selectedContent ? (
            <MarkdownDocument
              content={selectedContent}
              path={selected.path}
              onOpen={onOpen}
              onOpenGuide={onOpenGuide}
            />
          ) : contentError ? (
            <div className="content-state" role="alert">
              <CircleHelp size={18} />
              <p>{contentError}</p>
            </div>
          ) : (
            <div className="content-state" role="status">
              <span className="loading-indicator" />
              <p>Loading canonical Markdown…</p>
            </div>
          )}
        </div>
      </div>
    );
  return (
    <div className="page-wrap catalog-page">
      <div className="catalog-header">
        <div className="eyebrow">
          <span className="eyebrow-line" /> BROWSE BY TYPE
        </div>
        <div className="catalog-title-row">
          <div>
            <h1>{categoryTitles[category]}</h1>
            <p>
              {category === "skills"
                ? "Repeatable workflows for focused, high quality work."
                : category === "agents"
                  ? "Specialized roles for work that benefits from isolation."
                  : category === "rules"
                    ? "Stable guidance for how work gets done."
                    : category === "templates"
                      ? "Reusable starting points for recurring artifacts."
                      : "Long-running context for focused project workspaces."}
            </p>
          </div>
          <span className="catalog-total">
            {String(items.length).padStart(2, "0")} <small>items</small>
          </span>
        </div>
        <div className="search-field" role="search">
          <Search size={17} aria-hidden="true" />
          <input
            id="catalog-search"
            value={query}
            onChange={(event) => onQuery(event.target.value)}
            placeholder={`Search ${categoryTitles[category].toLowerCase()}...`}
            aria-label={`Search ${categoryTitles[category]}`}
          />
          {query && (
            <button aria-label="Clear search" onClick={() => onQuery("")}>
              <X size={15} />
            </button>
          )}
          <kbd>/</kbd>
        </div>
      </div>
      {items.length ? (
        <div className="catalog-grid">
          {items.map((item) => (
            <button
              className="catalog-card"
              key={item.id}
              onClick={() => onOpen(item)}
            >
              <span className="catalog-card-top">
                <span className="type-icon">
                  <Icon size={17} />
                </span>
                <span className="card-path">{item.path}</span>
              </span>
              <strong>{item.title}</strong>
              <span className="card-description">{item.description}</span>
              <span className="card-open">
                Read item <ArrowRight size={14} />
              </span>
            </button>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <Search size={22} />
          <h2>No matches found</h2>
          <p>Try a different search term or clear the filter.</p>
          <button className="text-button" onClick={() => onQuery("")}>
            Clear search
          </button>
        </div>
      )}
      <div className="catalog-footnote">
        <FileCode2 size={15} />
        <span>
          Entries are read directly from canonical repository files at build
          time.
        </span>
      </div>
    </div>
  );
}

function WorkflowPage({
  content,
  error,
  onOpen,
  onOpenGuide,
}: {
  content: string | null;
  error: string;
  onOpen: (item: CatalogItem) => void;
  onOpenGuide: (path: "README.md" | "WORKFLOWS.md", hash: string) => void;
}) {
  return (
    <div className="page-wrap workflow-page">
      <div className="eyebrow">
        <span className="eyebrow-line" /> SCENARIO-BASED GUIDE
      </div>
      <div className="workflow-heading">
        <div>
          <h1>Find your route.</h1>
          <p>
            Start with the task in front of you. The workflows are suggestions,
            not required stages.
          </p>
        </div>
        <a
          className="source-button"
          href={githubUrl("WORKFLOWS.md")}
          target="_blank"
          rel="noreferrer"
        >
          <Github size={15} /> View source <ArrowRight size={13} />
        </a>
      </div>
      <div className="workflow-content">
        {content ? (
          <MarkdownDocument
            content={content}
            path="WORKFLOWS.md"
            onOpen={onOpen}
            onOpenGuide={onOpenGuide}
          />
        ) : error ? (
          <div className="content-state" role="alert">
            <CircleHelp size={18} />
            <p>{error}</p>
            <a
              href={githubUrl("WORKFLOWS.md")}
              target="_blank"
              rel="noreferrer"
            >
              View on GitHub
            </a>
          </div>
        ) : (
          <div className="content-state" role="status">
            <span className="loading-indicator" />
            <p>Loading workflow guide…</p>
          </div>
        )}
      </div>
    </div>
  );
}

function ReadmePage({
  content,
  error,
  onOpen,
  onOpenGuide,
}: {
  content: string | null;
  error: string;
  onOpen: (item: CatalogItem) => void;
  onOpenGuide: (path: "README.md" | "WORKFLOWS.md", hash: string) => void;
}) {
  return (
    <div className="page-wrap reading-page guide-page">
      <div className="reading-heading">
        <p className="eyebrow">REPOSITORY GUIDE</p>
        <h1>How this repository fits together.</h1>
        <p>Read the canonical README as it is maintained in the repository.</p>
        <div className="reading-actions">
          <a
            className="source-button"
            href={githubUrl("README.md")}
            target="_blank"
            rel="noreferrer"
          >
            <Github size={15} /> View source <ArrowRight size={13} />
          </a>
        </div>
      </div>
      <div className="reading-content">
        {content ? (
          <MarkdownDocument
            content={content}
            path="README.md"
            onOpen={onOpen}
            onOpenGuide={onOpenGuide}
          />
        ) : error ? (
          <div className="content-state" role="alert">
            <CircleHelp size={18} />
            <p>{error}</p>
            <a href={githubUrl("README.md")} target="_blank" rel="noreferrer">
              View on GitHub
            </a>
          </div>
        ) : (
          <div className="content-state" role="status">
            <span className="loading-indicator" />
            <p>Loading repository guide…</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
