// Shared styling for every chart: sans-serif type and ink colours as on the page, without repeating them in 14 specs.
const theme = {
  background: null,                                   // transparent: the paper shows through
  font: "IBM Plex Sans, system-ui, sans-serif",            // sans-serif for all chart content, as on the page
  view: { stroke: null },                             // no box around each plot area
  title: { anchor: "start", font: "IBM Plex Sans, system-ui, sans-serif", fontSize: 17, fontWeight: 600, color: "#161513",
           subtitleFont: "IBM Plex Sans, system-ui, sans-serif", subtitleFontSize: 13, subtitleColor: "#57534b", subtitlePadding: 4 }, // sans-serif title (semibold) and subtitle
  axis: { labelFont: "IBM Plex Sans, system-ui, sans-serif", labelFontSize: 11, labelColor: "#57534b",
          titleFont: "IBM Plex Sans, system-ui, sans-serif", titleFontSize: 13, titleFontWeight: 400, titleColor: "#57534b",
          domainColor: "#161513", tickColor: "#161513", gridColor: "#e2ddd2" },   // ink axis lines, faint grid
  legend: { labelFont: "IBM Plex Sans, system-ui, sans-serif", labelFontSize: 13, labelColor: "#57534b",
            titleFont: "IBM Plex Sans, system-ui, sans-serif", titleFontSize: 13, titleFontWeight: 600, titleColor: "#161513" },
  header: { labelFont: "IBM Plex Sans, system-ui, sans-serif", labelFontSize: 13, labelFontWeight: 600, labelColor: "#161513" }   // labels above small multiples / facets
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

// Bump this (and the ?v= in index.html) after changing the files, so browsers fetch the new copies instead of cached ones.
const version = 14;

// Small multiples and side-by-side views can't use width "container", so their specs have fixed widths.
// On two-column screens these are stretched to fill their box exactly. width(spec) = the part that takes up the extra space.
const twoCols = window.matchMedia("(min-width: 861px)");
const gap = () => parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--gap"));
const fitted = {
  "#v4":  { width: s => s.spec, parts: 5 },          // five maps in a row share the extra space
  "#v12": { width: s => s.spec, parts: 1 },
  "#v8":  { width: s => s.hconcat[1], parts: 1,       // the area chart takes the extra space, after...
            prepare: (s, box) => {                    // ...the map is sized to the left column, so the area chart starts on the right column
              const col = (box.clientWidth + 8 - gap()) / 2;   // 8 = the .viz left padding
              s.hconcat[0].width = col - 13;          // minus the .viz padding (8) and Vega's own padding (5)
              s.spacing = gap();
            } }
};

// Draw one chart. Fitted charts are drawn, measured and redrawn (up to 3 times) until they fill the box.
async function draw(el, url) {
  const fit = fitted[el];
  if (!fit || !twoCols.matches) return vegaEmbed(el, `${url}?v=${version}`, opts);
  const box = document.querySelector(el);
  const spec = await (await fetch(`${url}?v=${version}`)).json();
  if (fit.prepare) fit.prepare(spec, box);
  let result = await vegaEmbed(el, spec, opts);
  for (let i = 0; i < 4; i++) {
    const spare = box.clientWidth - parseFloat(box.querySelector("svg").getAttribute("width"));
    if (spare >= 0 && spare < 3) break;              // fits, with at most 3px to spare
    const part = fit.width(spec);
    part.width = Math.floor(part.width + (spare - 1) / fit.parts);   // round down so it never ends up too wide
    result.finalize();
    result = await vegaEmbed(el, spec, opts);
  }
  return result;
}

// Draw each chart into its box. If one spec fails, log which file it was so the others still load.
charts.forEach(([el, url]) => draw(el, url).catch(err => console.error(url, err)));

// Refit the stretched charts when the window width changes.
let lastWidth = innerWidth, resizeTimer;
addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    if (innerWidth === lastWidth) return;
    lastWidth = innerWidth;
    charts.filter(([el]) => fitted[el]).forEach(([el, url]) => draw(el, url).catch(err => console.error(url, err)));
  }, 250);
});

// Fade blocks in as they scroll into view. The class is added here, so without JavaScript everything just shows.
const revealObserver = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add("in"); revealObserver.unobserve(e.target); } });
}, { threshold: 0.12 });
document.querySelectorAll(".chapter-head, .lede, .viz, .row .text, .pair, .figures").forEach(el => {
  el.classList.add("reveal");
  revealObserver.observe(el);
});
