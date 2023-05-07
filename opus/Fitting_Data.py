import numpy as np
'''
fitting 함수 정의
1. 피팅함수 정의하기
2. fitting_data에 피팅함수 이름, 피팅함수, 초기값, 범위를 정의한다.
'''

# 피팅 함수 정의


def GaussAmp(x, y_0, a, x_c, w):
    return y_0 + a * np.exp(-0.5*((x-x_c)/w) ** 2)


def Lorentz(x, y_0, a, x_c, w):
    return y_0 + (2*a/np.pi)*(w/(4*(x-x_c) ** 2+w ** 2))


def liner(x, y_0, a):
    return a*x+y_0


# 피팅 파라미터 정의
fitting_data = {
    "GaussAmp": {
        "func": GaussAmp,
        "p0": [0.005, 0.005, 1000, 200],
        "range": [800, 2000]
    },

    "Lorentz": {
        "func": Lorentz,
        "p0": [0.005, 0.005, 1000, 200],
        "range": [800, 2000]
    },

    "liner": {
        "func": liner,
        "p0": None,
        "range": [800, 2000]
    },
}

if __name__ == "__main__":
    for key, value in fitting_data.items():
        print(key)
        print(value)
        print(value["func"])
        print(value["p0"])
        print(value["range"])
        print("==================================")
