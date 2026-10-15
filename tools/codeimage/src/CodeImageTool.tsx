"use client";

import { useCallback, useDeferredValue, useEffect, useMemo, useRef, useState } from "react";
import hljs from "highlight.js/lib/core";
import bash from "highlight.js/lib/languages/bash";
import cpp from "highlight.js/lib/languages/cpp";
import csharp from "highlight.js/lib/languages/csharp";
import css from "highlight.js/lib/languages/css";
import fortran from "highlight.js/lib/languages/fortran";
import go from "highlight.js/lib/languages/go";
import java from "highlight.js/lib/languages/java";
import javascript from "highlight.js/lib/languages/javascript";
import json from "highlight.js/lib/languages/json";
import kotlin from "highlight.js/lib/languages/kotlin";
import markdown from "highlight.js/lib/languages/markdown";
import php from "highlight.js/lib/languages/php";
import python from "highlight.js/lib/languages/python";
import ruby from "highlight.js/lib/languages/ruby";
import rust from "highlight.js/lib/languages/rust";
import sql from "highlight.js/lib/languages/sql";
import swift from "highlight.js/lib/languages/swift";
import typescript from "highlight.js/lib/languages/typescript";
import xml from "highlight.js/lib/languages/xml";
import yaml from "highlight.js/lib/languages/yaml";

const languages = [
  ["javascript", "JavaScript", javascript],
  ["typescript", "TypeScript", typescript],
  ["python", "Python", python],
  ["bash", "Shell", bash],
  ["json", "JSON", json],
  ["html", "HTML", xml],
  ["css", "CSS", css],
  ["markdown", "Markdown", markdown],
  ["java", "Java", java],
  ["cpp", "C / C++", cpp],
  ["csharp", "C#", csharp],
  ["go", "Go", go],
  ["rust", "Rust", rust],
  ["sql", "SQL", sql],
  ["yaml", "YAML", yaml],
  ["swift", "Swift", swift],
  ["kotlin", "Kotlin", kotlin],
  ["ruby", "Ruby", ruby],
  ["php", "PHP", php],
  ["fortran", "Fortran", fortran],
] as const;

languages.forEach(([key, , definition]) => {
  if (!hljs.getLanguage(key)) hljs.registerLanguage(key, definition);
});

const starterCode = `const moments = ["读书", "写作", "生活"];

function keepToday(items) {
  return items.map((item, index) => ({
    id: index + 1,
    note: \`今天也要认真${'${item}'}。\`,
  }));
}

console.log(keepToday(moments));`;

const MAX_FILE_SIZE = 1024 * 1024;
const MAX_EXPORT_EDGE = 16_384;
const MAX_EXPORT_PIXELS = 64_000_000;

function downloadImage(dataUrl: string, fileName: string) {
  const link = document.createElement("a");
  link.download = fileName;
  link.href = dataUrl;
  link.click();
}

