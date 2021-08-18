import sys 
import struct
import numpy as np

with open(sys.argv[1], 'rb') as f:
    #f.seek(4)
    byte = f.read(4)
    if byte != b'FPG ':
        raise AssertionError("The file is not FPG")

    hsize = int.from_bytes(f.read(1), 'little')
    ver = 2 if hsize in (48, 60) else 1
    f.seek(6)
    format = int.from_bytes(f.read(1), 'little')

    print(ver, format)

    if format == 4:
        m = int.from_bytes(f.read(1), 'little')
        can = int.from_bytes(f.read(1), 'little')
        f.seek(2)

        Ts = int.from_bytes(f.read(1), 'little')
        res = int.from_bytes(f.read(1), 'little')
        f.seek(4)
        coef = int.from_bytes(f.read(1), 'little')
        mvector = int.from_bytes(f.read(1), 'little')
        nvectores = int.from_bytes(f.read(1), 'little')
        nc = int.from_bytes(f.read(1), 'little')
        if ver == 2:
            Fs = int.from_bytes(f.read(1), 'little')
            mventana = int.from_bytes(f.read(1), 'little')
            msolapadas = int.from_bytes(f.read(1), 'little')

        f.seek(hsize - 12)
        datos = int.from_bytes(f.read(1), 'little')
        delta = int.from_bytes(f.read(1), 'little')
        ddelta = int.from_bytes(f.read(1), 'little')

        f.seek(hsize)
        print(res, hsize)
        string = 'd'
        if res == 8:
            string = 'h'
        elif res == 16:
            string = 'i'
        elif res == 32:
            string = 'f'
        
        print(nvectores, can, mvector)
        tam_tot = nvectores * can * mvector
        print(string, tam_tot)
        temp = struct.unpack(string, f.read(tam_tot))
        h = 0
        vectores = np.zeros((nvectores, mvector))
        for i in range(nvectores):
            for m in range(mvector):
                vectores[i,m] = temp[h]
                h += 1
    else:
        vectores = np.zeros((0, 0))
    f.close()

    x = vectores[:, 0]
    y = vectores[:, 1]
    z = vectores[:, 2]
    az = vectores[:, 3]
    bin = vectores[:, 4]
    pps = Fs