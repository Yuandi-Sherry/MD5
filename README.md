# MD5算法原理概述

| 姓名   | 学号     | 学院                 | 班级                 |
| ------ | -------- | -------------------- | -------------------- |
| 周远笛 | 16340311 | 数据科学与计算机学院 | 软件工程（数字媒体） |

总的来说，MD5将任意长度的消息通过补全后分块的方式，对每一块和之前的结果进行迭代运算（4次循环，每个循环周有16次迭代）。将最后一次输出的结果作为加密结果。在这个过程中，每一轮迭代输入当前消息快和上一步迭代的结果。

## 运行环境

window10 安装 ubuntu 18.04 bash

```powershell
> bash
# python3 md5.py (args)
```

## 总体结构

### 填充

首先将明文消息根据ASCII码转换为每个字节占据一个字节8bit，计算出消息长度K，并填充P bit 使其能某mod 512 余448或者说在加入P和64bit后能够被512整除。

### 分块

填充过程中将消息变为了512bit的倍数，那么只需要分成`(K+P+64)/512`组即可。存储在数组或者vector等二维数组结构中。

### 缓冲区初始化

缓冲区需要将四个寄存器初始化为A = 0x01234567, B = 0x89abcdef, C = 0xfedcba98, D = 76543210. 并以**小端模式**存放。即寄存器向量IV的初始值为 A = 0x67452301, B = 0xEFCDAB89, C = 0x98BADCFE, D = 0x10325476. 

### 循环压缩

循环压缩过程一共应用(K+P+64)/512次压缩函数，每次分为四轮循环，每轮循环分为十六次迭代。每次引用压缩函数输入上次的结果CV以及本次对应的消息分组。

每次迭代需要计算A：

```
A = b+((a+func(b,c,d)+X[k]+T[i])<<<s)
```

每轮循环中一次迭代还需要将输入的[a, b, c, d]替换为当前的[d, A, b, c]作为下一轮迭代的输入。

一次内的4轮循环对应的生成函数fun分别为F, G, H, I，相同轮循环内的16次迭代采用相同生成函数。但是当处理消息分组的字以及T表元素时各不同循环不同迭代都是不相同的。其中选择的消息分组下标，每一轮循环内的迭代遵守不同的规则：

```
第一轮：k = j
第二轮：k = (1+5*j)%16
第三轮：k = (5+3*j)%16
第四轮：k = 7*j%16
```

而T根据迭代在本次压缩过程中的次序（1~64）作为T的输入值，根据公式：

```
T[i] = int(pow(2,32) * abs(sin(i)))
```

产生。

每次的左移运算位数遵循S表，相同循环中的间隔次数为4的迭代采用相同的左移位数。

**此外，每次进行完四次迭代之后，还需要将生成的[A, B, C, D]与该函数输入时的[a,b,c,d]进行相加得到本次函数执行结果的CV。**(这一步曾经被我遗漏以至于得不到正确结果)

### 得出结果

这一步需要将最后一轮输出的4个32bit字从小端模式改回. 对于每个32bit字要从0xabcdefgh改为0xghefcdab. 

## 模块分解

### padding

> 填充为能够被512bit整除

将输入的字符串通过`ord`函数将字符转为对应的ASCII码，并以8bit/1byte为长度单位进行元素的划分和存储。使得数组中有bit数/8个数组元素。

根据K计算出P：

```python
if lenOfK % 512 > 448:
    lenOfP = 512 + 448- lenOfK % 512
else:
    lenOfP = 448 - lenOfK % 512
```

并进行10...0补全：

```python
byteArray.append(0b10000000)
for i in range(1, int(lenOfP / 8)):
	byteArray.append(0b00000000)
```

然后将lenOfK%pow(2, 64)以小端模式作为数组的最后8个元素：

```python
for i in range(0, 8):
    byteArray.append(int(lenOfK / pow(2, i * 8) % pow(2,8)))
```

### dividing

> 分组为512bit一组

直接64bytes一组：

```python
for i in range(0, int(len(byteArray)/64)): # 每组64bytes
    temp = []
    for j in range(0, 64):
   		temp.append(byteArray[i * 64 + j])
	yGroups.append(temp)
```

### initialize

> 按小段模式初始化IV

```python
aRegister = 0x67452301
bRegister = 0xEFCDAB89
cRegister = 0x98BADCFE
dRegister = 0x10325476
CV_0 = list([aRegister, bRegister, cRegister, dRegister])
```

### cyclicCompress

