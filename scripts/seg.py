import soundfile as sf, numpy as np, glob, os, sys
def segs(s, sr, thr_db=20, min_gap=0.5, min_len=0.3):
    hop=int(sr*0.01); n=len(s)//hop
    e=np.array([np.sqrt(np.mean(s[i*hop:(i+1)*hop]**2)) for i in range(n)])
    db=20*np.log10(e+1e-12); act=db>thr_db
    out=[];i=0
    while i<n:
        if act[i]:
            j=i
            while j<n:
                # extend until gap >= min_gap
                k=j+1
                while k<n and not act[k]: k+=1
                if k-j-1>=min_gap*100 or k>=n: break
                j=k
            out.append((i*hop/sr,(j+1)*hop/sr)); i=j+1
        else: i+=1
    return [o for o in out if o[1]-o[0]>=min_len]
if __name__=="__main__":
    for f in sorted(glob.glob(sys.argv[1])):
        x,sr=sf.read(f,dtype='float64'); x=x*32768
        sp=x[:,0]; nz=x[:,1]
        S=segs(sp,sr)
        r=[]
        for a,b in S:
            i,j=int(a*sr),int(b*sr)
            snr=10*np.log10(np.mean(sp[i:j]**2)/np.mean(nz[i:j]**2))
            r.append(f"{a:.2f}-{b:.2f}:{snr:+.1f}")
        print(os.path.basename(f),len(x)/sr,len(S)); print("  ",r)
