# blc



获取raw图数据后，对其进行去除黑电平(blc)操作

blc.py文件中定义了函数`(raw_data:np.ndarray,obc:int=0)` 

> 第一个参数是`raw_data`是类型为np.ndarray的raw数据。
>
> 第二个参数obc为黑点平补偿系数。