进行yGroups长度次的循环压缩：

```python
for i in range(0, len(yGroups)):
	CV_0 = H_MD5(CV_0, yGroups[i])
```

#### H_MD5

> 循环压缩函数

首先记录下来最开始输入的CV，用于64次循环后的加和：

```python
 temp = IV
```

记循环为t(1-4) ，迭代为i(1-16)：

```python
	for t in range(1,5):
        for i in range(1,17):
            a = IV[0]
            b = IV[1]
            c = IV[2]
            d = IV[3]
            # 计算32位字的在分组中的下标以及循环左移位数
            if t == 1:
                k = i-1
                s = s_1[i-1]
            elif t == 2:
                k = (1+5*(i-1))%16
                s = s_2[i-1]
            elif t == 3:
                k = (5+3*(i-1))%16
                s = s_3[i-1]
            elif t == 4:
                k = (7*(i-1))%16
                s = s_4[i-1]
            # 根据小端模式计算32bit字的十进制值
            X_k = Y_i[4*k + 3]* pow(2, 24) + Y_i[4*k+2] * pow(2, 16) + Y_i[4*k+1] * pow(2, 8) + Y_i[4*k]
            # 根据轮数t选择生成函数
            if t == 1:
                A = (b+leftShift((a+F(b,c,d)+X_k+T(16*(t-1)+i))%pow(2,32), s))%pow(2,32)
            elif t == 2:
                A = (b+leftShift((a+G(b,c,d)+X_k+T(16*(t-1)+i))%pow(2,32), s))%pow(2,32)
            elif t == 3:
                A = (b+leftShift((a+H(b,c,d)+X_k+T(16*(t-1)+i))%pow(2,32), s))%pow(2,32)
            elif t == 4:
                A = (b+leftShift((a+I(b,c,d)+X_k+T(16*(t-1)+i))%pow(2,32), s))%pow(2,32)
            # 获得结果轮换
            IV = [d, A, b, c]
    # 在64次迭代后将其与输入CV相加，并取末8位
    IV[0] += temp[0]
    IV[0] %= pow(2,32)
    IV[1] += temp[1]
    IV[1] %= pow(2,32)
    IV[2] += temp[2]
    IV[2] %= pow(2,32)
    IV[3] += temp[3]
    IV[3] %= pow(2,32)
```

##### leftShift

> 左移函数

根据左移位数计算移动前的高位和低位：

```python
higher = int(x/pow(2, 32-s))
lower = x%(pow(2,32-s))
y = lower * pow(2, s) + higher
```

### backToBigEnd

> 生成加密后的字符串

获得参数传入的最后一次CV_q的结果后，需要遍历四个32bit字，补全32bit. 如果计算结果不足32bit，则会导致md5字符串不足128bit。之后，每个32bit字进入`inverseStr`转化为大端模式。

#### inverseStr

> 将32bit字从小端模式变为大端模式

```python
ans = ""
ans += str[8:10]
ans += str[6:8]
ans += str[4:6]
ans += str[2:4]
```

## 数据结构

这里主要运用了数组的数据结构，以字节为长度进行元素存储。需要注意的是这里在padding的最后一步和H_MD5函数中读取32bit字都是用的是小端模式，所以需要进行转换，不过存储的是以字节为单位，所以只需要倒叙从高到低位计算即可。

这里还用了字符串的数据结构（其实和数组大同小异），不过转换起来比较方便，常使用Map函数进行str和int之间的转换，并存入list中。

## 编译运行结果

首先，代码中调用了python的hashlib库生成md5的标准结果与自己的结果进行比对。

````python
md = hashlib.md5()  # 创建md5对象
md.update(str.encode(encoding='utf-8'))
````

### 基础测试

输入自己名字的拼音和学号分别与md5标准函数进行对比，发现结果一致：

输入字符串：

```
zhouyuandi
16340311
```

![1544249530258](imgs\1544249530258.png)

### 复杂测试

由于简单测试的字符串较短，只能补全为一个512bit，需要较长的字符串进行多次分组迭代的检测：

输入字符串：

```
\"Crescent moon\" \(The Crescent Moon, 1903\), by India famous poet, writer Tagore, mainly from 1903 published Bengali poetry \"child set\", some are also directly in English writing.Collections of poetry, poetry life depicted children's game, a skillfully performed the children's psychological, as well as their lively imagination.Its special meaningful artistic charm, led us to a pure child world, brought to our childhood memories
```

![1544249675118](imgs\1544249675118.png)

验证成功！