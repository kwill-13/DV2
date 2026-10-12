"""Cleans ABS Schools 2025 + ACARA 2025 files into small tidy CSVs for Vega-Lite.
Run: python3 clean_data.py   (reads raw/, writes data/)"""
import pandas as pd, re, os
R, O = 'raw', 'data'; os.makedirs(O, exist_ok=True)
STATE = {'NSW':'New South Wales','Vic.':'Victoria','Vic':'Victoria','Qld':'Queensland','SA':'South Australia',
         'WA':'Western Australia','Tas.':'Tasmania','Tas':'Tasmania','NT':'Northern Territory','ACT':'Australian Capital Territory'}
ABBR = {v:k.rstrip('.').upper() if k in('NSW','SA','WA','NT','ACT') else k.rstrip('.') for k,v in STATE.items()}
strip = lambda s: re.sub(r'^[a-z]{1,2} ', '', str(s)).strip()   # ABS prefixes like "a NSW"

def abs_table(fname, sheet_kw):
    xl = pd.ExcelFile(f'{R}/{fname}')
    sh = [s for s in xl.sheet_names if sheet_kw in s][0]
    df = pd.read_excel(xl, sh, header=3)
    df = df[pd.to_numeric(df['Year'], errors='coerce').notna()].copy()
    df['Year'] = df['Year'].astype(int)
    for c in df.columns:
        if df[c].dtype == object: df[c] = df[c].map(strip)
    df['State/Territory'] = df['State/Territory'].map(lambda s: STATE.get(s, s))
    return df

# ---------- ABS Table 42b: headcount enrolments 2006-2025 ----------
t = abs_table('ABS_T42b_students_2006_2025.xlsx', 'Data table')
t = t.rename(columns={'Year':'year','State/Territory':'state','Affiliation (Gov/Cath/Ind)':'sector','Sex':'sex',
    'Aboriginal and Torres Strait Islander Status':'indigenous','School Level':'level','Year (Grade)':'grade',
    'All Full-time and Part-time Student count':'students'})
t['level'] = t['level'].str.replace(' School','')
t['state_abbr'] = t['state'].map(ABBR)
g = lambda cols: t.groupby(cols, as_index=False)['students'].sum()

g(['year','state','state_abbr','sector','level','sex']).to_csv(f'{O}/enrolments_by_state_sector_level_sex.csv', index=False)
gr = g(['year','state','state_abbr','sector','grade'])
ORDER = ['Pre-Year 1 (Foundation Year)']+[f'Year {i}' for i in range(1,7)]+['Year 7 primary','Ungraded primary','Year 7 secondary']+[f'Year {i}' for i in range(8,13)]+['Ungraded secondary']
gr['grade_order'] = gr.grade.map({k:i for i,k in enumerate(ORDER)})
gr.sort_values(['year','state','sector','grade_order']).to_csv(f'{O}/enrolments_by_grade.csv', index=False)
g(['year','state','state_abbr','indigenous']).to_csv(f'{O}/enrolments_by_indigenous_status.csv', index=False)
nat = g(['year','sector']); nat.to_csv(f'{O}/enrolments_national_by_sector.csv', index=False)

# state summary for choropleths (keyed on STATE_NAME in the GeoJSON)
s = g(['year','state','state_abbr','sector']).pivot_table(index=['state','state_abbr','year'], columns='sector', values='students').reset_index()
s['total'] = s[['Government','Catholic','Independent']].sum(axis=1)
def row(st):
    d = s[s.state==st].set_index('year'); a, b, c = d.loc[2025], d.loc[2015], d.loc[2006]
    return dict(state=st, state_abbr=a.state_abbr, students_2025=int(a.total), students_2015=int(b.total), students_2006=int(c.total),
        growth_2015_2025_pct=round((a.total/b.total-1)*100,2), growth_2006_2025_pct=round((a.total/c.total-1)*100,2),
        govt_share_2025_pct=round(a.Government/a.total*100,2), catholic_share_2025_pct=round(a.Catholic/a.total*100,2),
        independent_share_2025_pct=round(a.Independent/a.total*100,2),
        govt_share_2015_pct=round(b.Government/b.total*100,2), independent_share_2015_pct=round(b.Independent/b.total*100,2),
        govt_growth_2015_2025_pct=round((a.Government/b.Government-1)*100,2),
        catholic_growth_2015_2025_pct=round((a.Catholic/b.Catholic-1)*100,2),
        independent_growth_2015_2025_pct=round((a.Independent/b.Independent-1)*100,2))
summ = pd.DataFrame([row(x) for x in sorted(s.state.unique())])
summ.to_csv(f'{O}/state_summary_2025.csv', index=False)
# long form sector share per state per year (for small multiples / slider choropleth)
sl = s.melt(id_vars=['state','state_abbr','year','total'], value_vars=['Government','Catholic','Independent'], var_name='sector', value_name='students')
sl['share_pct'] = (sl.students/sl.total*100).round(2)
sl.drop(columns='total').to_csv(f'{O}/sector_share_by_state_year.csv', index=False)

# ---------- ABS Table 46a: FTE by remoteness 2025 ----------
r = abs_table('ABS_T46a_FTE_by_remoteness_2025.xlsx', 'Data table')
r = r.rename(columns={'Year':'year','State/Territory':'state','Affiliation':'sector','ASGS Remoteness Classification':'remoteness',
    'Total Student Count (FTE)':'fte_students','Male Count (FTE)':'fte_male','Female Count (FTE)':'fte_female'})
