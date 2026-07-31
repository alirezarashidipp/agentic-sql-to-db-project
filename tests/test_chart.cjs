const assert = require("node:assert/strict");
const test = require("node:test");

const {inspectChartRows} = require("../static/chart.js");

test("offers only charts supported by the returned row shape", () => {
  const grouped = [
    {DEPARTMENT: "MSW", TOTAL: 4},
    {DEPARTMENT: "MRM", TOTAL: 3},
    {DEPARTMENT: "SECURITY", TOTAL: 3},
  ];
  const chart = inspectChartRows(grouped);
  assert.deepEqual(chart.types, ["bar", "pie"]);
  assert.equal(chart.labelKey, "DEPARTMENT");
  assert.equal(chart.valueKey, "TOTAL");

  assert.equal(inspectChartRows([{TOTAL: 10}]), null);
  assert.equal(inspectChartRows([
    {DEPARTMENT: "MSW", TOTAL: "4"},
    {DEPARTMENT: "MRM", TOTAL: "3"},
  ]), null);
  assert.equal(inspectChartRows([
    {DEPARTMENT: "MSW", STATUS: "CODER", TOTAL: 4},
    {DEPARTMENT: "MRM", STATUS: "CODER", TOTAL: 3},
  ]), null);
  assert.equal(inspectChartRows([
    {DEPARTMENT: "MSW", TOTAL: 4},
    {DEPARTMENT: "MSW", TOTAL: 3},
  ]), null);
  assert.equal(inspectChartRows([
    {DEPARTMENT: "MSW", TOTAL: -1},
    {DEPARTMENT: "MRM", TOTAL: 3},
  ]), null);
  assert.deepEqual(inspectChartRows([
    {DEPARTMENT: "MSW", TOTAL: 0},
    {DEPARTMENT: "MRM", TOTAL: 3},
  ]).types, ["bar"]);

  const nineGroups = Array.from({length: 9}, (_, index) => ({
    LABEL: `Group ${index + 1}`,
    TOTAL: index + 1,
  }));
  assert.deepEqual(inspectChartRows(nineGroups).types, ["bar"]);
  assert.deepEqual(inspectChartRows([
    {LABEL: "A", TOTAL: Number.MAX_VALUE},
    {LABEL: "B", TOTAL: Number.MAX_VALUE},
  ]).types, ["bar"]);
  assert.equal(inspectChartRows([
    {LABEL: "A", TOTAL: 0},
    {LABEL: "B", TOTAL: 0},
  ]), null);
  assert.equal(inspectChartRows(Array.from({length: 21}, (_, index) => ({
    LABEL: `Group ${index + 1}`,
    TOTAL: index + 1,
  }))), null);
});
