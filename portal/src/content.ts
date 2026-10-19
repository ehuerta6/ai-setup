export type CategoryId =
  "skills" | "agents" | "rules" | "templates" | "project-instructions";

export type CatalogItem = {
  id: string;
  category: CategoryId;
  title: string;
  description: string;
  path: string;
};

type RawModule = { default: string };

const markdownFiles = import.meta.glob<string>(
  [
    "../../skills/*/SKILL.md",
    "../../agents/*.md",
    "../../rules/*.md",
    "../../templates/*.md",
    "../../project-instructions/*.md",
  ],
  { query: "?raw", import: "default", eager: true },
);

const workflowsModule = import.meta.glob<RawModule>("../../WORKFLOWS.md", {
  query: "?raw",
});

const categoryTitles: Record<CategoryId, string> = {
  skills: "Skills",
  agents: "Agents",
  rules: "Rules",
  templates: "Templates",
  "project-instructions": "Project Instructions",
};

function frontMatter(content: string) {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---\s*\n?([\s\S]*)$/);
  if (!match) return { metadata: "", body: content };
  return { metadata: match[1], body: match[2] };
}

function metadataValue(metadata: string, key: string) {
  return (
    metadata
      .match(new RegExp(`^${key}:\\s*(.*)$`, "m"))?.[1]
      ?.trim()
      .replace(/^['"]|['"]$/g, "") ?? ""
  );
}

function openingDescription(body: string) {
  const introduction = body
    .split(/\r?\n\s*\r?\n/)
    .map((block) =>
      block
        .replace(/^#{1,6}\s+.*$/gm, "")
        .replace(/\s+/g, " ")
        .trim(),
    )
    .find(
      (block) =>
        block &&
        !block.startsWith("```") &&
        !block.startsWith("|") &&
        !block.startsWith("<"),
    );
  if (!introduction) return "";
  return introduction.length > 150
    ? `${introduction.slice(0, 147).trimEnd()}…`
    : introduction;
}

function titleFrom(content: string, path: string) {
  const body = frontMatter(content).body;
  const heading = body.match(/^#\s+(.+)$/m)?.[1]?.trim();
  if (heading) return heading.replace(/^Spec:\s*/i, "");
  return (
    path.split("/").at(-1)?.replace(/\.md$/i, "").replace(/[-_]/g, " ") ?? path
  );
}

function titleFromPath(category: CategoryId, path: string) {
  const pieces = path.split("/");
  const name =
    category === "skills"
      ? pieces.at(-2)
      : pieces.at(-1)?.replace(/\.md$/i, "");
  const title =
    name
      ?.replace(/[-_]/g, " ")
      .toLowerCase()
      .replace(/\b\w/g, (letter) => letter.toUpperCase()) ?? path;
  return title.replace(/\bAi\b/g, "AI").replace(/\bPr\b/g, "PR");
}

const categoryDescriptions: Record<CategoryId, string> = {
  skills: "A reusable workflow for AI-assisted engineering.",
  agents: "A focused role for specialized work.",
  rules: "Stable guidance for how work gets done.",
  templates: "A starting point for a recurring artifact.",
  "project-instructions": "A preset for long-running workspace context.",
};

function categoryAndPath(
  fileKey: string,
): { category: CategoryId; path: string } | undefined {
  const match = fileKey.match(
    /^\.\.\/\.\.\/(skills|agents|rules|templates|project-instructions)\/(.+\.md)$/,
  );
  if (!match) return undefined;
  const [, category, relativePath] = match;
  if (category === "skills" && !relativePath.endsWith("/SKILL.md"))
    return undefined;
  return {
    category: category as CategoryId,
    path: `${category}/${relativePath}`,
  };
}

export const catalog: CatalogItem[] = Object.entries(markdownFiles)
  .flatMap((key) => {
    const [fileKey, content] = key;
    const canonical = categoryAndPath(fileKey);
    if (!canonical) return [];
    const id = canonical.path.replace(/\.md$/i, "");
    const pathItem: CatalogItem = {
      id,
      category: canonical.category,
      title: titleFromPath(canonical.category, canonical.path),
      description: categoryDescriptions[canonical.category],
      path: canonical.path,
    };
    return [
      {
        ...pathItem,
        ...describeMarkdown(content, pathItem),
      },
    ];
  })
  .sort((a, b) => a.title.localeCompare(b.title));

export async function loadMarkdown(item: CatalogItem) {
  const content = markdownFiles[`../../${item.path}`];
  if (!content) throw new Error(`Could not load canonical file: ${item.path}`);
  return content;
}

export async function loadWorkflows() {
  const file = Object.values(workflowsModule)[0];
  if (!file) throw new Error("Could not load canonical file: WORKFLOWS.md");
  return (await file()).default;
}

export function describeMarkdown(content: string, item: CatalogItem) {
  const { metadata, body } = frontMatter(content);
  const title =
    item.category === "skills"
      ? titleFromPath(item.category, item.path)
      : titleFrom(body, item.path);
  const description =
    metadataValue(metadata, "description") ||
    body.match(/^>\s*(.+)$/m)?.[1]?.trim() ||
    openingDescription(body) ||
    item.description;
  return { title, description };
}

export const categoryCounts = Object.fromEntries(
  Object.keys(categoryTitles).map((id) => [
    id,
    catalog.filter((item) => item.category === id).length,
  ]),
) as Record<CategoryId, number>;

export { categoryTitles };
