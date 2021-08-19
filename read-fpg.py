import io
import sys 
import struct
import numpy as np
import matplotlib.pyplot as plt


def FPG_Signature_Read(fname, showXY = True, showWV = True):

    vectores, nvectores, mvector, res, fs, coef, format, mod, nc, Fs= (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    get_uint16 = lambda ff : struct.unpack('H', ff.read(2))[0]
    get_uint32 = lambda ff : struct.unpack('I', ff.read(4))[0]

    with open(fname, 'rb') as f:
        byte = f.read(4)
        if byte != b'FPG ':
            raise AssertionError("The file is not FPG")
            
        hsize = get_uint16(f)
        ver = 2 if hsize in (48, 60) else 1
        format = get_uint16(f)

        if format == 4:
            m = get_uint16(f)
            can = get_uint16(f)

            Ts = get_uint32(f)
            print(Ts)
            res = get_uint16(f)
            f.seek(4, io.SEEK_CUR)
            coef = get_uint32(f)
            mvector = get_uint32(f)
            nvectores = get_uint32(f)
            nc = get_uint16(f)
            if ver == 2:
                Fs = get_uint32(f)
                mventana = get_uint32(f)
                msolapadas = get_uint32(f)

            f.seek(hsize - 12, io.SEEK_SET)
            datos = get_uint32(f)
            delta = get_uint32(f)
            ddelta = get_uint32(f)

            f.seek(hsize, io.SEEK_SET)
            string = 'd'
            if res == 8:
                string = 'B'
            elif res == 16:
                string = 'H'
            elif res == 32:
                string = 'f'

            sizes = {
                'B' : 1,
                'H' : 2,
                'f' : 4,
                'd' : 8
            }
            
            tam_tot = nvectores * can * mvector
            temp = struct.iter_unpack(string, f.read(tam_tot * sizes[string]))
            vectores = np.zeros((nvectores, mvector))

            for i in range(nvectores):
                for m in range(mvector):
                    vectores[i,m] = next(temp)[0]
        else:
            return
        f.close()

        x = vectores[:, 0]
        y = vectores[:, 1]
        z = vectores[:, 2]
        az = vectores[:, 3]
        bin = vectores[:, 4]
        pps = Fs

        if showXY:
            _, ax = plt.subplots(1, 1)
            p0 = min(z)
            ind_p0 = [i for i, v in enumerate(z) if v == p0 or v < 1]
            vnan = np.empty((len(ind_p0), 1))
            x2 = x
            x2[ind_p0] = vnan
            y2 = y
            y2[ind_p0] = vnan
            alto = max(y2) - min(y2)
            ancho = max(x2) - min(x2)
            relacion = alto / ancho
            ax.plot(x, y, 'k', linewidth=2)
            ax.set_yticks([])
            ax.set_xticks([])
            ax.set_position([0.05, 0.05, .9, .9])
            ax.set_title(fname)

        if showWV:
            _, axs = plt.subplots(5, 1, tight_layout=True, num=fname)
            for ax, d, l in zip(axs, [x, y, z, az, bin], ['X', 'Y', 'Pressure', 'Azimuth', 'Elevation']):
                ax.grid(True, which='both')
                ax.plot(d, 'k')
                ax.set_ylabel(l)
                ax.set(ylim=(min(d), max(d)))
                print((min(d), max(d)))
                
            plt.title(fname)
            plt.show()

        return x, y, z, az, bin, pps


if __name__ == '__main__':
    for fname in sys.argv[1:]:
        FPG_Signature_Read(fname)