export default function CodeImageTool() {
  const [code, setCode] = useState(starterCode);
  const [language, setLanguage] = useState("auto");
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [padding, setPadding] = useState(0);
  const [imageWidth, setImageWidth] = useState(720);
  const [fontSize, setFontSize] = useState(14);
  const [lineHeight, setLineHeight] = useState(1.25);
  const [radius, setRadius] = useState(4);
  const [lineNumbers, setLineNumbers] = useState(false);
  const [windowChrome, setWindowChrome] = useState(false);
  const [shadow, setShadow] = useState(false);
  const [scale, setScale] = useState(3);
  const [exporting, setExporting] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const previewRef = useRef<HTMLDivElement>(null);
  const stageRef = useRef<HTMLDivElement>(null);
  const [previewSize, setPreviewSize] = useState({ width: 720, height: 240, ratio: 1 });

  useEffect(() => {
    const frame = previewRef.current;
    const stage = stageRef.current;
    if (!frame || !stage) return;
    const fit = () => {
      const width = frame.offsetWidth;
      const height = frame.offsetHeight;
      const ratio = Math.min(1, Math.max(1, stage.clientWidth - 48) / width,
        Math.max(1, stage.clientHeight - 48) / height);
      setPreviewSize(previous => previous.width === width && previous.height === height && previous.ratio === ratio
        ? previous : { width, height, ratio });
    };
    const observer = new ResizeObserver(fit);
    observer.observe(frame);
    observer.observe(stage);
    fit();
    return () => observer.disconnect();
  }, []);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const deferredCode = useDeferredValue(code);

  const showToast = useCallback((message: string) => {
    setToast(message);
    if (toastTimer.current) clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 2200);
  }, []);

  const highlighted = useMemo(() => {
    const source = deferredCode || " ";
    if (language === "auto") return hljs.highlightAuto(source).value;
    try {
      return hljs.highlight(source, { language }).value;
    } catch {
      return hljs.highlightAuto(source).value;
    }
  }, [deferredCode, language]);

  const lines = highlighted.split("\n");

  // 阴影绘制在代码块外沿，需要留白承接，否则会被图片边界裁掉
  const effectivePadding = shadow ? Math.max(padding, 24) : padding;

  const renderImage = useCallback(async () => {
    if (!previewRef.current) return Promise.resolve(null);
    const { offsetWidth: width, offsetHeight: height } = previewRef.current;
    const exportWidth = Math.ceil(width * scale);
    const exportHeight = Math.ceil(height * scale);
    if (
      exportWidth > MAX_EXPORT_EDGE ||
      exportHeight > MAX_EXPORT_EDGE ||
      exportWidth * exportHeight > MAX_EXPORT_PIXELS
    ) {
      throw new Error("图片尺寸过大，请减少代码行数、字号或边距");
    }
    // image-frame 自带纯色背景, 不需要 backgroundColor 选项
    try {
      const { toPng } = await import("html-to-image");
      return await toPng(previewRef.current, {
        width,
        height,
        pixelRatio: scale,
        cacheBust: true,
        // Only system fonts are used; avoid fetching the blog's unrelated KaTeX fonts.
        skipFonts: true,
      });
    } catch {
      throw new Error("图片生成失败，请缩小内容后重试");
    }
  }, [scale]);

  const fileName = language === "auto" ? "code.png" : `code-${language}.png`;

  const exportImage = useCallback(async () => {
    if (!previewRef.current || exporting) return;
    setExporting(true);
    try {
      const dataUrl = await renderImage();
      if (!dataUrl) return;
      downloadImage(dataUrl, fileName);
      showToast("已导出 PNG");
    } catch (error) {
      showToast(error instanceof Error ? error.message : "图片生成失败，请稍后重试");
    } finally {
      setExporting(false);
    }
  }, [exporting, fileName, renderImage, showToast]);

  const copyImage = useCallback(async () => {
    if (!previewRef.current || exporting) return;
    setExporting(true);
    let dataUrl: string | null = null;
    try {
      dataUrl = await renderImage();
      if (!dataUrl) return;
      const blob = await (await fetch(dataUrl)).blob();
      await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
      showToast("图片已复制，可直接粘贴");
    } catch (error) {
      if (dataUrl) {
        // 剪贴板不可用（非 HTTPS 等）时复用已生成的图片退回下载
        downloadImage(dataUrl, fileName);
        showToast("当前环境不支持复制图片，已改为下载");
      } else {
        showToast(error instanceof Error ? error.message : "图片生成失败，请稍后重试");
      }
    } finally {
      setExporting(false);
    }
  }, [exporting, fileName, renderImage, showToast]);

  // 快捷键、页面级粘贴、拖拽文件
  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if (!(event.metaKey || event.ctrlKey) || !event.shiftKey) return;
      const key = event.key.toLowerCase();
      if (key === "c") {
        event.preventDefault();
        void copyImage();
      } else if (key === "s") {
        event.preventDefault();
        void exportImage();
      }
    }
    function onPaste(event: ClipboardEvent) {
      const target = event.target as HTMLElement | null;
      if (target?.closest("textarea, input, select, [contenteditable]")) return;
      const text = event.clipboardData?.getData("text/plain");
      if (!text) return;
      event.preventDefault();
      setCode(text);
      showToast("代码已填入");
    }
    function onDragOver(event: DragEvent) {
      event.preventDefault();
    }
    function onDrop(event: DragEvent) {
      event.preventDefault();
      const file = event.dataTransfer?.files?.[0];
      if (!file) return;
      if (file.size > MAX_FILE_SIZE) {
        showToast("文件超过 1 MB，请选择更小的代码文件");
        return;
      }
      void file.text()
        .then((text) => {
          if (text.includes("\0")) throw new Error("不支持二进制文件");
          setCode(text);
          showToast(`已载入 ${file.name}`);
        })
        .catch((error) => {
          showToast(error instanceof Error ? error.message : "文件读取失败");
        });
    }
    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("paste", onPaste);
    window.addEventListener("dragover", onDragOver);
    window.addEventListener("drop", onDrop);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("paste", onPaste);
      window.removeEventListener("dragover", onDragOver);
      window.removeEventListener("drop", onDrop);
    };
  }, [copyImage, exportImage, showToast]);

  useEffect(() => () => {
    if (toastTimer.current) clearTimeout(toastTimer.current);
  }, []);

  return (
    <main className="app-shell" aria-label="代码成像">
      <section className="workspace" aria-label="代码图片编辑器">
        <div className="panel editor-panel">
          <div className="panel-heading editor-heading">
            <div>
              <h2>代码编辑器</h2>
            </div>
            <div className="editor-meta">
              <label className="language-select">
                <span className="sr-only">语言</span>
                <select value={language} onChange={(event) => setLanguage(event.target.value)}>
                  <option value="auto">自动检测</option>
                  {languages.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                </select>
              </label>
              <span className="line-count">{code.split("\n").length} 行</span>
            </div>
          </div>
          <textarea
            className="code-input"
            value={code}
            onChange={(event) => setCode(event.target.value)}
            spellCheck={false}
            aria-label="输入代码"
          />
          <div className="editor-footer">
            <span>粘贴或拖入代码文件</span>
            <span>最大 1 MB</span>
          </div>
        </div>

        <div className="preview-column">
          <div className="panel-heading preview-heading">
            <div>
              <h2>实时预览</h2>
            </div>
            <div className="preview-actions">
              <button className="copy-button" type="button" onClick={copyImage} disabled={exporting} title="⌘⇧C">
                {exporting ? "生成中…" : "复制图片"}
              </button>
              <button className="export-button" type="button" onClick={exportImage} disabled={exporting} title="⌘⇧S">
                {exporting ? "正在生成…" : "导出 PNG"}
              </button>
            </div>
          </div>

          <div className="settings-panel" aria-label="图片设置">
            <div className="appearance-control">
              <span className="control-title">外观</span>
              <div className="segmented" aria-label="主题">
                <button aria-label="浅色主题" aria-pressed={theme === "light"} className={theme === "light" ? "active" : ""} onClick={() => setTheme("light")} type="button">浅</button>
                <button aria-label="深色主题" aria-pressed={theme === "dark"} className={theme === "dark" ? "active" : ""} onClick={() => setTheme("dark")} type="button">深</button>
              </div>
            </div>
            <div className="appearance-control">
              <span className="control-title">清晰度</span>
              <div className="segmented" aria-label="导出倍率">
                {[2, 3, 4].map((value) => (
                  <button
                    key={value}
                    aria-label={`${value} 倍分辨率`}
                    aria-pressed={scale === value}
                    className={scale === value ? "active" : ""}
                    onClick={() => setScale(value)}
                    type="button"
                  >
                    {value}×
                  </button>
                ))}
              </div>
            </div>
              <label className="range-control width-control">
                <span>宽度</span>
                <input aria-label="图片宽度" type="range" min="400" max="1200" step="20" value={imageWidth} onChange={(event) => setImageWidth(Number(event.target.value))} />
                <output>{imageWidth}</output>
              </label>
            <details className="more-settings">
              <summary>更多设置</summary>
              <div className="advanced-settings">
              <div className="range-controls">
              <label className="range-control">
                <span>边距</span>
                <input aria-label="图片边距" type="range" min="0" max="80" step="4" value={padding} onChange={(event) => setPadding(Number(event.target.value))} />
                <output>{padding}</output>
              </label>
              <label className="range-control">
                <span>字号</span>
                <input aria-label="代码字号" type="range" min="12" max="20" value={fontSize} onChange={(event) => setFontSize(Number(event.target.value))} />
                <output>{fontSize}</output>
              </label>
              <label className="range-control">
                <span>行高</span>
                <input aria-label="代码行高" type="range" min="1.2" max="2" step="0.05" value={lineHeight} onChange={(event) => setLineHeight(Number(event.target.value))} />
                <output>{lineHeight.toFixed(2)}</output>
              </label>
              <label className="range-control">
                <span>圆角</span>
                <input aria-label="代码块圆角" type="range" min="0" max="16" step="1" value={radius} onChange={(event) => setRadius(Number(event.target.value))} />
                <output>{radius}</output>
              </label>
            </div>
            <div className="toggle-controls">
              <label className="line-toggle">
                <input type="checkbox" checked={lineNumbers} onChange={(event) => setLineNumbers(event.target.checked)} />
                <span>行号</span>
              </label>
              <label className="line-toggle">
                <input type="checkbox" checked={windowChrome} onChange={(event) => setWindowChrome(event.target.checked)} />
                <span>窗口栏</span>
              </label>
              <label className="line-toggle">
                <input type="checkbox" checked={shadow} onChange={(event) => setShadow(event.target.checked)} />
                <span>阴影</span>
              </label>
            </div>
              </div>
            </details>
          </div>

          <div ref={stageRef} className={`image-stage ${theme}`} aria-label="图片预览">
            <div className="preview-scaled" style={{ width: previewSize.width * previewSize.ratio, height: previewSize.height * previewSize.ratio }}>
            <div className="preview-transform" style={{ transform: `scale(${previewSize.ratio})` }}>
            <div
              ref={previewRef}
              className={`image-frame ${theme}`}
              style={{ padding: `${effectivePadding}px`, width: `${imageWidth}px` }}
            >
              <div
                className="blog-code-block"
                style={{
                  fontSize: `${fontSize}px`,
                  lineHeight,
                  borderRadius: `${radius}px`,
                  boxShadow: shadow ? "0 8px 24px rgba(0,0,0,.16)" : undefined,
                }}
              >
                {windowChrome && (
                  <div className="window-bar" aria-hidden="true">
                    <span /><span /><span />
                  </div>
                )}
                <code className="hljs">
                  {lines.map((line, index) => (
                    <span className="code-line" key={`${index}-${line.slice(0, 12)}`}>
                      {lineNumbers && <span className="line-number">{index + 1}</span>}
                      <span dangerouslySetInnerHTML={{ __html: line || "&nbsp;" }} />
                    </span>
                  ))}
                </code>
              </div>
            </div>
            </div>
            </div>
          </div>
        </div>
      </section>

      <footer className="app-footer">
        <span><i aria-hidden="true" />代码仅在你的浏览器中处理</span>
        <span>⌘/Ctrl + Shift + C 复制 · S 导出</span>
      </footer>

      {toast && <div className="toast" role="status">{toast}</div>}
    </main>
  );
}
