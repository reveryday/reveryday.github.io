import { createRequire } from "node:module";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

// NODE_PATH also allows rebuilding with an existing local dependency install.
const require = createRequire(import.meta.url);
const { build, transform } = require("esbuild");
const postcss = require("postcss");
const here = path.dirname(fileURLToPath(import.meta.url));
const outdir = path.resolve(here, "../../assets/codeimage");
await mkdir(outdir, { recursive: true });
await build({
  absWorkingDir: here,
  entryPoints: { editor: "src/editor.tsx" },
  outdir,
  bundle: true,
  splitting: true,
  format: "esm",
  target: ["es2020"],
  jsx: "automatic",
  minify: true,
  define: { "process.env.NODE_ENV": '"production"' },
  chunkNames: "[name]-[hash]",
  nodePaths: (process.env.NODE_PATH || "").split(path.delimiter).filter(Boolean),
  legalComments: "linked",
});

const css = postcss.parse(await readFile(path.join(here, "src/style.css"), "utf8"));
css.walkAtRules("import", rule => rule.remove());
css.walkDecls(decl => {
  if (decl.parent.selector === ":root" && ["--bg", "--paper", "--text", "--muted", "--border", "--accent", "--accent-hover"].includes(decl.prop)) decl.remove();
});
css.walkRules(rule => {
  if (rule.parent.type === "atrule" && /keyframes$/.test(rule.parent.name)) return;
  if (rule.selector === "html, body" || rule.selector === "body") {
    rule.remove();
    return;
  }
  rule.selectors = rule.selectors.map(selector =>
    selector.trim() === ":root" ? ".codeimage-tool" : `.codeimage-tool ${selector}`
  );
});
const overrides = await readFile(path.join(here, "src/blog.css"), "utf8");
const result = await transform(css.toString() + overrides, { loader: "css", minify: true });
await writeFile(path.join(outdir, "editor.css"), result.code);
const licenses = await Promise.all(["react", "react-dom", "scheduler", "highlight.js", "html-to-image"].map(async name => {
  const root = path.dirname(require.resolve(`${name}/package.json`));
  return `${name}\n${await readFile(path.join(root, "LICENSE"), "utf8")}`;
}));
await writeFile(path.join(outdir, "THIRD-PARTY-LICENSES.txt"), licenses.join("\n\n"));
console.log("Built isolated codeimage assets in assets/codeimage/");
