import time

ctime = time.time()
var = time.localtime(ctime)
exp_num = 1
print('Exp_' + str(exp_num) + '_' + str(var[0]) + str(var[1]) +  str(var[2]) + '.npy')