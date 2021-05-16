let vars = {
  recordNum: null,
  recordNumMax: null,
  rawData: null,
  processedData: null,
  refreshing: null,
  counterData: null,
};

let params = {
  rectSize: 15,
  blockGap: 10,
  maturationGap: 15,
  whiteGap: 2,
  barHeight: 1000,
};

async function loadRawData() {
  return rawData;
}

// LOAD DATA ON BUTTON CLICK
d3.select("#button-load").on("click", loadData);

d3.select("input#json-file").on("keypress", function (event) {
  console.log(event);
  if (event.keyCode === 32 || event.keyCode === 13) {
    loadData();
  }
});

function aggregateFromCounter(data, attr, normalize = false) {
  function normaliz(a) {
    let suma = a.reduce((a, b) => a + b, 0);
    return a.map((i) => i / suma);
  }

  if (normalize == false) {
    return data.map((record) => record[attr].flat());
  } else {
    return data.map((record) => normaliz(record[attr].flat()));
  }
}

async function loadData() {
  // Load data and visualize with button
  d3.select("#button-load").classed("button-pressed", true);
  let filename = d3.select("input#json-file").node().value;
  let rawData = await d3.json(`json/${filename}`, d3.autoType);
  let counterData = await d3.json(`counter/${filename}`, d3.autoType);

  let processedData = {
    // gensurv: transpose(rawData.gensurv),
    // genrepr: transpose(rawData.genrepr),
    // phesurv: transpose(rawData.phesurv),
    // pherepr: transpose(rawData.pherepr),
    // deatheco: rawData.death_eco,
    // deathend: rawData.death_end,
    // deathgen: rawData.death_gen,
    gensurv: transpose(aggregateFromCounter(counterData, "gensurv")),
    genrepr: transpose(aggregateFromCounter(counterData, "genrepr")),
    phesurv: transpose(aggregateFromCounter(counterData, "phesurv")),
    pherepr: transpose(aggregateFromCounter(counterData, "pherepr")),
    age_at_birth: transpose(
      aggregateFromCounter(counterData, "age_at_birth", true)
    ),
    age_at_overshoot: transpose(
      aggregateFromCounter(counterData, "age_at_overshoot", true)
    ),
    age_at_genetic: transpose(
      aggregateFromCounter(counterData, "age_at_genetic", true)
    ),
    cumulative_ages: transpose(
      aggregateFromCounter(counterData, "cumulative_ages", true)
    ),
  };

  // Birth shift age by one
  processedData.age_at_birth.unshift(
    processedData.age_at_birth[processedData.age_at_birth.length - 1]
  );
  processedData.age_at_birth.pop();

  vars.recordNumMax = processedData.gensurv[0].length;
  vars.recordNum = vars.recordNumMax - 1;

  vars.rawData = rawData;
  vars.counterData = counterData;
  vars.processedData = processedData;

  plot();

  refreshStageNumber();

  console.log(rawData);

  // Loading is over
  d3.select("#button-load").classed("button-pressed", false);
}

function plot() {
  plotBars(d3.select("g#age_at_birth"), vars.processedData.age_at_birth);
  plotBars(
    d3.select("g#age_at_overshoot"),
    vars.processedData.age_at_overshoot
  );
  plotBars(d3.select("g#age_at_genetic"), vars.processedData.age_at_genetic);
  plotBars(
    d3.select("g#age_at_overshoot"),
    vars.processedData.age_at_overshoot
  );
  plotBars(d3.select("g#age_at_genetic"), vars.processedData.age_at_genetic);
  plotBars(d3.select("g#cumulative_ages"), vars.processedData.cumulative_ages);
  plotHeatTiles(d3.select("g#gensurv"), vars.processedData.gensurv);
  plotHeatTiles(d3.select("g#phesurv"), vars.processedData.phesurv, 1);
  plotHeatTiles(d3.select("g#pherepr"), vars.processedData.pherepr, 1);
  plotHeatTiles(d3.select("g#genrepr"), vars.processedData.genrepr);

  //   Reposition groups

  let delta = params.rectSize * vars.rawData.bitsperlocus + params.blockGap;

  d3.select("g#phesurv").attr("transform", `translate(0, ${delta})`);

  delta += params.rectSize + params.blockGap;

  d3.select("g#pherepr").attr("transform", `translate(0, ${delta})`);

  delta += params.rectSize + params.blockGap;

  d3.select("g#genrepr").attr("transform", `translate(0, ${delta})`);

  delta += params.rectSize * vars.rawData.bitsperlocus + params.blockGap;

  d3.select("g#age_at_birth").attr("transform", `translate(0, ${delta})`);

  // delta += params.barHeight + params.blockGap;

  d3.select("g#age_at_overshoot").attr("transform", `translate(0, ${delta})`);

  // delta += params.barHeight + params.blockGap;

  d3.select("g#age_at_genetic").attr("transform", `translate(0, ${delta})`);

  // delta += params.barHeight + params.blockGap;

  d3.select("g#cumulative_ages").attr("transform", `translate(0, ${delta})`);

  delta += params.barHeight + params.blockGap;

  //   Resize svg to fit plot exactly
  d3.select("svg")
    .attr("height", delta)
    .attr(
      "width",
      params.rectSize * vars.rawData.lifespan + params.maturationGap
    );
}

