# rawViewer
## 文件结构
.  
├── plugins  
│   ├── __init__.py  
│   ├── plusOne  
│   │   ├── plusOne.c  
│   │   ├── plusOne.dll  
│   │   └── plusOne.so  
│   ├── __pycache__  
│   │   ├── __init__.cpython-36.pyc  
│   │   ├── parseMIPIraw.cpython-36.pyc  
│   │   ├── plugin1.cpython-36.pyc  
│   │   └── plugin2.cpython-36.pyc  
│   ├── raw2rgb  
│   │   ├── config.py  
│   │   ├── const_def.py  
│   │   ├── conversion_rules.py  
│   │   ├── fileoperations.py  
│   │   ├── __init__.py  
│   │   ├── mipiraw2raw.py  
│   │   ├── multi_coroutine_cc.py  
│   │   └── raw2rgb.py  
│   └── unpackMipiraw  
│       ├── unpackMipiraw.c  
│       └── unpackMipiraw.so  
├── rawViewer.py  
├── README.md  
└── Sample_MIPIRAW10bit_Pattern_RGGB_W4000_H3000.raw  

## 命令行交互与增加插件
### 命令行交互
通过命令 python3 rawViewer.py [pathToImage] {--[module] [arguments]}进行调用
eg：
python3 rawViewer.py Sample_MIPIRAW10bit_Pattern_RGGB_W4000_H3000.raw --raw2rgb 3000 4000
### 添加插件
将源码（py/c）放在plugins文件夹下，通过 命令行调用。
parser.add_argument('--raw2rgb', type=int, nargs='*') 
代表向命令行工具中加入参数 '--raw2rgb'， number of arguments不限制
详情见https://docs.python.org/zh-cn/3/library/argparse.html
C源文件先通过命令gcc -shared -fPIC plusOne.c -o ../plusOne.so生成动态库输出至其自身目录下
## 模块接口
目前设想的是，每个模块提供一个类似setParameters()的函数或构造函数作为参数设定接口。命令行输入的参数后会被传输给该接口，以供模块完成初始化。实际的计算处理则提供一个run()函数，在process()的过程中被调用
## mipiraw to raw
目前通过加载郑嘉诚的raw2rgb模块，把单张mipiraw图片自动转存为“temp.raw”供后续模块使用