r = r[r.state.isin(set(STATE.values())) & ~r.sector.str.contains('Total', case=False) & ~r.remoteness.str.contains('Total', case=False)]
r.groupby(['year','state','sector','remoteness'], as_index=False)[['fte_students','fte_male','fte_female']].sum().round(1)\
 .to_csv(f'{O}/fte_by_remoteness_2025.csv', index=False)

# ---------- ABS Table 66a: participation rates ----------
p = abs_table('ABS_T66a_participation_rates_2011_2025.xlsx', 'Data table')
p.columns = ['year','state','sex','age','participation_rate_ft_pt','participation_rate_ft']
p['state'] = p.state.replace({'Aust.':'Australia'})
p.to_csv(f'{O}/participation_rates_6_19.csv', index=False)

# ---------- ABS Table 53a: student-teacher ratio ----------
q = abs_table('ABS_T53a_student_teacher_ratio_2006_2025.xlsx', 'Data table')
q.columns = ['year','state','sector','level','student_teacher_ratio']
q['level'] = q['level'].str.replace(' School','')
q.to_csv(f'{O}/student_teacher_ratio.csv', index=False)

# ---------- ACARA: every school, 2025, with lat/long ----------
loc = pd.read_excel(f'{R}/ACARA_School_Location_2025.xlsx', sheet_name=1)
prof = pd.read_excel(f'{R}/ACARA_School_Profile_2025.xlsx', sheet_name=1)
sch = loc[['ACARA SML ID','School Name','Suburb','State','School Sector','School Type','Latitude','Longitude',
           'ABS Remoteness Area Name','Local Government Area Name']].merge(
      prof[['ACARA SML ID','ICSEA','Total Enrolments','Girls Enrolments','Boys Enrolments','Indigenous Enrolments (%)']], on='ACARA SML ID', how='left')
sch.columns = ['id','name','suburb','state_abbr','sector','type','lat','lon','remoteness','lga','icsea','enrolments','girls','boys','indigenous_pct']
sch = sch.dropna(subset=['lat','lon','enrolments'])
sch['lat'] = sch.lat.round(4); sch['lon'] = sch.lon.round(4)
sch['enrolments'] = sch.enrolments.astype(int)
sch.to_csv(f'{O}/schools_2025.csv', index=False)

# ACARA history: school-level enrolment change 2015 -> 2025 (same school ID in both years)
hist = pd.read_excel(f'{R}/ACARA_School_Profile_2008_2025.xlsx', sheet_name=1, usecols=['Calendar Year','ACARA SML ID','Total Enrolments'])
h = hist[hist['Calendar Year'].isin([2015,2025])].pivot_table(index='ACARA SML ID', columns='Calendar Year', values='Total Enrolments').dropna()
h.columns = ['enrol_2015','enrol_2025']; h = h.reset_index().rename(columns={'ACARA SML ID':'id'})
ch = sch[['id','name','suburb','state_abbr','sector','type','lat','lon','remoteness','lga']].merge(h, on='id')
ch['change'] = (ch.enrol_2025-ch.enrol_2015).astype(int)
ch['change_pct'] = ((ch.enrol_2025/ch.enrol_2015-1)*100).round(1)
ch[['enrol_2015','enrol_2025']] = ch[['enrol_2015','enrol_2025']].astype(int)
ch.to_csv(f'{O}/schools_enrolment_change_2015_2025.csv', index=False)

# LGA / remoteness rollups from ACARA (for tables or LGA choropleth if you add LGA boundaries)
sch.groupby(['state_abbr','lga','sector'], as_index=False).agg(schools=('id','count'), enrolments=('enrolments','sum'))\
   .to_csv(f'{O}/lga_enrolments_by_sector_2025.csv', index=False)

for f in sorted(x for x in os.listdir(O) if x.endswith('.csv')): print(f, os.path.getsize(f'{O}/{f}')//1024, 'KB', len(pd.read_csv(f'{O}/{f}')), 'rows')

# ---------- Slim web file: every 2025 school + its 2015 enrolment (blank = opened after 2015) ----------
h15 = hist[hist['Calendar Year']==2015][['ACARA SML ID','Total Enrolments']].rename(columns={'ACARA SML ID':'id','Total Enrolments':'enrol_2015'})
w = sch[['name','suburb','state_abbr','sector','type','lat','lon','remoteness','lga','icsea','enrolments','id']].merge(h15, on='id', how='left')
w['status'] = w.enrol_2015.isna().map({True:'New since 2015', False:'Open in 2015'})
w['change_pct'] = ((w.enrolments/w.enrol_2015-1)*100).round(0)
w['enrol_2015'] = w.enrol_2015.astype('Int64')
w['sector'] = w.sector.str[0]          # G / C / I to keep the file small (decoded in Vega-Lite)
w = w[(w.lon>112)&(w.lon<154)&(w.lat>-44)]   # drop offshore territories (Christmas, Cocos, Norfolk, Lord Howe Is.)
w.drop(columns=['id']).to_csv(f'{O}/schools_web.csv', index=False)
print('schools_web', len(w), 'new since 2015:', (w.status=='New since 2015').sum(), 'students in new schools:', w.loc[w.status=='New since 2015','enrolments'].sum())
