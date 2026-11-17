import xlrd, json, os, re, glob
from config import R, work
b=xlrd.open_workbook(glob.glob(R+"/BKBSIN_Mandarin_C/*.xls")[0])
lists={}; cur=None
for s in b.sheets():
    for r in range(s.nrows):
        row=[str(v).strip() for v in s.row_values(r)]
        cells=[c for c in row if c]
        if not cells: continue
        m=[c for c in cells if re.fullmatch(r"练?\d[AB]",c)]
        if m: cur=m[0]; lists.setdefault(cur,[]); continue
        if re.fullmatch(r"\d+\.0",cells[0]) and cur and len(cells)>=3:
            n=int(float(cells[0])); kc=int(float(cells[-1])); kws=cells[1:-1]
            lists[cur].append(dict(n=n,raw=kws,kc=kc))
for k,v in lists.items(): print(k,len(v),[x['n'] for x in v][-1], sum(x['kc'] for x in v))
# Fix: the 2nd block on sheet "练1" is mislabeled "练2A" in the xls; it is practice list 1B.
lists["练1B"]=lists["练2A"][:10]; lists["练2A"]=lists["练2A"][10:]
json.dump(lists,open(work("xls_fixed.json"),"w"),ensure_ascii=False,indent=1)
