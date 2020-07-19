
actualPrice = 9500
init_margin = 1
margin = init_margin
leverage = 5
maker_fee= -0.00025
taker_fee = 0.00075
short_qtd = round(actualPrice * margin * leverage * 0.8)
short_entry = actualPrice
short_target = actualPrice * (1-0.005)
short_stop = actualPrice * (1+0.005)

long_qtd = round(actualPrice * margin * leverage * 0.8)

long_entry = actualPrice
long_target =  actualPrice * (1+0.005)
long_stop = actualPrice * (1-0.005)


# margin = margin - actualPrice/short_qtd * taker_fee
# margin = margin + ((short_qtd/short_target) - (short_qtd/short_entry)) - (short_qtd/short_target * maker_fee)
# print(margin)
# print (((short_qtd/short_target) - (short_qtd/short_entry)))
# print(short_qtd/short_target)
# print(short_qtd/short_entry)
# print(short_qtd/short_target * maker_fee)
# print(round((margin/init_margin-1)*100,2))

margin1 = margin + ((long_qtd/long_entry) - (long_qtd/long_target)) - (long_qtd/long_target * maker_fee) - (long_qtd/long_entry * taker_fee)
margin2 = margin + ((long_qtd/long_entry) - (long_qtd/long_stop)) - (long_qtd/long_stop * taker_fee) - (long_qtd/long_entry * taker_fee)

margin3 = margin + ((long_qtd/long_entry) - (long_qtd/long_target)) - (long_qtd/long_target * maker_fee) - (long_qtd/long_entry * maker_fee)
margin4 = margin + ((long_qtd/long_entry) - (long_qtd/long_stop)) - (long_qtd/long_stop * taker_fee) - (long_qtd/long_entry * maker_fee)

print("Market Orders Case:")
print('Long Target Entry Reached {}, {}%'.format(round(margin1,5),round((margin1/init_margin-1)*100,2)))
print('Long Stop Entry Reached {}, {}%'.format(round(margin2,5),round((margin2/init_margin-1)*100,2)))
print('Relationship {}'.format(round((margin2/init_margin-1)/(margin1/init_margin-1),2)))
print('//////////////////////////////////////////')
print("Limit Orders Case:")
print('Long Target Entry Reached {}, {}%'.format(round(margin3,5),round((margin3/init_margin-1)*100,2)))
print('Long Stop Entry Reached {}, {}%'.format(round(margin4,5),round((margin4/init_margin-1)*100,2)))
print('Relationship {}'.format(round((margin4/init_margin-1)/(margin3/init_margin-1),2)))


# margin = margin - actualPrice/short_qtd * taker_fee
# margin = margin + ((long_qtd/long_entry) - (long_qtd/long_target)) - (long_qtd/long_entry * maker_fee)
# print(margin)
# print((taker_fee))
# print((long_qtd/long_entry))
# print(long_qtd/long_entry * taker_fee)
# print('{}%'.format(round((margin/init_margin-1)*100,2)))