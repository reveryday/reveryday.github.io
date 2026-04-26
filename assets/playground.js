(function () {
  "use strict";

  const GODBOLT_ENDPOINT = "https://godbolt.org/api";
  const STORAGE_PREFIX = "playground:";

  const LANGUAGES = {
    python: {
      label: "Python",
      displayName: "Python 3.13",
      compilerId: "python313",
      godboltLang: "python",
      cmMode: "python",
      defaultCode: 'print("Hello, World!")\n',
    },
    cpp: {
      label: "C++",
      displayName: "gcc 13.2",
      compilerId: "g132",
      godboltLang: "c++",
      cmMode: "text/x-c++src",
      defaultCode:
        '#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello, World!" << endl;\n    return 0;\n}\n',
    },
    fortran: {
      label: "Fortran",
      displayName: "gfortran 13.2",
      compilerId: "gfortran132",
      godboltLang: "fortran",
      cmMode: "fortran",
      defaultCode:
        'program hello\n    print *, "Hello, World!"\nend program hello\n',
    },
  };

  let currentLang = "python";
  let editor = null;

  function loadStored(key, fallback) {
    try {
      const value = localStorage.getItem(STORAGE_PREFIX + key);
      return value === null ? fallback : value;
    } catch (e) {
      return fallback;
    }
  }

  function saveStored(key, value) {
    try {
      localStorage.setItem(STORAGE_PREFIX + key, value);
    } catch (e) {
      /* storage unavailable; silently ignore */
    }
  }

  function getCodeFor(lang) {
    return loadStored("code:" + lang, LANGUAGES[lang].defaultCode);
  }

  function getStdinFor(lang) {
    return loadStored("stdin:" + lang, "");
  }

  function setActiveButton(lang) {
    document.querySelectorAll(".pg-lang-btn").forEach(function (btn) {
      const isActive = btn.dataset.lang === lang;
      btn.classList.toggle("is-active", isActive);
      btn.setAttribute("aria-pressed", String(isActive));
    });
  }

  function updateCompilerInfo() {
    const el = document.getElementById("pg-compiler-info");
    if (!el) return;
    const cfg = LANGUAGES[currentLang];
    el.textContent = cfg ? cfg.displayName : "";
  }

  function clearOutput() {
    const out = document.getElementById("pg-output");
    if (out) out.innerHTML = "";
  }

  function switchLanguage(lang) {
    if (!LANGUAGES[lang]) return;
    if (lang === currentLang) {
      setActiveButton(lang);
      return;
    }

    if (editor) {
      saveStored("code:" + currentLang, editor.getValue());
    }
    const stdinEl = document.getElementById("pg-stdin");
    if (stdinEl) {
      saveStored("stdin:" + currentLang, stdinEl.value);
    }

    currentLang = lang;
    saveStored("lang", lang);
    setActiveButton(lang);

    if (editor) {
      editor.setOption("mode", LANGUAGES[lang].cmMode);
      editor.setValue(getCodeFor(lang));
    }
    if (stdinEl) {
      stdinEl.value = getStdinFor(lang);
    }
    updateCompilerInfo();
  }

  function setRunning(running) {
    const runBtn = document.getElementById("pg-run");
    if (runBtn) {
      runBtn.disabled = running;
      runBtn.textContent = running ? "Running…" : "▶ Run";
    }
    document.querySelectorAll(".pg-lang-btn").forEach(function (btn) {
      btn.disabled = running;
    });
    const clearBtn = document.getElementById("pg-clear");
    if (clearBtn) clearBtn.disabled = running;
  }

  function joinLines(arr) {
    if (!Array.isArray(arr) || arr.length === 0) return "";
    return arr
      .map(function (x) {
        return x && typeof x.text === "string" ? x.text : String(x);
      })
      .join("\n");
  }

  function appendOutputBlock(parent, label, text, cls) {
    if (!text) return;
    const wrap = document.createElement("div");
    wrap.className = "pg-output-block " + (cls || "");
    const head = document.createElement("div");
    head.className = "pg-output-label";
    head.textContent = label;
    const pre = document.createElement("pre");
    pre.textContent = text;
    wrap.appendChild(head);
    wrap.appendChild(pre);
    parent.appendChild(wrap);
  }

  function renderOutput(result) {
    const out = document.getElementById("pg-output");
    if (!out) return;
    out.innerHTML = "";

    const build = result.buildResult || {};
    appendOutputBlock(out, "compile stdout", joinLines(build.stdout), "pg-stdout");
    appendOutputBlock(out, "compile stderr", joinLines(build.stderr), "pg-stderr");
    appendOutputBlock(out, "stdout", joinLines(result.stdout), "pg-stdout");
    appendOutputBlock(out, "stderr", joinLines(result.stderr), "pg-stderr");

    const meta = document.createElement("div");
    meta.className = "pg-output-meta";
    let line = "Exit code: " + (typeof result.code === "number" ? result.code : "?");
    if (result.timedOut) line += " | Timed out";
    if (result.didExecute === false) line += " | Did not execute";
    meta.textContent = line;
    out.appendChild(meta);
  }

  function renderError(message) {
    const out = document.getElementById("pg-output");
    if (!out) return;
    out.innerHTML = "";
    appendOutputBlock(out, "error", message, "pg-stderr");
  }

  function runCode() {
    if (!editor) return;
    const code = editor.getValue();
    const stdinEl = document.getElementById("pg-stdin");
    const stdin = stdinEl ? stdinEl.value : "";

    saveStored("code:" + currentLang, code);
    saveStored("stdin:" + currentLang, stdin);

    const cfg = LANGUAGES[currentLang];

    setRunning(true);
    fetch(GODBOLT_ENDPOINT + "/compiler/" + cfg.compilerId + "/compile", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
      body: JSON.stringify({
        source: code,
        lang: cfg.godboltLang,
        options: {
          userArguments: "",
          executeParameters: { args: [], stdin: stdin },
          compilerOptions: { executorRequest: true },
          filters: { execute: true },
        },
      }),
    })
      .then(function (resp) {
        return resp.text().then(function (text) {
          if (!resp.ok) {
            throw new Error("HTTP " + resp.status + ": " + text);
          }
          try {
            return JSON.parse(text);
          } catch (e) {
            throw new Error("Invalid response: " + text);
          }
        });
      })
      .then(function (data) {
        renderOutput(data);
      })
      .catch(function (err) {
        renderError(err && err.message ? err.message : String(err));
      })
      .then(function () {
        setRunning(false);
      });
  }

  function init() {
    const textarea = document.getElementById("pg-code");
    if (!textarea || !window.CodeMirror) return;

    const storedLang = loadStored("lang", "python");
    currentLang = LANGUAGES[storedLang] ? storedLang : "python";

    textarea.value = getCodeFor(currentLang);

    editor = window.CodeMirror.fromTextArea(textarea, {
      mode: LANGUAGES[currentLang].cmMode,
      lineNumbers: true,
      indentUnit: 4,
      tabSize: 4,
      lineWrapping: false,
      viewportMargin: Infinity,
      extraKeys: {
        "Ctrl-Enter": runCode,
        "Cmd-Enter": runCode,
      },
    });

    editor.on("change", function () {
      saveStored("code:" + currentLang, editor.getValue());
    });

    const stdinEl = document.getElementById("pg-stdin");
    if (stdinEl) {
      stdinEl.value = getStdinFor(currentLang);
      stdinEl.addEventListener("input", function () {
        saveStored("stdin:" + currentLang, stdinEl.value);
      });
      stdinEl.addEventListener("keydown", function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
          e.preventDefault();
          runCode();
        }
      });
    }

    setActiveButton(currentLang);
    updateCompilerInfo();
    document.querySelectorAll(".pg-lang-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        switchLanguage(btn.dataset.lang);
      });
    });

    const runBtn = document.getElementById("pg-run");
    if (runBtn) {
      runBtn.addEventListener("click", runCode);
    }

    const clearBtn = document.getElementById("pg-clear");
    if (clearBtn) {
      clearBtn.addEventListener("click", clearOutput);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
