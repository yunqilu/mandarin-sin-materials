import soundfile as sf, numpy as np, glob, os, json, sys
from seg import segs
from config import R, work
def env(s,sr):
    hop=int(sr*0.01); n=len(s)//hop
    return np.array([np.sqrt(np.mean(s[i*hop:(i+1)*hop]**2)) for i in range(n)])
def groups(S,gap=1.2):
    G=[list(S[0])]
    for a,b in S[1:]:
        if a-G[-1][1]<gap: G[-1][1]=b
        else: G.append([a,b])
    return G
# B corpus
B=[]
for f in sorted(glob.glob(R+"/BKBSIN_Mandarin_B_Quiet/*/*.wav")):
    x,sr=sf.read(f); e=env(x[:,0],sr); idx=np.where(20*np.log10(e*32768+1e-9)>20)[0]
    e=e[idx[0]:idx[-1]+1]; B.append((os.path.basename(f),np.log(e+1e-6)))
out={}
for f in sorted(glob.glob(R+"/BKBSIN_Mandarin_C/BKB-SIN*.wav")):
    x,sr=sf.read(f); S=segs(x[:,0]*32768,sr); G=groups(S)
    name=os.path.basename(f)[8:-4]
    res=[]
    for a,b in G:
        # sentence = after carrier: take sub-segments; carrier is the first 0.5 s burst if group starts with ~0.5s seg
        sub=[s for s in S if s[0]>=a-1e-6 and s[1]<=b+1e-6]
        sa = sub[1][0] if len(sub)>1 and sub[0][1]-sub[0][0]<0.7 else sub[0][0]
        e=env(x[int(sa*sr):int(b*sr),0],sr); le=np.log(e+1e-6)
        best=(-1,None)
        for bn,be in B:
            L=min(len(le),len(be))
            if abs(len(le)-len(be))>40: continue
            c=np.corrcoef(le[:L],be[:L])[0,1]
            if c>best[0]: best=(c,bn)
        res.append(dict(group=[round(a,2),round(b,2)],sent_start=round(sa,2),n_sub=len(sub),match=best[1],r=round(best[0],3)))
    out[name]=res
    print(name,len(G),[ (r['match'][:6] if r['match'] else None, r['r']) for r in res])
json.dump(out,open(work("c_match.json"),"w"),ensure_ascii=False,indent=1)
