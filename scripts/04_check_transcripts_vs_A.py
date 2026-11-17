import soundfile as sf, numpy as np, glob, os, json, re
from config import R, work
def env(s,sr):
    hop=int(sr*0.01); n=len(s)//hop
    return np.array([np.sqrt(np.mean(s[i*hop:(i+1)*hop]**2)) for i in range(n)])
def trim(e):
    idx=np.where(20*np.log10(e*32768+1e-9)>20)[0]; return e[idx[0]:idx[-1]+1]
# A texts
txt=open(R+"/BKBSIN_Mandarin_A_Quiet/BKBMandarinList_output.txt").read()
At={}
for m in re.finditer(r"BKBMandarinList\[(\d+)\] = \"\"\"(.*?)\"\"\"",txt,re.S):
    L=int(m.group(1))
    for line in m.group(2).strip().splitlines():
        p=line.split(); At[(L,int(p[0]))]="".join(p[1:-1])
P=[]
for f in glob.glob(R+"/BKBSIN_Mandarin_A_Quiet/*/*.wav"):
    m=re.search(r"List(\d+)_Sentence-(\d+)",f); x,sr=sf.read(f)
    P.append((At[(int(m.group(1)),int(m.group(2)))],np.log(trim(env(x,sr))+1e-6)))
X=json.load(open(work("xls_fixed.json")))
M=json.load(open(work("c_match.json")))
amap={"L%d%s"%(i,s):"%d%s"%(i,s) for i in range(1,9) for s in "AB"}
amap.update({"Practice1A":"练1A","Practice1B":"练1B","Practice2A":"练2A","Practice2B":"练2B"})
for a,res in M.items():
    x,sr=sf.read(glob.glob(R+f"/BKBSIN_Mandarin_C/BKB-SIN {a}.wav")[0])
    ok=0;bad=[]
    for i,r in enumerate(res):
        le=np.log(env(x[int(r['sent_start']*sr):int(r['group'][1]*sr),0],sr)+1e-6)
        best=(-1,None)
        for t,pe in P:
            L=min(len(le),len(pe))
            if abs(len(le)-len(pe))>30: continue
            c=np.corrcoef(le[:L],pe[:L])[0,1]
            if c>best[0]: best=(c,t)
        xt=re.sub(r"[\s？?！!，,。]","","".join(X[amap[a]][i]['raw']))
        if best[0]>0.98:
            if best[1]==xt: ok+=1
            else: bad.append((i+1,best[1],xt,round(best[0],3)))
    print(a,"A-corpus ok",ok,"bad",bad)
