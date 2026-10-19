// Shared styling for every chart, so fonts and colours match without repeating them in 14 specs.
const theme = {
  background: null,                         // transparent: the white card behind shows through
  font: "Inter, system-ui, sans-serif",     // same typeface as the page text
  view: { stroke: null },                   // no box around each plot area
  title: { anchor: "start", fontSize: 15, fontWeight: 600, color: "#1b2333", subtitleColor: "#5a6475", subtitleFontSize: 12.5 }, // left-aligned titles
  axis: { labelColor: "#52514e", titleColor: "#52514e", domainColor: "#c9c6bd", tickColor: "#c9c6bd", gridColor: "#ecebe6" },   // soft grey axes and grid
  legend: { labelColor: "#52514e", titleColor: "#1b2333" },
  header: { labelColor: "#1b2333" }         // labels above small multiples / facets
};

// Options for every chart: no "..." export menu, draw as crisp SVG, apply the theme above.
const opts = { actions: false, renderer: "svg", config: theme };

// Which spec goes into which empty box in index.html (box id -> spec file), in page order.
const charts = [
  ["#v1",  "specs/01_sector_growth.vg.json"],
  ["#v2",  "specs/02_sector_students.vg.json"],
  ["#v3",  "specs/03_sector_waffle.vg.json"],
  ["#v4",  "specs/04_independent_share_small_multiples.vg.json"],
  ["#v5",  "specs/05_state_sector_marimekko.vg.json"],
  ["#v6",  "specs/06_independent_dumbbell.vg.json"],
  ["#v7",  "specs/07_year_level_sector_heatmap.vg.json"],
  ["#v8",  "specs/08_growth_choropleth_linked.vg.json"],
  ["#v9",  "specs/09_state_contribution_waterfall.vg.json"],
  ["#v10", "specs/10_school_growth_symbols.vg.json"],
  ["#v11", "specs/11_new_schools_dots.vg.json"],
  ["#v12", "specs/12_school_size_density.vg.json"],
  ["#v13", "specs/13_top_growth_lgas.vg.json"],
  ["#v14", "specs/14_remoteness_sector.vg.json"]
];

// Draw each chart into its box. If one spec fails, log which file it was so the others still load.
charts.forEach(([el, url]) => vegaEmbed(el, url, opts).catch(err => console.error(url, err)));
