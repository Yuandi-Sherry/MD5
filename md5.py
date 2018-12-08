import sys
import hashlib
import math

# aRegister = 0x01234567
# bRegister = 0x89ABCDEF
# cRegister = 0xFEDCBA98
# dRegister = 0x76543210
aRegister = 0x67452301
bRegister = 0xEFCDAB89
cRegister = 0x98BADCFE
dRegister = 0x10325476

def F(b,c,d):
    return (b&c)|((~b)&d)

def G(b,c,d):
    return (b&d)|(c&(~d))

def H(b,c,d):
    return b^c^d

def I(b,c,d):
    return c^(b|(~d))

s_1 = [ 7, 12, 17, 22] * 4
s_2 = [ 5,  9, 14, 20] * 4
s_3 = [ 4, 11, 16, 23] * 4
s_4 = [ 6, 10, 15, 21] * 4
X_1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
X_2 = [1, 6, 11, 0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12]
X_3 = [5, 8, 11, 14, 1, 4, 7, 10, 13, 0, 3, 6, 9, 12, 15, 2]
X_4 = [0, 7, 14, 5, 12, 3, 10, 1, 8, 15, 6, 13, 4, 11, 2, 9]

def T(i):
    return int(pow(2,32) * abs(math.sin(i)))

def padding(cleartext):
    # 对于input_m中每个元素执行ord函数，使用ord函数其转化为ASCII值
    byteArray = list(map(ord, cleartext))
    lenOfK = len(byteArray) * 8
    if lenOfK % 512 > 448:
        lenOfP = 512 + 448- lenOfK % 512
    else:
        lenOfP = 448 - lenOfK % 512
    byteArray.append(0b10000000)
    for i in range(1, int(lenOfP / 8)):
        byteArray.append(0b00000000)
    for i in range(0, 8):
        byteArray.append(int(lenOfK / pow(2, i * 8) % pow(2,8)))
    return byteArray

def dividing(byteArray):
    yGroups = []
    for i in range(0, int(len(byteArray)/64)): # 每组64bytes
        temp = []
        for j in range(0, 64):
            temp.append(byteArray[i * 64 + j])
        yGroups.append(temp)
    return yGroups

def initialize():
    CV_0 = list([aRegister, bRegister, cRegister, dRegister])
    return CV_0

def cyclicCompress(yGroups, CV_0):
    for i in range(0, len(yGroups)):
        CV_0 = H_MD5(CV_0, yGroups[i])
    return CV_0

def H_MD5(IV, Y_i): # i in 1~16, t in 1~4, Y_i = yGroup[i]
    temp = IV
    for t in range(1,5):
        for i in range(1,17):
            a = IV[0]
            b = IV[1]
            c = IV[2]
            d = IV[3]
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
            X_k = Y_i[4*k + 3]* pow(2, 24) + Y_i[4*k+2] * pow(2, 16) + Y_i[4*k+1] * pow(2, 8) + Y_i[4*k]
            if t == 1:
                A = (b+leftShift((a+F(b,c,d)+X_k+T(16*(t-1)+i))%pow(2,32), s))%pow(2,32)
            elif t == 2:
                A = (b+leftShift((a+G(b,c,d)+X_k+T(16*(t-1)+i))%pow(2,32), s))%pow(2,32)
            elif t == 3:
                A = (b+leftShift((a+H(b,c,d)+X_k+T(16*(t-1)+i))%pow(2,32), s))%pow(2,32)
            elif t == 4:
                A = (b+leftShift((a+I(b,c,d)+X_k+T(16*(t-1)+i))%pow(2,32), s))%pow(2,32)
            IV = [d, A, b, c]
    IV[0] += temp[0]
    IV[0] %= pow(2,32)
    IV[1] += temp[1]
    IV[1] %= pow(2,32)
    IV[2] += temp[2]
    IV[2] %= pow(2,32)
    IV[3] += temp[3]
    IV[3] %= pow(2,32)
    return IV

def leftShift(x, s): # 参数为 32 bit 输入，4字节
    higher = int(x/pow(2, 32-s))
    lower = x%(pow(2,32-s))
    y = lower * pow(2, s) + higher
    return y

def backToBigEnd(result):
    for i in range (0,4):
        while len(result[i]) != 10:
            result[i] = result[i][0:2] + '0' + result[i][2:10]
    ans = ""
    for i in range (0,4):
        ans += inverseStr(result[i])
    return ans

def inverseStr(str):
    ans = ""
    ans += str[8:10]
    ans += str[6:8]
    ans += str[4:6]
    ans += str[2:4]
    return ans

def md5(input_m):
    bytearray = padding(input_m)
    yGroups = dividing(bytearray)
    CV_0 = initialize()
    result = cyclicCompress(yGroups, CV_0)
    return backToBigEnd(list(map(hex,result)))

def standard_md5(str=''):
    md = hashlib.md5()  # 创建md5对象
    md.update(str.encode(encoding='utf-8'))  # 这里必须用encode()函数对字符串进行编码，不然会报 TypeError: Unicode-objects must be encoded before hashing
    return md.hexdigest()

if __name__ == '__main__':
    CLEARTEXT = sys.argv[1]
    print("STANDARD MD5 IS: ")
    print(standard_md5(CLEARTEXT))
    # print(standard_md5("\"Crescent moon\" (The Crescent Moon, 1903), by India famous poet, writer Tagore, mainly from 1903 published Bengali poetry \"child set\", some are also directly in English writing.Collections of poetry, poetry life depicted children's game, a skillfully performed the children's psychological, as well as their lively imagination.Its special meaningful artistic charm, led us to a pure child world, brought to our childhood memories"))
    print("IMPLEMENTED MD5 IS: ")
    print(md5(CLEARTEXT))
    # print(md5("\"Crescent moon\" (The Crescent Moon, 1903), by India famous poet, writer Tagore, mainly from 1903 published Bengali poetry \"child set\", some are also directly in English writing.Collections of poetry, poetry life depicted children's game, a skillfully performed the children's psychological, as well as their lively imagination.Its special meaningful artistic charm, led us to a pure child world, brought to our childhood memories"))
