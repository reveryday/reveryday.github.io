(function () {
  const config = window.TRACKER_CONFIG || TRACKER_CONFIG || { workTargetHours: 8 };
  const entries = (window.TRACKER_ENTRIES || TRACKER_ENTRIES || [])
    .map((entry) => ({
      date: entry.date,
      workHours: Number(entry.workHours) || 0,
      studyHours: Number(entry.studyHours) || 0,
    }))
    .sort((a, b) => a.date.localeCompare(b.date));

  const entryByDate = new Map(entries.map((entry) => [entry.date, entry]));
  const dayMs = 24 * 60 * 60 * 1000;

  function pad(value) {
    return String(value).padStart(2, "0");
  }

  function toDateKey(date) {
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
  }

  function addDays(date, days) {
    const next = new Date(date);
    next.setDate(next.getDate() + days);
    return next;
  }

  function formatHours(value) {
    const rounded = Math.round(value * 10) / 10;
    return Number.isInteger(rounded) ? String(rounded) : rounded.toFixed(1);
  }

  function renderSummary() {
    const targetEl = document.querySelector("#work-target");
    const completionEl = document.querySelector("#work-completion");
    const studyTotalEl = document.querySelector("#study-total");
    const target = Number(config.workTargetHours) || 8;
    const recorded = entries.filter((entry) => entry.workHours > 0);
    const completed = recorded.filter((entry) => entry.workHours >= target).length;
    const studyTotal = entries.reduce((sum, entry) => sum + entry.studyHours, 0);

    if (targetEl) targetEl.textContent = `${formatHours(target)} h/day`;
    if (completionEl) {
      completionEl.textContent = recorded.length
        ? `${completed}/${recorded.length}`
        : "0/0";
    }
    if (studyTotalEl) studyTotalEl.textContent = `${formatHours(studyTotal)} h`;
  }

  function renderCalendar() {
    const calendar = document.querySelector("#work-calendar");
    if (!calendar) return;

    const target = Number(config.workTargetHours) || 8;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const start = addDays(today, -364);
    const offset = start.getDay();
    const firstCellDate = addDays(start, -offset);
    const totalCells = Math.ceil((365 + offset) / 7) * 7;

    calendar.innerHTML = "";
    for (let index = 0; index < totalCells; index += 1) {
      const date = addDays(firstCellDate, index);
      const key = toDateKey(date);
      const entry = entryByDate.get(key);
      const cell = document.createElement("span");
      const outOfRange = date < start || date > today;
      let state = "empty";

      if (!outOfRange && entry) {
        state = entry.workHours >= target ? "done" : "partial";
      }

      cell.className = `calendar-day ${state}${outOfRange ? " muted" : ""}`;
      cell.title = entry
        ? `${key}: work ${formatHours(entry.workHours)}h, study ${formatHours(entry.studyHours)}h`
        : `${key}: no record`;
      calendar.appendChild(cell);
    }
  }

  function weekKey(dateKey) {
    const date = new Date(`${dateKey}T00:00:00`);
    const day = (date.getDay() + 6) % 7;
    date.setDate(date.getDate() - day);
    return toDateKey(date);
  }

  function aggregate(view) {
    if (view === "day") {
      return entries.map((entry) => ({
        label: entry.date.slice(5),
        value: entry.studyHours,
      }));
    }

    const grouped = new Map();
    entries.forEach((entry) => {
      const key = view === "week" ? weekKey(entry.date) : entry.date.slice(0, 7);
      grouped.set(key, (grouped.get(key) || 0) + entry.studyHours);
    });

    return Array.from(grouped.entries()).map(([label, value]) => ({ label, value }));
  }

  function renderChart(view) {
    const chart = document.querySelector("#study-chart");
    if (!chart) return;

    const points = aggregate(view);
    if (!points.length) {
      chart.innerHTML = '<p class="meta">No study records yet.</p>';
      return;
    }

    const width = 720;
    const height = 280;
    const padLeft = 44;
    const padRight = 18;
    const padTop = 20;
    const padBottom = 38;
    const plotWidth = width - padLeft - padRight;
    const plotHeight = height - padTop - padBottom;
    const maxValue = Math.max(1, ...points.map((point) => point.value));
    const xStep = points.length > 1 ? plotWidth / (points.length - 1) : 0;

    const coords = points.map((point, index) => {
      const x = padLeft + xStep * index;
      const y = padTop + plotHeight - (point.value / maxValue) * plotHeight;
      return { ...point, x, y };
    });
    const path = coords
      .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`)
      .join(" ");
    const baseline = padTop + plotHeight;
    const midline = padTop + plotHeight / 2;
    const labelEvery = Math.max(1, Math.ceil(points.length / 6));

    chart.innerHTML = `
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Study hours ${view} chart">
        <line class="chart-grid" x1="${padLeft}" y1="${padTop}" x2="${width - padRight}" y2="${padTop}"></line>
        <line class="chart-grid" x1="${padLeft}" y1="${midline}" x2="${width - padRight}" y2="${midline}"></line>
        <line class="chart-axis" x1="${padLeft}" y1="${baseline}" x2="${width - padRight}" y2="${baseline}"></line>
        <line class="chart-axis" x1="${padLeft}" y1="${padTop}" x2="${padLeft}" y2="${baseline}"></line>
        <text class="chart-label" x="4" y="${padTop + 4}">${formatHours(maxValue)}h</text>
        <text class="chart-label" x="4" y="${baseline + 4}">0h</text>
        <path class="chart-line" d="${path}"></path>
        ${coords
          .map(
            (point) => `
              <circle class="chart-point" cx="${point.x.toFixed(1)}" cy="${point.y.toFixed(1)}" r="4">
                <title>${point.label}: ${formatHours(point.value)}h</title>
              </circle>`
          )
          .join("")}
        ${coords
          .filter((_, index) => index % labelEvery === 0 || index === coords.length - 1)
          .map(
            (point) => `
              <text class="chart-label" x="${point.x.toFixed(1)}" y="${height - 10}" text-anchor="middle">${point.label}</text>`
          )
          .join("")}
      </svg>`;
  }

  function bindTabs() {
    const buttons = Array.from(document.querySelectorAll(".chart-tabs button"));
    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        buttons.forEach((item) => item.setAttribute("aria-pressed", "false"));
        button.setAttribute("aria-pressed", "true");
        renderChart(button.dataset.view || "day");
      });
    });
  }

  renderSummary();
  renderCalendar();
  bindTabs();
  renderChart("day");
})();
