import numpy as np

def sagitta(ca, height, pitch, surface_tension):
    _ca=float(ca)
    _height=float(height)
    _pitch=float(pitch)
    _surface_tension=float(surface_tension)

    a1=180.0-_ca
    a2=180-90-a1
    b=180-90-a2

    y=np.tan(np.deg2rad(_ca))*(_pitch/2)
    x=_pitch/2
    r=np.sqrt((x)**2+(y)**2)
    s=r-np.sqrt((r)**2-(_pitch)**2)
    return s