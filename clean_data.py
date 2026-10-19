"""Cleans ABS Schools 2025 and ACARA school data into the small CSVs the site loads.

Run:   python3 clean_data.py           reads raw/, writes data/
Check: python3 clean_data.py --check   writes to data_check/ instead and compares every file with data/

Raw files (keep them in raw/, which is not uploaded to GitHub):
  ABS, Schools 2025, Table 42b  -> ABS_T42b_students_2006_2025.xlsx       (headcount enrolments, 2006-2025)
  ABS, Schools 2025, Table 46a  -> ABS_T46a_FTE_by_remoteness_2025.xlsx   (full-time equivalent students by remoteness)
  ACARA School Location 2025    -> ACARA_School_Location_2025.xlsx        (every school's location, sector, type)
  ACARA School Profile 2025     -> ACARA_School_Profile_2025.xlsx         (every school's 2025 enrolments)
  ACARA School Profile 2008-2025 -> ACARA_School_Profile_2008_2025.xlsx   (enrolments by year, for 2015)

Outputs used by the site:
  data/enrolments_national_by_sector.csv   charts 1-3
  data/enrolments_by_grade.csv             chart 7 (year-level heatmap)
  data/state_summary_2025.csv              charts 6 and 9
  data/sector_share_by_state_year.csv      charts 4, 5 and 8
  data/fte_by_remoteness_2025.csv          chart 14
  data/schools_web.csv                     charts 10-13
(data/state_labels.csv and data/geo/*.topojson are made by hand / in mapshaper, not by this script.)

Needs: pip install pandas openpyxl
"""
import os, re, sys
import pandas as pd

CHECK = '--check' in sys.argv
R, O = 'raw', ('data_check' if CHECK else 'data')
os.makedirs(O, exist_ok=True)

STATE = {'NSW': 'New South Wales', 'Vic.': 'Victoria', 'Vic': 'Victoria', 'Qld': 'Queensland', 'SA': 'South Australia',
         'WA': 'Western Australia', 'Tas.': 'Tasmania', 'Tas': 'Tasmania', 'NT': 'Northern Territory',
         'ACT': 'Australian Capital Territory'}
ABBR = {v: k.rstrip('.').upper() if k in ('NSW', 'SA', 'WA', 'NT', 'ACT') else k.rstrip('.') for k, v in STATE.items()}
strip = lambda s: re.sub(r'^[a-z]{1,2} ', '', str(s)).strip()   # remove ABS footnote letters, e.g. "a NSW"


def abs_table(fname, sheet_kw):
    """Read an ABS Schools data cube: find the data sheet, keep real data rows, tidy text and state names."""
    xl = pd.ExcelFile(f'{R}/{fname}')
    sh = [s for s in xl.sheet_names if sheet_kw in s][0]
    df = pd.read_excel(xl, sh, header=3)
    df = df[pd.to_numeric(df['Year'], errors='coerce').notna()].copy()
    df['Year'] = df['Year'].astype(int)
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].map(strip)
    df['State/Territory'] = df['State/Territory'].map(lambda s: STATE.get(s, s))
    return df


# ---------- ABS Table 42b: headcount enrolments, 2006-2025 ----------
t = abs_table('ABS_T42b_students_2006_2025.xlsx', 'Data table')
t = t.rename(columns={'Year': 'year', 'State/Territory': 'state', 'Affiliation (Gov/Cath/Ind)': 'sector',
                      'Year (Grade)': 'grade', 'All Full-time and Part-time Student count': 'students'})
t['state_abbr'] = t['state'].map(ABBR)
g = lambda cols: t.groupby(cols, as_index=False)['students'].sum()

# national totals by sector (charts 1-3)
g(['year', 'sector']).to_csv(f'{O}/enrolments_national_by_sector.csv', index=False)

# students by year level (chart 7)
gr = g(['year', 'state', 'state_abbr', 'sector', 'grade'])
ORDER = (['Pre-Year 1 (Foundation Year)'] + [f'Year {i}' for i in range(1, 7)]
         + ['Year 7 primary', 'Ungraded primary', 'Year 7 secondary'] + [f'Year {i}' for i in range(8, 13)] + ['Ungraded secondary'])
gr['grade_order'] = gr.grade.map({k: i for i, k in enumerate(ORDER)})
gr.sort_values(['year', 'state', 'sector', 'grade_order']).to_csv(f'{O}/enrolments_by_grade.csv', index=False)

# students by state, year and sector, one column per sector
s = g(['year', 'state', 'state_abbr', 'sector']).pivot_table(
    index=['state', 'state_abbr', 'year'], columns='sector', values='students').reset_index()
s['total'] = s[['Government', 'Catholic', 'Independent']].sum(axis=1)


def summary_row(st):
    """One row per state with 2006/2015/2025 totals, growth and sector shares (charts 6 and 9)."""
    d = s[s.state == st].set_index('year')
    a, b, c = d.loc[2025], d.loc[2015], d.loc[2006]
    return dict(state=st, state_abbr=a.state_abbr,
                students_2025=int(a.total), students_2015=int(b.total), students_2006=int(c.total),
                growth_2015_2025_pct=round((a.total / b.total - 1) * 100, 2),
                growth_2006_2025_pct=round((a.total / c.total - 1) * 100, 2),
                govt_share_2025_pct=round(a.Government / a.total * 100, 2),
                catholic_share_2025_pct=round(a.Catholic / a.total * 100, 2),
                independent_share_2025_pct=round(a.Independent / a.total * 100, 2),
                govt_share_2015_pct=round(b.Government / b.total * 100, 2),
                independent_share_2015_pct=round(b.Independent / b.total * 100, 2),
                govt_growth_2015_2025_pct=round((a.Government / b.Government - 1) * 100, 2),
                catholic_growth_2015_2025_pct=round((a.Catholic / b.Catholic - 1) * 100, 2),
                independent_growth_2015_2025_pct=round((a.Independent / b.Independent - 1) * 100, 2))


