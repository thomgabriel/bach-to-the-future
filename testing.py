import csv
import multi

with open('data.csv' , 'r') as file:
    readcsv = csv.reader(file, delimiter=',')
    candles= [row for row in readcsv]
    closes= [float(x) for x in candles[0]]

num = round(len(closes)/2)
half1 = closes[:num]
half2 = closes[num:]

# with open('functions.csv', 'w') as file:
#     writer = csv.writer(file)
#     writer.writerow(multi.sorting_index(closes))

import multiprocessing

pool = multiprocessing.Pool(8)
x = pool.apply(multi.sorting_index,[closes]) 
pool.close()
 
# for close in y:
#     x.append(close)
print(len(x))

with open('functions2.csv', 'w') as file:
    writer = csv.writer(file)
    writer.writerow(x)