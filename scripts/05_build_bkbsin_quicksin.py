import soundfile as sf, numpy as np, glob, os, json, re, csv
from config import R, work
OUT=R+"/BKBSIN_Mandarin_SIN"
X=json.load(open(work("xls_fixed.json")))
M=json.load(open(work("c_match.json")))
NOM=[21,18,15,12,9,6,3,0,-3,-6]
def tag(a):
    m=re.fullmatch(r"L(\d)([AB])",a)
    return (f"List{m.group(1)}{m.group(2)}", f"{m.group(1)}{m.group(2)}") if m else (a, "练"+a[-2:])
def clean_kw(k): return re.sub(r"[\s？?！!，,。、；;：:“”\"]","",k)
rows=[]; report=[]
for a,res in M.items():
    x,sr=sf.read(glob.glob(R+f"/BKBSIN_Mandarin_C/BKB-SIN {a}.wav")[0])
    mix=x[:,0]+x[:,1]
    nclip=int(np.sum(np.abs(mix)>0.999)); mix=np.clip(mix,-0.999,0.999)
    name,xk=tag(a); d=f"{OUT}/BKBSIN_Mandarin_{name}"; os.makedirs(d,exist_ok=True)
    G=[r['group'] for r in res]
    cuts=[0]+[ (G[i][1]+G[i+1][0])/2 for i in range(len(G)-1)]+[len(mix)/sr]
    lines=[]
    for i in range(10):
        a0=int(round(cuts[i]*sr)); a1=len(mix) if i==9 else int(round(cuts[i+1]*sr))
        fn=f"BKBSIN_Mandarin_{name}_Sentence{i+1}.wav"
        sf.write(f"{d}/{fn}",mix[a0:a1],sr,subtype="PCM_16")
        # measured SNR on active speech frames within sentence (excluding carrier)
        s0,s1=int(res[i]['sent_start']*sr),int(G[i][1]*sr); sp=x[s0:s1,0]; nz=x[s0:s1,1]
        hop=int(sr*0.02); fr=np.array([np.mean(sp[j:j+hop]**2) for j in range(0,len(sp)-hop,hop)])
        act=fr>np.max(fr)*10**(-30/10)
        idx=np.repeat(act,hop)[:len(sp)]
        snr=10*np.log10(np.mean(sp[:len(idx)][idx]**2)/np.mean(nz**2))
        kws=[clean_kw(k) for k in X[xk][i]['raw'] if clean_kw(k)]
        kws=[k.replace("9","九") for k in kws]
        text="".join(kws)
        rows.append(dict(List=name,Sentence=i+1,File=f"BKBSIN_Mandarin_{name}/{fn}",SNR_dB=NOM[i],Measured_SNR_dB=round(snr,1),
                         Start_s=round(cuts[i],3),End_s=round(cuts[i+1],3),Text=text,Keywords=" | ".join(kws),N_Keywords=X[xk][i]['kc']))
        lines.append(f"{i+1}\t{NOM[i]:+d} dB".replace("+0 ","0 ")+f"\t{text}\t{' / '.join(kws)}\t{X[xk][i]['kc']}")
    with open(f"{d}/BKBSIN_Mandarin_{name}.txt","w",encoding="utf-8") as f:
        f.write("Sentence\tSNR\tText\tKeywords\tN_Keywords\n"+"\n".join(lines)+"\n")
    report.append((name,nclip,[r['Measured_SNR_dB'] for r in rows[-10:]]))
with open(f"{OUT}/BKBSIN_Mandarin_transcripts.csv","w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in report: print(r)