pd.DataFrame([summary_row(x) for x in sorted(s.state.unique())]).to_csv(f'{O}/state_summary_2025.csv', index=False)

# long form: one row per state, year and sector, with its share (charts 4, 5 and 8)
sl = s.melt(id_vars=['state', 'state_abbr', 'year', 'total'], value_vars=['Government', 'Catholic', 'Independent'],
            var_name='sector', value_name='students')
sl['share_pct'] = (sl.students / sl.total * 100).round(2)
sl.drop(columns='total').to_csv(f'{O}/sector_share_by_state_year.csv', index=False)

# ---------- ABS Table 46a: full-time equivalent students by remoteness, 2025 (chart 14) ----------
r = abs_table('ABS_T46a_FTE_by_remoteness_2025.xlsx', 'Data table')
r = r.rename(columns={'Year': 'year', 'State/Territory': 'state', 'Affiliation': 'sector',
                      'ASGS Remoteness Classification': 'remoteness', 'Total Student Count (FTE)': 'fte_students',
                      'Male Count (FTE)': 'fte_male', 'Female Count (FTE)': 'fte_female'})
r = r[r.state.isin(set(STATE.values())) & ~r.sector.str.contains('Total', case=False)
      & ~r.remoteness.str.contains('Total', case=False)]
r.groupby(['year', 'state', 'sector', 'remoteness'], as_index=False)[['fte_students', 'fte_male', 'fte_female']] \
 .sum().round(1).to_csv(f'{O}/fte_by_remoteness_2025.csv', index=False)

# ---------- ACARA: every school in 2025, with its 2015 enrolment (charts 10-13) ----------
loc = pd.read_excel(f'{R}/ACARA_School_Location_2025.xlsx', sheet_name=1)
prof = pd.read_excel(f'{R}/ACARA_School_Profile_2025.xlsx', sheet_name=1)
sch = loc[['ACARA SML ID', 'School Name', 'Suburb', 'State', 'School Sector', 'School Type', 'Latitude', 'Longitude',
           'ABS Remoteness Area Name', 'Local Government Area Name']].merge(
      prof[['ACARA SML ID', 'ICSEA', 'Total Enrolments']], on='ACARA SML ID', how='left')
sch.columns = ['id', 'name', 'suburb', 'state_abbr', 'sector', 'type', 'lat', 'lon', 'remoteness', 'lga', 'icsea', 'enrolments']
sch = sch.dropna(subset=['lat', 'lon', 'enrolments'])
sch['lat'] = sch.lat.round(4)
sch['lon'] = sch.lon.round(4)
sch['enrolments'] = sch.enrolments.astype(int)

# each school's 2015 enrolment, matched on its ACARA ID; no match = opened after 2015
hist = pd.read_excel(f'{R}/ACARA_School_Profile_2008_2025.xlsx', sheet_name=1,
                     usecols=['Calendar Year', 'ACARA SML ID', 'Total Enrolments'])
h15 = hist[hist['Calendar Year'] == 2015][['ACARA SML ID', 'Total Enrolments']] \
    .rename(columns={'ACARA SML ID': 'id', 'Total Enrolments': 'enrol_2015'})
w = sch[['name', 'suburb', 'state_abbr', 'sector', 'type', 'lat', 'lon', 'remoteness', 'lga', 'icsea', 'enrolments', 'id']] \
    .merge(h15, on='id', how='left')
w['status'] = w.enrol_2015.isna().map({True: 'New since 2015', False: 'Open in 2015'})
w['change_pct'] = ((w.enrolments / w.enrol_2015 - 1) * 100).round(0)
w['enrol_2015'] = w.enrol_2015.astype('Int64')
w['sector'] = w.sector.str[0]                                    # G / C / I keeps the file small; decoded in the specs
w = w[(w.lon > 112) & (w.lon < 154) & (w.lat > -44)]             # drop offshore territories (Christmas, Cocos, Norfolk, Lord Howe)
w.drop(columns=['id']).to_csv(f'{O}/schools_web.csv', index=False)

OUTPUTS = ['enrolments_national_by_sector.csv', 'enrolments_by_grade.csv', 'state_summary_2025.csv',
           'sector_share_by_state_year.csv', 'fte_by_remoteness_2025.csv', 'schools_web.csv']
for f in OUTPUTS:
    print(f'{O}/{f}: {os.path.getsize(f"{O}/{f}") // 1024} KB, {len(pd.read_csv(f"{O}/{f}"))} rows')

# ---------- --check: compare the rebuilt files with the ones the site uses ----------
if CHECK:
    print('\nComparing data_check/ with data/:')
    all_ok = True
    for f in OUTPUTS:
        new, old = pd.read_csv(f'data_check/{f}'), pd.read_csv(f'data/{f}')
        if list(new.columns) != list(old.columns) or len(new) != len(old):
            print(f'  DIFFERENT  {f}: columns or row count differ ({len(new)} vs {len(old)} rows)')
            all_ok = False
            continue
        try:
            pd.testing.assert_frame_equal(new, old, check_dtype=False, atol=0.05)
            print(f'  MATCH      {f}')
        except AssertionError as e:
            print(f'  DIFFERENT  {f}: {str(e).splitlines()[0]}')
            all_ok = False
    print('\nAll files match the raw data.' if all_ok else '\nSome files differ - see above.')
