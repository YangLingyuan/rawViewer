# -*- coding: utf-8 -*-
import numpy as np


#a = [[3,4],[2,2],[1,1],[4,15],[4,8],[4,9],[4,10]]
a=np.ones([100,2])
#b=sorted(a,key=(lambda x:x[0]))
b=np.sort(a)

print(b)