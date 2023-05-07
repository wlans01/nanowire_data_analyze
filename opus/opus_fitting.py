from brukeropusreader import read_file
import pandas as pd
import os
import datetime
import time
import numpy as np
from scipy.optimize import curve_fit
from originlab_graphing import OriginLabGraphing
import logging
from tqdm import tqdm
from Fitting_Data import fitting_data

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
# Set up logging
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f'error//error_log_{timestamp}.log'

logging.basicConfig(filename=log_filename, level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

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


def fit_and_save_data(file_lsit, data_path, x_data, result_save_path, params_save_path, file_path, fit_function, p0=None, range=[800, 2000], debug=False):
    ''''''
    # 데이터 프레임 만들기 빈
    df_data = pd.DataFrame(index=None)
    df_params = pd.DataFrame(index=None)
    X_index = []
    # 파일 찾기
    for j, f in enumerate(file_lsit):
        try:

            # 찾은 파일들 데이터 프레임에 넣기
            df = pd.DataFrame()
            opus_data = read_file(os.path.join(data_path, file_path, f))
            ab = opus_data['AB'][:-1]
            df["x"] = x_data
            df[f] = ab
            # 인덱스 자르기
            df = df[(df["x"] >= range[0]) & (df["x"] <= range[1])]
            X_index = df["x"]

            # Extinction 구하기
            df['Extinction'] = 1-df[f]

            params_list = []

            # Function Fitting
            popt, pcov = curve_fit(
                fit_function, df["x"], df['Extinction'], p0=p0, maxfev=5000)

            params_list += popt.tolist()
            params_list.append(np.sqrt(np.diag(pcov)))

            df[fit_function.__name__] = df['Extinction'] - popt[0]

            df_data[f] = df[fit_function.__name__]

            df.set_index(keys=["x"], drop=True, inplace=True)
            df_params[f] = params_list

            # 기본파일
            if debug:
                df.to_csv(os.path.join(result_save_path, f'{f}.csv'))

        except:
            logging.error(f"Error Fitting the file: {f}")

    # GaussAmp 평균값 구하기
    df_data['mean'] = df_data.mean(axis=1)
    # GaussAmp 표준편차 구하기
    df_data['std'] = df_data.std(axis=1)

    df_data["X"] = X_index

    # 파라미터 파일
    df_params.to_csv(os.path.join(params_save_path,
                     f'{file_path}_{fit_function.__name__}_params.csv'), index=False)

    # 가우시안 피팅파일
    df_data.to_csv(os.path.join(result_save_path,
                   f'{file_path}_{fit_function.__name__}_result.csv'), index=False)


def main(fit_function, fit_function_p0, fit_function_range):
    start_time = time.time()

    # 경로 설정
    work_path = os.getcwd()
    data_path = os.path.join(work_path, 'data')
    result_path = os.path.join(work_path, 'result')
    origin_result_path = os.path.join(work_path, 'origin_result')

    # result폴더에 결과 폴더 생성
    result_save_path = os.path.join(
        result_path, fit_function.__name__, "result")
    params_save_path = os.path.join(
        result_path, fit_function.__name__, "params")
    create_file_or_folder(result_save_path, result_path, is_folder=True)
    create_file_or_folder(params_save_path, result_path, is_folder=True)

    # x 데어터 얻기 (wavenumbers)
    with open('x_data.txt', 'r') as f:
        read_data = f.read().splitlines()
        x_data = [float(i) for i in read_data]

    # data폴더에서 작업파일 얻기  (data폴더에는 1-1등 정리된 폴더안에 실험결과 파일이 있어야함)
    data_list = os.listdir(data_path)
    print(f'변환 할 폴더 갯수 : {len(data_list)}')

    # 폴더 찾기
    for file_name in tqdm(data_list):
        file_lsit = os.listdir(os.path.join(data_path, file_name))

        fit_and_save_data(file_lsit, data_path, x_data,
                          result_save_path, params_save_path, file_name, fit_function, fit_function_p0, fit_function_range)

    print("""
    파일 피팅완료
    오리진 그래프 그리기중...
    """)
    # 오리진 그리기
    og = OriginLabGraphing(result_path, origin_result_path,
                           f"{fit_function.__name__}_result")

    og.graphing(fit_function_range)

    end_time = time.time()
    work_time = end_time - start_time
    print(f'걸린 시간 : {work_time}')


if __name__ == "__main__":

    print("""
    피팅할 함수의 번호를 입력해주세요
    """)
    for i, key in enumerate(fitting_data):
        print(f"{i}. {key}")

    func_num = int(input("함수번호 : "))

    main(
        fitting_data[list(fitting_data.keys())[func_num]]["func"],
        fitting_data[list(fitting_data.keys())[func_num]]["p0"],
        fitting_data[list(fitting_data.keys())[func_num]]["range"]
    )
