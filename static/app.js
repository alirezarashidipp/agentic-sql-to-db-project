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
const steps = [...document.querySelectorAll(".workflow li")];
const schemaTableName = document.querySelector("#schema-table-name");
const schemaFields = document.querySelector("#schema-fields");
const workspaceTitle = document.querySelector("#workspace-title");
const examples = document.querySelector("#examples");

function setWorkflow(status) {
  const reviewOnly = status === "incomplete" || status === "invalid";
  steps.forEach((step, index) => {
    step.classList.toggle("is-active", status === "loading" && index === 0);
    step.classList.toggle(
      "is-complete",
      status === "valid" || (reviewOnly && index === 0),
    );
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
  submit.classList.add("is-loading");
  buttonLabel.textContent = "Thinking";
  result.hidden = false;
  normalized.hidden = true;
  debug.hidden = true;
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
  } catch (error) {
    answer.className = "error";
    answer.textContent = error.message;
    setStatus("error");
    setWorkflow("error");
  } finally {
    submit.disabled = false;
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
