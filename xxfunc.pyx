from tqdm import tqdm
import numpy
cimport numpy
cimport cython

cdef float sorting_index(list candles, float prec=1e-3):
   
    # Obtém séries de dados ordenadas de forma crescente e decrescente
    cdef numpy.ndarray y_alta = numpy.sort(candles)
    cdef numpy.ndarray y_queda = y_alta[::-1]

    # y_alta = numpy.sort(candles)
    # y_queda = y_alta[::-1]
    
    cdef float den =  numpy.sum(numpy.power((candles - numpy.mean(candles)),2))

    # Cálcula R2 de alta
    cdef float num_H =  numpy.sum(numpy.power((candles - y_alta),2))
    cdef float R2_alta  = (100*(1 - num_H/(den+prec))) if (100*(1 - num_H/(den+prec))) > 0 else 0.0
    
    # Cálcula R2 de queda
    cdef float num_L =  numpy.sum(numpy.power((candles - y_queda),2))
    cdef float R2_queda  = (100*(1 - num_L/(den+prec))) if (100*(1 - num_L/(den+prec))) > 0 else 0.0

    # Tomada de decisão: Qual a tendência preponderante
    if R2_alta > R2_queda:
        R2 = R2_alta
    else:
        R2 = -R2_queda
    return R2

def loop_sort_index(candles,N=130):
    pbar = tqdm(total=len(candles))
    sort_I = []
    for num in range(len(candles)):
        if num == 0:
            w_closes = [candles[0]]
        if num < N:
            w_closes = candles[:num]
        else:
            w_closes = candles[num-N:num]
    
        sort_I.append(sorting_index(w_closes))
        pbar.update(1)
    pbar.close()


def sorting_index(candles,  prec=1e-3, N=130):
    data=[]
    pbar = tqdm(total=len(candles))
   
    for num in range(len(candles)):
        if num == 0:
            w_closes = [candles[0]]
        if num < N:
            w_closes = candles[:num]
        else:
            w_closes = candles[num-N:num]

        # Obtém séries de dados ordenadas de forma crescente e decrescente
        y_alta = np.sort(w_closes)
        y_queda = y_alta[::-1]
        den =  np.sum(np.power((w_closes - np.mean(w_closes)),2))

        # Cálcula R2 de alta
        num_H =  np.sum(np.power((w_closes - y_alta),2))
        R2_alta  = (100*(1 - num_H/(den+prec))) if (100*(1 - num_H/(den+prec))) > 0 else 0
        
        # Cálcula R2 de queda
        num_L =  np.sum(np.power((w_closes - y_queda),2))
        R2_queda  = (100*(1 - num_L/(den+prec))) if (100*(1 - num_L/(den+prec))) > 0 else 0

        # Tomada de decisão: Qual a tendência preponderante
        if R2_alta > R2_queda:
            R2 = R2_alta
        else:
            R2 = -R2_queda
 
        data.append(R2)
        pbar.update(1)
    pbar.close()
    print(len(data))
    return data


    # with open('functions.csv', 'w') as file:
    # writer = csv.writer(file)
    # writer.writerow(sort)
    print(len(sort_I))
    return sort_I

