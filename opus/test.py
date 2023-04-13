from brukeropusreader import read_file
import pandas as pd
import os
import datetime
import time
from originlab_graphing import OriginLabGraphing
from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt

'''
FTIR 데이터를 정리하는 코드
고정된 x 값에 대해 y값만 붙여서 저장
x 값은 wavenumbers는 x_data.txt에 저장되어 있음 (수정 필요시 수정 [3319개])

data에 들어가 있는 폴더 하나당 하나의 파일로 정리
=> 1-1폴더에 20개의 실험 파일이 있으면 x값 1개와 20개의 y값이 들어가는 파일이 생성됨 + 평균값과 표준편차도 같이 저장

%data폴더에는 1-1등 정리된 폴더안에 실험결과 파일이 있어야함%

변환된 파일은 result폴더에 저장됨
=> 변환 날짜를 기준으로 폴더가 생성되고 그 안에 파일이 저장됨

Bruker OPUS Reader 모듈을 사용해서 opus 뷰어 실행할 필요 없이 변환가능
링크 : https://github.com/qedsoftware/brukeropusreader

!!! 뷰어에서는 TR값을 찾지만 모듈에서는 AB값을 찾음 같은 값인것 확인했는데 한번더 확인 필요 !!!

'''

# 폴더 파일 만들기


def create_file_or_folder(name, path, is_folder=False):
    """
    Creates a new file or folder at the specified path.
    :param name: Name of the file or folder to be created
    :param path: Path where the file or folder should be created
    :param is_folder: Boolean value indicating whether to create a folder (True) or file (False)
    """
    file_path = os.path.join(path, name)
    if not os.path.exists(file_path):
        if is_folder:
            os.makedirs(file_path)
        else:
            with open(file_path, "w") as file:
                file.write("Hello, World!")
    else:
        print(f"{name} already exists at {path}")


# 피팅 함수 정의
def Guassian(x, a, b, c, d):
    return a*np.exp(-((x-b)**2)/(2*c**2))+d


def GaussAmp(x, y_0, a, x_c, w):
    return y_0 + a * np.exp(-0.5*((x-x_c)/w) ** 2)


def Lorentz(x, y_0, a, x_c, w):
    return y_0 + (2*a/np.pi)*(w/(4*(x-x_c) ** 2+w ** 2))


def main():
    start_time = time.time()

    # 경로 설정
    work_path = os.getcwd()
    data_path = os.path.join(work_path, 'data')
    result_path = os.path.join(work_path, 'result')

    # result폴더에 결과 폴더 생성
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    create_file_or_folder(date, result_path, is_folder=True)
    result_save_path = os.path.join(result_path, date)

    # x 데어터 얻기 (wavenumbers)
    with open('x_data.txt', 'r') as f:
        x_data = f.read().splitlines()

    # data폴더에서 작업파일 얻기  (data폴더에는 1-1등 정리된 폴더안에 실험결과 파일이 있어야함)
    data_list = os.listdir()
    print(f'변환 할 폴더 갯수 : {len(data_list)}')

    # 폴더 찾기

    # 파일 찾기

    # 데이터 프레임 만들기 빈
    df = pd.read_csv("test_data.txt",
                     header=None, delimiter="\t")

    # 찾은 파일들 데이터 프레임에 넣기
    # ab = opus_data['AB'][:-1]
    # df[f] = ab
    df = df[(df[0] >= 800) & (df[0] <= 2000)]

    # Extinction 구하기
    df['Extinction'] = 1-df[1]

    X = df[0].to_numpy()
    Y = df['Extinction'].to_numpy()

    # GaussAMP Fitting
    gauss_amp_popt, gauss_amp_pcov = curve_fit(
        GaussAmp, X, Y, p0=[0.005, 0.005, 1000, 200])

    lorentz_popt, lorentz_pcov = curve_fit(
        Lorentz, X, Y, p0=[0.005, 0.005, 1000, 200])

    df['GaussAmp'] = df['Extinction'] - gauss_amp_popt[0]
    df['Lorentz'] = df['Extinction'] - lorentz_popt[0]

    print(gauss_amp_popt)
    print(np.sqrt(np.diag(gauss_amp_pcov)))
    print("=====================================")
    print(lorentz_popt)
    print(np.sqrt(np.diag(lorentz_pcov)))

    plt.plot(X, Y, label="original data")
    plt.plot(X, GaussAmp(X, *gauss_amp_popt),
             label="GaussAmp fitting data")
    plt.plot(X, Lorentz(X, *lorentz_popt),
             label="Lorentz fitting data")
    plt.legend()
    plt.show()

    plt.plot(X, Y, label="original data")
    plt.plot(X, df["GaussAmp"],
             label="GaussAmp data")
    plt.plot(X, df["Lorentz"],
             label="Lorentz data")
    plt.legend()
    plt.show()

    # 데이터 저장
    # df.to_csv(os.path.join(result_save_path, f'{d}.csv'))

    # og = OriginLabGraphing(data_path=result_save_path,
    #                        result_path=os.path.join(work_path, 'origin_result'))

    # og.graphing()

    end_time = time.time()
    work_time = end_time - start_time
    print(f'걸린 시간 : {work_time}')


if __name__ == "__main__":
    main()
