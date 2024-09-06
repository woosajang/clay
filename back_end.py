import pandas as pd
import datetime
import numpy as np


def create_time_slots():
    """Create time slots from 06:00 to 23:30, each slot repeated 4 times."""
    time_slots = []
    start_time = datetime.datetime.strptime("06:00", "%H:%M")
    end_time = datetime.datetime.strptime("23:30", "%H:%M")
    current_time = start_time

    while current_time <= end_time:
        for i in range(1, 5):
            time_slots.append(f"{current_time.strftime('%H:%M')}-{i}")
        current_time += datetime.timedelta(minutes=30)

    return time_slots


def create_date_range(start_year, end_year):
    """Create a date range from start_year to end_year."""
    date_range = pd.date_range(start_year,
                               end=datetime.datetime(end_year, 12, 31), freq='D')
    return date_range


def get_matching_dates(schedule, start_year, end_year):
    """
    주어진 기간 내에 특정 요일과 시간대에 해당하는 모든 날짜를 리스트로 반환합니다.

    :param schedule: 요일과 시간대 리스트 (예: ['월 06:30', '화 08:00'])
    :param start_year: 시작 년도 (예: 2024)
    :param end_year: 종료 년도 (예: 2030)
    :return: 해당하는 날짜와 시간대의 리스트
    """
    # 요일 문자열을 숫자로 변환 (0: 월요일, 6: 일요일)
    days = ["월", "화", "수", "목", "금", "토", "일"]

    # 날짜 범위 생성
    date_range = create_date_range(start_year, end_year)

    # 일정 파싱
    parsed_schedule = []
    for item in schedule:
        day, time = item.split()
        day_index = days.index(day)
        parsed_schedule.append((day_index, time))

    # 기간 내의 모든 날짜를 순회하면서 선택된 요일과 시간대에 일치하는 날짜를 찾음
    matching_dates = []

    for single_date in date_range:
        for day_index, time in parsed_schedule:
            if single_date.weekday() == day_index:
                matching_dates.append(f"{single_date.strftime('%Y-%m-%d')} {time}")

    return matching_dates


def fill_dataframe_with_schedule(df, schedule, number_repeat, member_info):
    """
    주어진 스케줄을 DataFrame에 채웁니다. 단, 각 시간대의 1~4까지 칸이 다 찬 경우 에러를 반환합니다.

    :param df: DataFrame to fill
    :param schedule: List of matching dates and times
    """
    idx_N = 0
    # print(schedule)
    if ":" in member_info:
        coach = member_info[member_info.index(":")-3:member_info.index(":")]
    else:
        coach = member_info[-3:]
    print("coach", coach)
    already_coach = []
    for entry in schedule:
        date_str, time_str = entry.split()
        time_slot_base = f"{time_str}-"

        # Find the first available slot (1-4) for the given date and time
        for slot in range(1, 5):
            time_slot = time_slot_base + str(slot)
            print("내용",df.at[time_slot, date_str])
            if df.at[time_slot, date_str] == "" or pd.isna(df.at[time_slot, date_str]) :
                if coach in already_coach:
                    print(f"{date_str} 날짜에 {time_str} 시간대의 강사 schedule이 꽉 차있습니다. 다른 시간대로 다시 시도하세요")
                    return date_str, time_str, df
                if idx_N >= number_repeat:
                    return 0, 0, df
                if ":" not in member_info:
                    print(f"{member_info} {idx_N+1}/{number_repeat}회차")
                    df.at[time_slot, date_str] = f"{member_info}:{idx_N+1}/{number_repeat}회차" # 회원데이터로 채우기
                    idx_N += 1
                else:
                    print(f"{member_info}회차")
                    df.at[time_slot, date_str] = f"{member_info}" # 회원데이터로 채우기
                    idx_N += 1
                    print(idx_N)
                    print(idx_N)

            else:
                already_coach.append(df.at[time_slot, date_str][df.at[time_slot, date_str].index(" ")+1:df.at[time_slot, date_str].index(" ")+4])
                print(already_coach)
                continue
        else:
            # print(time_slot)
            print(f"{date_str} 날짜에 {time_str} 시간대의 schedule이 꽉 차있습니다. 다른 시간대로 다시 시도하세요")
            return date_str, time_str, df



def find_dataframe_with_schedule(df, schedule, coach):

    date_str, time_str = schedule.split()
    time_slot_base = f"{time_str}-"

    # Find the first available slot (1-4) for the given date and time
    try:
        for slot in range(1, 5):
            time_slot = time_slot_base + str(slot)
            print("내용",df.at[time_slot, date_str])
            if coach in df.at[time_slot, date_str]:
                return df.at[time_slot, date_str]
            else:
                continue
        else:
            # print(time_slot)
            print(f"{date_str} 날짜에 {time_str}에서 {coach}님의 스케줄을 찾을 수 없습니다.")
            return -1
    except:
        return -1


def change_dataframe_with_schedule(df, pre_schedule, chg_schedule, df_result):

    date_str, time_str = pre_schedule.split()

    time_slot_base = f"{time_str}-"


    print("df_result", df_result)
    tg_date_str, tg_time_str, df = fill_dataframe_with_schedule(df, chg_schedule, int(1), df_result)

    if tg_date_str != 0 and tg_time_str != 0:

        print(f"{date_str}날짜에 {time_str}시간대의 코트 및 강사의 schedule이 꽉 차있습니다. 다른 시간대로 다시 시도하세요")
        return tg_date_str, tg_time_str, df

    # Find the first available slot (1-4) for the given date and time
    for slot in range(1, 5):
        time_slot = time_slot_base + str(slot)
        print("내용",df.at[time_slot, date_str])
        try:
            if np.isnan(df.at[time_slot, date_str]):
                continue
        except:
            if df_result in df.at[time_slot, date_str]:
                print(df.at[time_slot, date_str])
                df.at[time_slot, date_str] = np.nan
            else:
                continue

    return 0, 0, df

def find_coach_with_schedule(df, date_str, coach):

    df_date = df[f'{date_str}']
    if coach == "ALL":
        df_coatch = df_date.dropna()
    else:
        df_coatch = df_date[df_date.str.contains(coach, na=False)]

    return df_coatch


def confirm_dataframe_with_schedule(df_confirm):
    date_str = df_confirm.columns[1]
    df = pd.read_csv("raw_date.csv", header=0, index_col=0, encoding='cp949')
    idx_N = 0
    for i, time_slot in enumerate(df_confirm.index):
        print("내용",df_confirm.at[time_slot, df_confirm.columns[0]])
        if "진행" in df.at[time_slot, date_str]:
            continue
        if df_confirm.at[time_slot, df_confirm.columns[0]]:
            df.at[time_slot, date_str] = f"{df_confirm.at[time_slot, date_str]}, 진행"
            idx_N +=1

    return df, idx_N





# Create the time slots and date range
time_slots = create_time_slots()
date_range = create_date_range(2024, 2030)

if __name__ == "__main__":
    # Example usage
    schedule = ["월 08:30", "화 10:00", "수 18:00"]
    matching_dates = get_matching_dates(schedule, datetime.datetime(2024, 8, 1), 2030)
    number_repeat = 10
    member_info = ["TEST"]
    df = pd.read_csv("raw_date.csv", header=0, index_col=0, encoding='cp949')
    df[:] = ""
    print(df)
    # Fill the DataFrame with the schedule
    # fill_dataframe_with_schedule(df, matching_dates, number_repeat,member_info)


    df.to_csv("raw_date.csv",encoding='cp949')
