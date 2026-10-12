const opts = { actions: false, renderer: "svg" };

const charts = [
  ["#v1",  "specs/01_sector_trend.vg.json"],
  ["#v2",  "specs/10_sector_waffle.vg.json"],
  // ["#v3",  "specs/02_growth_choropleth_linked.vg.json"],
  // ["#v4",  "specs/03_independent_share_small_multiples.vg.json"],
  // ["#v5",  "specs/11_state_sector_marimekko.vg.json"],
  // ["#v6",  "specs/04_independent_dumbbell.vg.json"],
  // ["#v7",  "specs/05_school_growth_symbols.vg.json"],
  // ["#v8",  "specs/06_new_schools_dots.vg.json"],
  // ["#v9",  "specs/12_school_size_density.vg.json"],
  // ["#v10", "specs/07_top_growth_lgas.vg.json"],
  // ["#v11", "specs/08_grade_cohort_heatmap.vg.json"],
  // ["#v12", "specs/09_remoteness_sector.vg.json"],
  // ["#v13", "specs/13_state_contribution_waterfall.vg.json"],
];

charts.forEach(([el, url]) => vegaEmbed(el, url, opts).catch(err => console.error(url, err)));
