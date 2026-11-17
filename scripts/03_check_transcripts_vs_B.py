import json, os, glob, re
from config import R, work
X=json.load(open(work("xls_fixed.json")))
bt={}
for t in glob.glob(R+"/BKBSIN_Mandarin_B_Quiet/*/*.txt"):
    raw=open(t,'rb').read()
    try: s=raw.decode('gbk')
    except: s=raw.decode('utf-8','ignore')
    for line in s.splitlines()[1:]:
        p=line.split('\t')
        if len(p)>=4: bt[p[3].strip()+".wav"]=re.sub(r"[#\s？?！!，,。]","",p[2])
M=json.load(open(work("c_match.json")))
amap={"L%d%s"%(i,s):"%d%s"%(i,s) for i in range(1,9) for s in "AB"}
amap.update({"Practice1A":"练1A","Practice1B":"练1B","Practice2A":"练2A","Practice2B":"练2B"})
for a,res in M.items():
    xs=X[amap[a]]; ok=bad=0
    for i,r in enumerate(res):
        if r['r']>0.98:  # below ~0.98 envelope matches are unreliable
            bt_=bt.get(r['match']); xt=re.sub(r"[\s？?！!，,。]","","".join(xs[i]['raw']))
            if bt_ and bt_.replace("9","九")==xt.replace("9","九"): ok+=1
            else: bad+=1; print("  MISMATCH",a,i+1,bt_,xt,r['r'])
    print(a,"->",amap[a],"ok",ok,"bad",bad)
