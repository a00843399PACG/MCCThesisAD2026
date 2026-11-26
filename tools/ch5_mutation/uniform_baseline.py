import numpy as np, sys
def values(W,P,c):
    N,n=W.shape
    orders=[np.tile(np.arange(n),(N,1)),
            np.argsort(W,axis=1,kind='stable'),
            np.argsort(-(P/W),axis=1,kind='stable'),
            np.argsort(-P,axis=1,kind='stable')]
    out=np.zeros((N,4))
    rows=np.arange(N)
    for h,o in enumerate(orders):
        res=np.full(N,c,dtype=np.int64);tot=np.zeros(N)
        for j in range(n):
            w=W[rows,o[:,j]];p=P[rows,o[:,j]]
            fit=w<=res;res-=np.where(fit,w,0);tot+=np.where(fit,p,0)
        out[:,h]=tot
    return out
def rates(n,c,wmax,pmax,N,rng):
    V=values(rng.integers(1,wmax+1,(N,n)),rng.integers(1,pmax+1,(N,n)).astype(float),c)
    win=[];lose=[]
    for h in range(4):
        o=np.delete(V,h,axis=1)
        win.append((V[:,h]>o.max(1)).mean());lose.append((V[:,h]<o.min(1)).mean())
    return win,lose
if __name__=='__main__':
    rng=np.random.default_rng(int(sys.argv[2]))
    b=int(sys.argv[1])
    for n in [50,100,200,500,1000]:
        for a in [0.05,0.25,0.5]:
            c=int(a*n*(2**b+1)/2)
            N=int(2e6//n) if n<=200 else int(1e6//n)
            w,l=rates(n,c,2**b,2**b,N,rng)
            print(n,a,c,N,' '.join(f'{x:.5f}' for x in w),'|',' '.join(f'{x:.5f}' for x in l),flush=True)
