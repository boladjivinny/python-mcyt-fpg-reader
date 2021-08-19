import io
import sys 
import struct
import numpy as np
import matplotlib.pyplot as plt


def fpg_signature_read(fname, showXY = True, showWV = True):

    vectores, rows, cols, res, fs, coef, format, mod, nc, Fs= (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    get_uint16 = lambda ff : struct.unpack('H', ff.read(2))[0]
    get_uint32 = lambda ff : struct.unpack('I', ff.read(4))[0]

    with open(fname, 'rb') as f:
        type = f.read(4)
        if type != b'FPG ':
            raise AssertionError("The file is not FPG")
            
        hsize = get_uint16(f)
        ver = 2 if hsize in (48, 60) else 1
        format = get_uint16(f)

        if format == 4:
            m = get_uint16(f)
            can = get_uint16(f)

            Ts = get_uint32(f)
            res = get_uint16(f)
            f.seek(4, io.SEEK_CUR)
            coef = get_uint32(f)
            cols = get_uint32(f)
            rows = get_uint32(f)
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
            
            
            tam_tot = rows * can * cols
            temp = struct.iter_unpack(string, f.read(tam_tot * sizes[string]))
            vectores = np.zeros((rows, cols))

            for i in range(rows):
                for m in range(cols):
                    vectores[i,m] = next(temp)[0]
        else:
            return
        f.close()

        idx = np.argsort(vectores[:, 0])

        x = vectores[:, 0]
        y = vectores[:, 1]
        z = vectores[:, 2]
        az = vectores[:, 3]
        bin = vectores[:, 4]
        pps = Fs

        fig, axs = plt.subplots(5, 2, num=fname, tight_layout=True)
        if showXY:
            gs = axs[1, 0].get_gridspec()
            # remove the underlying axes
            for ax in axs[3:, 0]:
                ax.remove()
            ax = fig.add_subplot(gs[1:, 0])
            for i in range(4):
                axs[i, 0].axis('off')
            p0 = min(z)
            ind_p0 = [i for i, v in enumerate(z) if v == p0]
            vnan = np.empty((len(ind_p0), 1))
            x2 = x[idx]
            x2[ind_p0] = vnan
            y2 = y[idx]
            y2[ind_p0] = vnan
            alto = max(y2) - min(y2)
            ancho = max(x2) - min(x2)
            relacion = alto / ancho
            ax.plot(x, y, 'k', linewidth=2)
            ax.set_yticks([])
            ax.set_xticks([])
            ax.set_position([0.05, 0.05, .9, .9], which='active')
            ax.annotate('XY', xy=(0.05,0.95),xycoords='axes fraction',)

        if showWV:
            #_, axs = plt.subplots(5, 1, tight_layout=True, num=fname)
            for i, d, l in zip(range(5), [x, y, z, az, bin], ['X', 'Y', 'Pressure', 'Azimuth', 'Elevation']):
                ax = axs[i, 1]
                ax.grid(True, which='both')
                ax.plot(d, 'k', linewidth=1)
                #ax.legend(l)
                ax.annotate(l, xy=(0.01,1.1),xycoords='axes fraction', fontsize=8)
                ax.set(ylim=(min(d), max(d)))
        plt.show()

        return x, y, z, az, bin, pps


if __name__ == '__main__':
    for fname in sys.argv[1:]:
        fpg_signature_read(fname, True, True)