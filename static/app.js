const form = document.querySelector("#ask-form");
const question = document.querySelector("#question");
const submit = document.querySelector("#submit");
const buttonLabel = document.querySelector(".button-label");
const result = document.querySelector("#result");
const resultStatus = document.querySelector("#result-status");
const normalized = document.querySelector("#normalized");
const answer = document.querySelector("#answer");
const debug = document.querySelector("#debug");
const sql = document.querySelector("#sql");
const rows = document.querySelector("#rows");
const chartActions = document.querySelector("#chart-actions");
const chartPanel = document.querySelector("#chart-panel");
const chartTitle = document.querySelector("#chart-title");
const chartOutput = document.querySelector("#chart-output");
const chartButtons = [...document.querySelectorAll("[data-chart]")];
const steps = [...document.querySelectorAll(".workflow li")];
const schemaTableName = document.querySelector("#schema-table-name");
const schemaFields = document.querySelector("#schema-fields");
const workspaceTitle = document.querySelector("#workspace-title");
const examples = document.querySelector("#examples");
const chartColors = Array.from(
  {length: 8},
  (_, index) => `var(--color-chart-${index + 1})`,
);
const numberFormat = new Intl.NumberFormat();
let chartData = null;

function setWorkflow(status) {
  const reviewOnly = status === "incomplete" || status === "invalid";
  steps.forEach((step, index) => {
    const isActive = status === "loading" && index === 0;
    step.classList.toggle("is-active", isActive);
    step.classList.toggle(
      "is-complete",
      status === "valid" || (reviewOnly && index === 0),
    );
    if (isActive) {
      step.setAttribute("aria-current", "step");
    } else {
      step.removeAttribute("aria-current");
    }
  });
}

function setStatus(status) {
  const labels = {
    valid: "Validated",
    incomplete: "Needs details",
    invalid: "Out of scope",
    error: "Error",
  };
  resultStatus.className = `status status-${status}`;
  resultStatus.textContent = labels[status] || "Processing";
}

function chartElement(tag, className, text) {
  const element = document.createElement(tag);
  element.className = className;
  if (text !== undefined) {
    element.textContent = text;
  }
  return element;
}

function resetChart() {
  chartData = null;
  chartActions.hidden = true;
  chartPanel.hidden = true;
  chartOutput.replaceChildren();
  chartButtons.forEach((button) => {
    button.hidden = false;
    button.setAttribute("aria-pressed", "false");
  });
}

function offerCharts(dataRows) {
  chartData = window.inspectChartRows(dataRows);
  if (!chartData) {
    return;
  }

  chartButtons.forEach((button) => {
    button.hidden = !chartData.types.includes(button.dataset.chart);
  });
  chartActions.hidden = false;
}

function renderBarChart() {
  const chart = chartElement("div", "bar-chart");
  const maximum = Math.max(...chartData.items.map((item) => item.value));

  chartData.items.forEach((item) => {
    const row = chartElement("div", "bar-row");
    const label = chartElement("span", "bar-label", item.label);
    const track = chartElement("span", "bar-track");
    const fill = chartElement("span", "bar-fill");
    const value = chartElement("strong", "bar-value", numberFormat.format(item.value));
    fill.style.width = `${(item.value / maximum) * 100}%`;
    track.append(fill);
    row.append(label, track, value);
    chart.append(row);
  });

  return chart;
}

function renderPieChart() {
  const total = chartData.items.reduce((sum, item) => sum + item.value, 0);
  let start = 0;
  const stops = chartData.items.map((item, index) => {
    const end = index === chartData.items.length - 1
      ? 100
      : start + (item.value / total) * 100;
    const stop = `${chartColors[index]} ${start}% ${end}%`;
    start = end;
    return stop;
  });
  const chart = chartElement("div", "pie-chart");
  const graphic = chartElement("div", "pie-graphic");
  const legend = chartElement("div", "pie-legend");
  graphic.style.background = `conic-gradient(${stops.join(", ")})`;
  graphic.setAttribute("aria-hidden", "true");
  legend.setAttribute("role", "list");

  chartData.items.forEach((item, index) => {
    const row = chartElement("div", "pie-legend-row");
    row.setAttribute("role", "listitem");
    const swatch = chartElement("span", "pie-swatch");
    const label = chartElement("span", "pie-label", item.label);
    const percent = Math.round((item.value / total) * 100);
    const value = chartElement(
      "strong",
      "pie-value",
      `${numberFormat.format(item.value)} · ${percent}%`,
    );
    swatch.style.background = chartColors[index];
    row.append(swatch, label, value);
    legend.append(row);
  });

  chart.append(graphic, legend);
  return chart;
}

function renderChart(type) {
  if (!chartData || !chartData.types.includes(type)) {
    return;
  }

  chartTitle.textContent = `${type === "bar" ? "Bar" : "Pie"} chart · ${chartData.valueKey} by ${chartData.labelKey}`;
  chartOutput.replaceChildren(type === "bar" ? renderBarChart() : renderPieChart());
  chartPanel.hidden = false;
  chartButtons.forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.chart === type));
  });
}

chartActions.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-chart]");
  if (button && !button.hidden) {
    renderChart(button.dataset.chart);
  }
});

examples.addEventListener("click", (event) => {
  if (event.target.matches("button")) {
    const button = event.target;
    question.value = button.textContent;
    question.focus();
  }
});

question.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    form.requestSubmit();
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  submit.disabled = true;
  question.disabled = true;
  submit.classList.add("is-loading");
  buttonLabel.textContent = "Thinking";
  result.hidden = false;
  normalized.hidden = true;
  debug.hidden = true;
  resetChart();
  answer.className = "";
  answer.textContent = "Checking your question against the configured schema...";
  setWorkflow("loading");
  resultStatus.className = "status";
  resultStatus.textContent = "Processing";

  try {
    const response = await fetch("/ask", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question: question.value}),
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Request failed");
    }

    answer.textContent = data.answer;
    setStatus(data.status);
    setWorkflow(data.status);

    if (data.normalized_question !== data.question) {
      normalized.textContent = `↳ Understood as: ${data.normalized_question}`;
      normalized.hidden = false;
    }

    debug.hidden = !data.sql;
    sql.textContent = data.sql || "";
    rows.textContent = JSON.stringify(data.rows, null, 2);
    offerCharts(data.status === "valid" ? data.rows : []);
  } catch (error) {
    answer.className = "error";
    answer.textContent = error.message;
    setStatus("error");
    setWorkflow("error");
  } finally {
    submit.disabled = false;
    question.disabled = false;
    submit.classList.remove("is-loading");
    buttonLabel.textContent = "Run question";
  }
});

async function loadSchema() {
  const response = await fetch("/schema");
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Could not load the database schema.");
  }

  document.title = `${data.table} SQL Assistant`;
  schemaTableName.textContent = data.table;
  workspaceTitle.textContent = `Explore ${data.table} data`;
  question.maxLength = data.max_question_length;

  data.columns.forEach((column, index) => {
    const field = document.createElement("span");
    const number = document.createElement("b");
    number.textContent = String(index + 1).padStart(2, "0");
    field.append(number, ` ${column.name}`);
    field.title = `${column.description} Possible values: ${column.possible_values}`;
    schemaFields.append(field);
  });

  data.examples.forEach((example) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = example;
    examples.append(button);
  });

  if (!question.value && data.examples.length) {
    question.value = data.examples[0];
  }
}

loadSchema().catch((error) => {
  schemaTableName.textContent = "Schema unavailable";
  console.error(error);
});
