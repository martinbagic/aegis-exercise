function transpose(a) {
  return Object.keys(a[0]).map((c) => a.map((r) => r[c]));
}

let colorant = d3
  .scaleLinear()
  .domain([0, 1])
  .interpolate(d3.interpolateCubehelixLong)
  .range([d3.rgb("#0043de"), d3.rgb("#fc5a03")]);

function refitSVG(svg, bottom, top) {
  svg
    .attr("height", bottom.node().getBoundingClientRect().bottom)
    .attr("width", bottom.node().getBoundingClientRect().right);
}

function refreshStageNumber() {
  d3.select("#stats-stage").text(vars.recordNum + 1);
}
