"""Cara (caja yolo + 68 puntos 2dfan4) en cada fotograma de un vídeo 1080x1920 -> npz."""
import subprocess, sys, numpy as np, cv2, onnxruntime as ort
cv2.setNumThreads(2)
MOD='/tmp/claude-0/-home-user-mi-tienda-shopify/684840b5-c1b1-582f-bcd6-bf822ef2e72f/scratchpad/modelos'
_S={}
def ses(n):
    if n not in _S:
        so=ort.SessionOptions(); so.intra_op_num_threads=2; so.inter_op_num_threads=1; so.log_severity_level=3
        _S[n]=ort.InferenceSession(f'{MOD}/{n}.onnx',so,providers=['CPUExecutionProvider'])
    return _S[n]
def yolo(bgr, umbral=0.5):
    h,w=bgr.shape[:2]; e=640/max(h,w); l=np.zeros((640,640,3),np.uint8)
    p=cv2.resize(bgr,(round(w*e),round(h*e)),interpolation=cv2.INTER_AREA); l[:p.shape[0],:p.shape[1]]=p
    x=((l.astype(np.float32)-127.5)/128).transpose(2,0,1)[None]
    o=ses('yoloface_8n').run(None,{'input':x})[0][0].T; o=o[o[:,4]>umbral]
    if not len(o): return None
    m=o[np.argmax(o[:,2]*o[:,3]*o[:,4])]; cx,cy,bw,bh=m[:4]/e
    return np.array([cx-bw/2,cy-bh/2,cx+bw/2,cy+bh/2],np.float32)
def fan68(bgr, caja):
    esc=195/max(caja[2]-caja[0],caja[3]-caja[1],1); tr=(256-(caja[:2]+caja[2:])*esc)*0.5
    M=np.array([[esc,0,tr[0]],[0,esc,tr[1]]],np.float32)
    c=cv2.warpAffine(bgr,M,(256,256),flags=cv2.INTER_AREA if esc<1 else cv2.INTER_LINEAR)
    lm,hm=ses('2dfan4').run(None,{'input':(c.transpose(2,0,1).astype(np.float32)/255)[None]})
    lm=lm[0,:,:2]/64*256; Mi=cv2.invertAffineTransform(M); return lm@Mi[:,:2].T+Mi[:,2]
if __name__=='__main__':
    f,out=sys.argv[1],sys.argv[2]; W,H=1080,1920
    p=subprocess.Popen(['ffmpeg','-v','error','-i',f,'-vf','scale=1080:1920:in_color_matrix=bt709,format=bgr24','-f','rawvideo','-'],stdout=subprocess.PIPE)
    cajas=[]; lms=[]
    while True:
        b=p.stdout.read(W*H*3)
        if len(b)<W*H*3: break
        fr=np.frombuffer(b,np.uint8).reshape(H,W,3); c=yolo(fr)
        if c is None: cajas.append(np.full(4,np.nan)); lms.append(np.full((68,2),np.nan)); continue
        cajas.append(c); lms.append(fan68(fr,c))
    np.savez(out,caja=np.array(cajas),lm=np.array(lms)); print(len(cajas))
