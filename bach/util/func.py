import numpy as np
import csv
from tqdm import tqdm

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

def calc_correcao(N1,N2):
    SSC1 = 2/(N1+1) #rápida
    SSC2 = 2/(N2+1) #lenta
    a1= 1 - SSC1
    a2= 1 - SSC2
    return (a2-a1)/((1-a1)*(1-a2))
    
def calc_med_ema(candles,N):
    ema = np.zeros(len(candles))
    ema[0] = candles[0]
    SSC = 2/(N+1)
    for i in range(1,len(candles)):            
        ema[i] = ema[i-1]*(1-SSC) + candles[i]*SSC
    return ema

def MACD(candles,N1,N2,N3):
    correcao = calc_correcao(N1,N2)
    emaN1 = calc_med_ema(candles,N1)
    emaN2 = calc_med_ema(candles,N2)
    linha_MACD = (emaN1 - emaN2)/correcao # rápida - lenta (1 derivada)
    linha_sinal = calc_med_ema(linha_MACD,N3) # lenta
    return linha_sinal
 

