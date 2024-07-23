import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, timedelta


@st.cache_data
def create_calendar(year, month):
    cal = calendar.Calendar(firstweekday=6)  # 일요일 시작
    month_days = cal.monthdayscalendar(year, month)

    previous_month = month - 1 if month > 1 else 12
    previous_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    previous_month_days = calendar.monthrange(previous_year, previous_month)[1]
    print(month_days)

    # 첫 주의 빈 칸을 이전 달의 날짜로 채우기
    first_week = month_days[0]
    month_day = previous_month_days
    for i in range(first_week.count(0),-1,-1):
        if first_week[i] == 0:
            first_week[i] = month_day
            month_day -= 1


    # 마지막 주의 빈 칸을 다음 달의 날짜로 채우기
    last_week = month_days[-1]
    next_day = 1
    for i in range(len(last_week)):
        if last_week[i] == 0:
            last_week[i] = next_day
            next_day += 1

    return month_days, previous_month, previous_year, next_month, next_year


@st.cache_data
def time_slots():
    slots = []
    start_time = datetime.strptime("06:00", "%H:%M")
    end_time = datetime.strptime("23:30", "%H:%M")
    current_time = start_time
    while current_time <= end_time:
        slots.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=30)
    return slots


def create_weekly_dataframes(year, month):
    month_days, previous_month, previous_year, next_month, next_year = create_calendar(year, month)
    slots = time_slots()

    weekly_dfs = {}
    week_num = 1

    for week in month_days:
        # 월의 첫 번째 주가 이전 달의 날짜를 포함하는 경우
        if week[-1] < 7 and week[0] > 7 and week_num == 1:
            all_days = [
                f'{previous_month:02d}-{day:02d}' if day > 7 else f'{month:02d}-{day:02d}' for
                day in week]
        # 월의 마지막 주가 다음 달의 날짜를 포함하는 경우
        elif week[-1] < 7 and week[0] > 7 and week_num > 1 :
            all_days = [f'{next_month:02d}-{day:02d}' if day < 7 else f'{month:02d}-{day:02d}' for
                        day in week]
        else:
            all_days = [f'{month:02d}-{day:02d}' for day in week]

        index = []
        for slot in slots:
            for i in range(1, 6):

                if i == 5:
                    index.append(f'=======')
                else:
                    index.append(f'{slot} - {i}')

        columns = all_days

        # 빈 데이터프레임 생성
        df = pd.DataFrame(index=index, columns=columns)

        weekly_dfs[f'Week {week_num}'] = df
        week_num += 1

    return weekly_dfs

def split_dataframe(df):
    # 기존 데이터프레임을 새로운 컬럼을 추가하여 확장
    expanded_df = pd.DataFrame()
    for column in df.columns:
        col_df = df[[column]].copy()
        col_df.columns = [f'{column}'] * len(col_df.columns)
        expanded_df = pd.concat([expanded_df, col_df], axis=1)
        expanded_df = expanded_df.fillna('')
    return expanded_df


def save_member_info(member_info):
    df = pd.DataFrame([member_info])
    csv_file_path = 'member_info.csv'
    df.to_csv(csv_file_path, index=False)
    return csv_file_path


# Main function
def main():
    st.title("회원 관리 및 주차별 일정 보기")

    # 사이드바에서 연도 및 월 선택
    with st.sidebar:
        year = st.number_input('Year', min_value=1900, max_value=2100, value=datetime.today().year)
        month = st.number_input('Month', min_value=1, max_value=12, value=datetime.today().month)

    # 탭 선택
    tab = st.selectbox("보기 선택", ["주차별 테이블", "회원 정보 입력"])

    if tab == "주차별 테이블":
        st.write(f"### {year}년 {month}월")
        weekly_dfs = create_weekly_dataframes(year, month)

        for week_name, df in weekly_dfs.items():
            st.write(f"#### {week_name}")
            expanded_df = split_dataframe(df)
            st.dataframe(expanded_df, height=400, width=1500)  # Adjust height as needed

    elif tab == "회원 정보 입력":
        with st.form(key='member_form'):
            member_name = st.text_input('회원명')
            age = st.number_input('연령', min_value=0)
            gender = st.selectbox('성별', ['남성', '여성'])
            status = st.selectbox('진행 여부', ['진행 중', '완료', '취소'])
            acquaintance = st.selectbox('지인 여부', ['네', '아니오'])
            contact = st.text_input('연락처')
            vehicle_number = st.text_input('차량 번호')
            payment_method = st.selectbox('결제 수단', ['신용카드', '현금', '기타'])
            individual_or_group = st.selectbox('개인/그룹', ['개인', '그룹'])
            registration_time = st.text_input('등록 시간', value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            start_date = st.date_input('시작일')
            end_date = st.date_input('종료일')

            submit_button = st.form_submit_button(label='제출')

            if submit_button:
                member_info = {
                    '회원명': member_name,
                    '연령': age,
                    '성별': gender,
                    '진행 여부': status,
                    '지인 여부': acquaintance,
                    '연락처': contact,
                    '차량 번호': vehicle_number,
                    '결제 수단': payment_method,
                    '개인/그룹': individual_or_group,
                    '등록 시간': registration_time,
                    '시작일': start_date,
                    '종료일': end_date,
                }
                csv_file_path = save_member_info(member_info)
                st.success(f'정보가 {csv_file_path}에 저장되었습니다.')


if __name__ == "__main__":
    main()
