// Shared styling for every chart: same type pairing and ink colours as the page, without repeating them in 14 specs.
const theme = {
  background: null,                                   // transparent: the paper shows through
  font: "IBM Plex Sans, system-ui, sans-serif",            // sans-serif for all chart content, as on the page
  view: { stroke: null },                             // no box around each plot area
  title: { anchor: "start", font: "Instrument Serif, Georgia, serif", fontSize: 22, fontWeight: 400, color: "#161513",
           subtitleFont: "IBM Plex Sans, system-ui, sans-serif", subtitleFontSize: 13, subtitleColor: "#57534b", subtitlePadding: 4 }, // serif title, sans-serif subtitle
  axis: { labelFont: "IBM Plex Sans, system-ui, sans-serif", labelFontSize: 11.5, labelColor: "#57534b",
          titleFont: "IBM Plex Sans, system-ui, sans-serif", titleFontSize: 12.5, titleFontWeight: 400, titleColor: "#57534b",
          domainColor: "#161513", tickColor: "#161513", gridColor: "#ddd7cb" },   // ink axis lines, faint grid
  legend: { labelFont: "IBM Plex Sans, system-ui, sans-serif", labelFontSize: 12.5, labelColor: "#57534b",
            titleFont: "IBM Plex Sans, system-ui, sans-serif", titleFontSize: 12.5, titleFontWeight: 600, titleColor: "#161513" },
  header: { labelFont: "IBM Plex Sans, system-ui, sans-serif", labelFontSize: 15, labelColor: "#161513" }   // labels above small multiples / facets
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

// Turn every <i data-lucide="name"> into its icon.
if (window.lucide) lucide.createIcons();

// Fade blocks in as they scroll into view. The class is added here, so without JavaScript everything just shows.
const revealObserver = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); revealObserver.unobserve(e.target); } });
}, { threshold: 0.12 });
document.querySelectorAll(".chapter-head, .lede, .viz, .row .text, .pair, .takeaways li, .figures").forEach(el => {
  el.classList.add("reveal");
  revealObserver.observe(el);
});
