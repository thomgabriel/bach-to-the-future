from tqdm import tqdm
import numpy

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
        y_alta = numpy.sort(w_closes)
        y_queda = y_alta[::-1]
        den =  numpy.sum(numpy.power((w_closes - numpy.mean(w_closes)),2))

        # Cálcula R2 de alta
        num_H =  numpy.sum(numpy.power((w_closes - y_alta),2))
        R2_alta  = (100*(1 - num_H/(den+prec))) if (100*(1 - num_H/(den+prec))) > 0 else 0
        
        # Cálcula R2 de queda
        num_L =  numpy.sum(numpy.power((w_closes - y_queda),2))
        R2_queda  = (100*(1 - num_L/(den+prec))) if (100*(1 - num_L/(den+prec))) > 0 else 0

        # Tomada de decisão: Qual a tendência preponderante
        if R2_alta > R2_queda:
            R2 = R2_alta
        else:
            R2 = -R2_queda
 
        data.append(R2)
        pbar.update(1)
    pbar.close()
    return data
