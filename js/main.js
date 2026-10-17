const opts = { actions: false, renderer: "svg", config: { title: { anchor: "start" } } };

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

charts.forEach(([el, url]) => vegaEmbed(el, url, opts).catch(err => console.error(url, err)));