function plotHeatTiles(g, data, bitsperlocus = null) {
  // console.log("Plotting heat tiles", vars.recordNum);

  if (bitsperlocus == null) {
    bitsperlocus = vars.rawData.bitsperlocus;
  }

  let ddata = Array.from(data, (bit, i) => ({
    d: bit,
    i: i,
    bit: i % bitsperlocus,
    age: Math.floor(i / bitsperlocus) + 1,
  }));

  g.selectAll("rect")
    .data(ddata)
    .join(
      (enter) =>
        enter
          .append("rect")
          .classed("heat-tile", true)
          .attr("height", params.rectSize - params.whiteGap)
          .attr("width", params.rectSize - params.whiteGap)
          .attr("fill", (d) => colorant(d.d[vars.recordNum]))
          .attr("y", (d) => d.bit * params.rectSize)
          .attr(
            "x",
            (d) =>
              Math.floor(d.i / bitsperlocus) * params.rectSize +
              (d.age > vars.rawData.maturationage) * params.maturationGap
          )
          .on("mouseover", function (_, d) {
            let value = Math.round(d.d[vars.recordNum] * 100) + "%";
            d3.select("#stats-value").text(value);
            d3.select("#stats-age").text(d.age);
            d3.select("#stats-bit").text(d.bit);
          })
          .on("mouseout", function (_, d) {
            d3.select("#stats-value").text("value");
            d3.select("#stats-age").text("age");
            d3.select("#stats-bit").text("bit");
          }),
      (update) => update.attr("fill", (d) => colorant(d.d[vars.recordNum]))
    );
}

function plotBars(g, data) {
  g.selectAll("rect")
    .data(data)
    .join(
      (enter) =>
        enter
          .append("rect")
          .classed("bar", true)
          .attr("height", (d) => d[vars.recordNum] * params.barHeight)
          .attr("width", params.rectSize - params.whiteGap)
          .attr("fill", (d) => colorant(d[vars.recordNum]))
          .attr("y", 0)
          .attr(
            "x",
            (d, i) =>
              i * params.rectSize +
              (i >= vars.rawData.maturationage) * params.maturationGap
          )
          .on("mouseover", function (_, d) {
            let value = Math.round(d[vars.recordNum] * 100) + "%";
            d3.select("#stats-value").text(value);
          })
          .on("mouseout", function (_, d) {
            d3.select("#stats-value").text("value");
          }),
      (update) =>
        update
          .attr("fill", (d) => colorant(d[vars.recordNum]))
          .attr("height", (d) => d[vars.recordNum] * params.barHeight)
    );
}

d3.selectAll(".button-bars").on("click", function (event) {
  d3.selectAll(".bars-toggle").attr("display", "none");
  let gId = d3.select(event.target).attr("affect");
  d3.select(`#${gId}`).attr("display", "auto");
  d3.select(".button-bars-active").classed("button-bars-active", false);
  d3.select(event.target).classed("button-bars-active", true);
});

d3.selectAll(".bars-toggle").attr("display", "none");
d3.selectAll("#age_at_birth").attr("display", "auto");
d3.select("[affect=age_at_birth]").classed("button-bars-active", true);

loadData();

d3.select("#slider-knob")
  .style(
    "left",
    parseInt(d3.select("#panel-slider").style("width"), 10) - 18 + "px"
  )
  .call(
    d3
      .drag()
      .on("start", function (event) {
        console.log("yas");
      })
      .on("drag", function (event) {
        let minX = 20;
        let maxX = parseInt(d3.select("#panel-slider").style("width"), 10) - 8;
        let x = event.x;
        if (x < minX) x = minX;
        if (x > maxX) x = maxX;
        d3.select(this).style("left", x - 10 + "px");

        var recordNumScale = d3
          .scaleQuantize()
          .domain([minX, maxX])
          .range(d3.range(vars.recordNumMax));

        vars.recordNum = recordNumScale(x);
        plot();
        refreshStageNumber();
      })
      .on("end", function (event) {
        // d3.select("#stats-stage").text("stage");
      })
  );

// #button-reload

d3.select("#button-reload").on("click", function () {
  if (vars.refreshing == null) {
    console.log("Refreshing initiated");
    vars.refreshing = setInterval(loadData, 1000 * 5); // Every 5 seconds
    d3.select("#button-reload").classed("button-reload-on", true);
  } else {
    console.log("Refreshing aborted");
    clearInterval(vars.refreshing);
    vars.refreshing = null;
    d3.select("#button-reload").classed("button-reload-on", false);
  }
});

// // Refreshing

// d3.select("#button-refresh").on("click", () => refresh());

// // keep refreshing
// {
//   let keepRefreshing = null;
//   d3.select("#keepRefreshing").on("click", function () {
//     if (keepRefreshing == null) {
//       console.log("Refreshing initiated.");
//       keepRefreshing = setInterval(refresh, 1000 * 10);
//       d3.select(this).classed("buttonOn", true);
//     } else {
//       console.log("Refreshing aborted.");
//       clearInterval(keepRefreshing);
//       keepRefreshing = null;
//       d3.select(this).classed("buttonOn", false);
//     }
//   });
// }
