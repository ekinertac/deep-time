/*
 * curves.js: the three time series the chart page plots.
 *
 * WHAT THESE ARE: a hand-built synthesis of published reconstructions, resampled
 * onto a common age grid so three quantities on wildly different scales can be
 * read against one shared time axis. They are NOT one dataset and NOT a
 * published compilation. Treat them as schematic: the shapes, the crossings and
 * the order of events are the claim; individual values are not precise, and the
 * pre-Devonian oxygen curve in particular is model output that different groups
 * disagree about by a factor of two. chart.html states this in the open.
 *
 * Broad provenance: oxygen follows the shape of geochemical carbon–sulfur models
 * (the GEOCARBSULF family); CO₂ follows proxy compilations (stomatal density,
 * boron isotopes, paleosols); temperature follows mean-global reconstructions
 * with the known excursions (Huronian, Sturtian, Marinoan, Hirnantian,
 * end-Permian, Cenomanian–Turonian, PETM) placed explicitly.
 *
 * Shape: [ageMa, value], strictly descending in age. Consumed by assets/chart.js,
 * which splits every series at the 539 Ma scale break so no line is drawn across
 * it. Era boundaries come from ERAS in assets/data.js, not from here.
 */

/* Atmospheric oxygen, percent of the atmosphere by volume. */
const O2 = [
  [4540, 0], [4000, 0], [3000, 0], [2600, 0.001], [2450, 0.02], [2400, 1.5],
  [2300, 2], [2000, 1.5], [1600, 1], [1200, 1], [900, 1.5], [750, 2], [700, 3],
  [635, 4], [600, 6], [560, 8], [541, 11], [520, 13], [500, 14], [485, 14],
  [460, 15], [444, 15], [430, 15], [419, 16], [400, 17], [380, 18], [360, 21],
  [350, 25], [340, 29], [320, 33], [305, 35], [299, 34], [290, 32], [275, 29],
  [260, 24], [252, 16], [250, 14], [245, 13], [240, 12], [230, 13], [220, 14],
  [210, 15], [201, 16], [190, 17], [180, 18], [160, 19], [150, 20], [130, 21],
  [120, 22], [100, 24], [90, 25], [80, 26], [70, 25], [66, 24], [56, 23],
  [50, 23], [40, 22], [34, 22], [23, 21], [10, 21], [0, 20.9],
];

/* Carbon dioxide, ppm. Plotted on a log axis: the range spans three orders of
   magnitude. Starts at 4,000 Ma: Hadean CO₂ may have reached ~100 bar, which is
   off the top of any scale that can also show 425 ppm. */
const CO2 = [
  [4000, 200000], [3500, 120000], [3000, 60000], [2500, 30000], [2000, 12000],
  [1500, 7000], [1000, 4500], [800, 4500], [700, 5000], [635, 5000], [541, 5000],
  [500, 4500], [485, 4300], [460, 4000], [444, 3800], [430, 3400], [419, 3000],
  [400, 2600], [380, 1900], [370, 1400], [360, 900], [350, 500], [340, 400],
  [320, 340], [305, 300], [299, 320], [290, 400], [275, 600], [260, 800],
  [252, 1600], [250, 2200], [245, 2400], [240, 2500], [230, 2400], [220, 2300],
  [210, 2200], [201, 2100], [190, 1900], [180, 1800], [160, 1500], [150, 1400],
  [130, 1300], [120, 1300], [100, 1100], [90, 1000], [80, 900], [70, 820],
  [66, 800], [58, 900], [56, 1600], [54, 1300], [50, 1200], [45, 1000],
  [40, 800], [34, 600], [30, 500], [23, 420], [15, 350], [10, 300], [5, 280],
  [0, 425],
];

/* Mean global surface temperature, °C. The sharp negative excursions are the
   glaciations; the sharp positive ones are the end-Permian and the PETM. */
const TEMP = [
  [4000, 55], [3500, 38], [3000, 32], [2600, 28], [2450, 25], [2400, -8],
  [2300, 22], [2000, 22], [1500, 22], [1000, 20], [800, 18], [720, -15],
  [700, -18], [660, 12], [650, -18], [640, -15], [635, 14], [600, 17],
  [560, 19], [541, 22], [520, 24], [500, 25], [485, 25], [470, 23], [460, 22],
  [450, 18], [445, 11], [443, 13], [430, 17], [419, 19], [400, 20], [380, 22],
  [370, 21], [360, 18], [350, 15], [340, 13], [320, 12], [305, 12], [299, 13],
  [290, 16], [275, 19], [260, 21], [252, 30], [251, 32], [250, 32], [245, 29],
  [240, 26], [230, 25], [220, 24], [210, 25], [201, 25], [190, 23], [180, 22],
  [160, 21], [150, 21], [130, 21], [120, 22], [100, 26], [93, 28], [85, 26],
  [80, 24], [70, 23], [66, 22], [58, 24], [56, 28], [54, 26], [50, 26],
  [45, 24], [40, 20], [34, 16], [30, 15], [23, 15], [15, 16], [10, 15],
  [5, 14], [3, 14], [0, 15],
];

/*
 * Panel definitions. Each panel is its own chart with exactly ONE series: three
 * quantities this different can never share a y-axis, and a second scale on one
 * plot would invent correlations that are not in the data.
 *
 * Colours are slots 1–3 of the reference categorical palette, dark steps. That
 * triple passes every gate under the all-pairs check on this surface (worst CVD
 * ΔE 9.4, worst normal-vision ΔE 20.9), so the panels stay distinguishable in
 * both normal and colour-deficient vision.
 */
const PANELS = [
  {
    key: 'o2',
    data: O2,
    title: 'Atmospheric oxygen',
    unit: '% of atmosphere',
    color: '#3987e5',
    scale: 'linear',
    min: 0,
    max: 40,
    ticks: [0, 10, 20, 30, 40],
    fmt: (v) => v.toFixed(v < 1 ? 2 : 0) + '%',
    // The one line on this page that decides everything before 430 Ma.
    rule: { at: 16, label: 'below 16% you lose consciousness' },
  },
  {
    key: 'co2',
    data: CO2,
    title: 'Carbon dioxide',
    unit: 'ppm, log scale',
    color: '#d95926',
    scale: 'log',
    min: 200,
    max: 300000,
    ticks: [1000, 10000, 100000],
    fmt: (v) => (v >= 1000 ? Math.round(v / 1000) + 'k' : Math.round(v)) + ' ppm',
    rule: { at: 425, label: 'today, 425 ppm' },
  },
  {
    key: 'temp',
    data: TEMP,
    title: 'Mean global temperature',
    unit: '°C',
    color: '#199e70',
    scale: 'linear',
    min: -25,
    max: 60,
    ticks: [-20, 0, 20, 40, 60],
    fmt: (v) => Math.round(v) + ' °C',
    rule: { at: 15, label: 'today, 15 °C' },
  },
];
