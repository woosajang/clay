import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, timedelta
import back_end as be

@st.cache_data
def create_calendar(year, month):
    cal = calendar.Calendar(firstweekday=6)  # 일요일 시작
    month_days = cal.monthdayscalendar(year, month)

    previous_month = month - 1 if month > 1 else 12
    previous_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    previous_month_days = calendar.monthrange(previous_year, previous_month)[1]
    # print(month_days)

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
    # print(len(slots))

    weekly_dfs = {}
    week_num = 1

    for week in month_days:
        # 월의 첫 번째 주가 이전 달의 날짜를 포함하는 경우
        if week[-1] < 7 and week[0] > 7 and week_num == 1:
            all_days = [datetime(year, previous_month, day).strftime('%Y-%m-%d') if day > 7 else datetime(year, month, day).strftime('%Y-%m-%d') for
                day in week]
        # 월의 마지막 주가 다음 달의 날짜를 포함하는 경우
        elif week[-1] < 7 and week[0] > 7 and week_num > 1 :
            all_days = [datetime(year, next_month, day).strftime('%Y-%m-%d') if day < 7 else datetime(year, month, day).strftime('%Y-%m-%d') for
                        day in week]
        else:
            all_days = [datetime(year, month, day).strftime('%Y-%m-%d') for day in week]

        index = []
        for slot in slots:
            for i in range(1, 6):

                if i == 5:
                    index.append(f'=======')
                else:
                    index.append(f'{slot}-{i}')

        columns = all_days

        # 빈 데이터프레임 생성
        df_time = pd.read_csv("raw_date.csv", header=0, index_col=0, encoding='cp949')
        df = pd.DataFrame(index=index, columns=columns)
        df.update(df_time)
        print(df)
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
    csv_file_path = 'member_info.csv'
    df = pd.DataFrame([member_info])
    df_member = pd.read_csv(csv_file_path, header=0, encoding='cp949')
    print(member_info["연락처"].replace("-", ""))
    df.insert(0,"회원번호",int(df["연락처"][0].replace("-","")))
    df = pd.concat([df_member, df],axis=0)
    df.to_csv(csv_file_path, index=False,encoding='cp949')
    return csv_file_path


# Helper function to create time slots
def create_time_slots():
    time_slots = []
    start_time = datetime.strptime("06:00", "%H:%M")
    end_time = datetime.strptime("23:30", "%H:%M")
    current_time = start_time

    while current_time <= end_time:
        time_slots.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=30)

    return time_slots

# Main function
def main():
    st.title("주차별 일정 보기")

    # 사이드바에서 연도 및 월 선택
    with st.sidebar:
        year = st.number_input('Year', min_value=1900, max_value=2100, value=datetime.today().year)
        month = st.number_input('Month', min_value=1, max_value=12, value=datetime.today().month)

    # 탭 선택
    tab = st.selectbox("보기 선택", ["주차별 테이블", "회원 정보 입력", "스케줄 변경", "보강 등록"])

    if tab == "주차별 테이블":
        st.write(f"### {year}년 {month}월")
        weekly_dfs = create_weekly_dataframes(year, month)

        for week_name, df in weekly_dfs.items():
            st.write(f"#### {week_name}")
            expanded_df = split_dataframe(df)
            st.dataframe(expanded_df,width=5000)  # Adjust height as needed

    elif tab == "회원 정보 입력":
        age_list = ['미취학', '초등학생', '중학생', '고등학생', '20대', '30대', '40대', '50대', '60대이상']
        gender_list = ['남성', '여성']
        status_list = ['진행 중', '완료', '취소']
        acquaintance_list = ['O', 'X']
        payment_method_list = ['신용카드', '현금', '기타']
        individual_or_group_list = ['개인', '그룹']
        membership_grade_list = ['LV1', 'LV2', 'LV3', 'LV4']
        coach_list = ['김상엽', '박지훈', '이지윤', '이민혁', '장우혁']
        payment_status_list = ['신용카드', '현금', '계좌이체', '기타']
        registration_source_list = ['온라인', '오프라인', '기타']
        # Initialize the session state for storing selected slots
        if 'selected_slots' not in st.session_state:
            st.session_state.selected_slots = []
        if 'resistered' not in st.session_state:
            st.session_state["resistered"] = 0
        if 'df_resistered' not in st.session_state:
            st.session_state['df_resistered'] = pd.DataFrame()
        contact = st.text_input('연락처')

        if st.button(label="회원정보 불러오기"):

            csv_file_path = 'member_info.csv'
            df_member = pd.read_csv(csv_file_path, header=0, encoding='cp949')
            st.session_state['df_resistered']  = df_member[df_member['회원번호'] == int(contact.replace("-", ""))]
            if len(st.session_state['df_resistered'] ) != 0:
                st.session_state["resistered"] = 1
            else:
                st.session_state["resistered"] = 0

        if st.session_state["resistered"] == 1:

            df_resistered = st.session_state['df_resistered'] .iloc[0]
            member_name = st.text_input('회원명', value=df_resistered["회원명"])
            age_list_index = age_list.index(df_resistered["연령"])
            age = st.selectbox('연령', age_list, index=age_list_index)
            gender_list_index = gender_list.index(df_resistered["성별"])
            gender = st.selectbox('성별', gender_list, index=gender_list_index)
            status_list_index = status_list.index(df_resistered["진행 여부"])
            status = st.selectbox('진행 여부', status_list, index=status_list_index)
            acquaintance_list_index = acquaintance_list.index(df_resistered["지인 여부"])
            acquaintance = st.selectbox('지인 여부', acquaintance_list, index=acquaintance_list_index)
            vehicle_number = st.text_input('차량 번호', value=df_resistered["차량 번호"])
            payment_method_list_index = payment_method_list.index(df_resistered["결제 수단"])
            payment_method = st.selectbox('결제 수단', payment_method_list, index=payment_method_list_index)
            individual_or_group_list_index = individual_or_group_list.index(df_resistered["개인/그룹"])
            individual_or_group = st.selectbox('개인/그룹', individual_or_group_list, index=individual_or_group_list_index)
            start_date = st.date_input('시작일',value=datetime(int(df_resistered["시작일"][:4]), int(df_resistered["시작일"][5:7]), int(df_resistered["시작일"][8:10])) )
            repeat_number = st.number_input('반복 횟수', min_value=0, format="%.d", value=int(df_resistered["반복 횟수"]))
            membership_grade_list_index = membership_grade_list.index(df_resistered["회원 등급"])
            membership_grade = st.selectbox('테니스 Level', membership_grade_list, index=membership_grade_list_index)
            coach_list_index = coach_list.index(df_resistered["담당 코치"])
            coach = st.selectbox('담당 코치', coach_list, index=coach_list_index)
            payment_amount = st.number_input('결제 금액', min_value=0, format="%.d", value=int(df_resistered["결제 금액"]))
            payment_status_list_index = payment_status_list.index(df_resistered["결제 완료 수단"])
            payment_status = st.selectbox('결제 완료 수단', payment_status_list, index=payment_status_list_index)
            discount_rate = st.number_input('할인율 (%)', min_value=0.0, max_value=100.0, format="%.2f", value=float(df_resistered["할인율"]))
            # registration_month = st.selectbox('등록 월', [f'{i:02d}' for i in range(1, 13)])
            registration_source_list_index = registration_source_list.index(df_resistered["등록 경로"])
            registration_source = st.selectbox('등록 경로', registration_source_list, index=registration_source_list_index)
            notes = st.text_area('비고', value=df_resistered["비고"])
            st.session_state.member_info = {
                '회원명': member_name,
                '연령': age,
                '성별': gender,
                '진행 여부': status,
                '지인 여부': acquaintance,
                '연락처': contact,
                '차량 번호': vehicle_number,
                '결제 수단': payment_method,
                '개인/그룹': individual_or_group,
                '시작일': start_date,
                '반복 횟수': repeat_number,
                '회원 등급': membership_grade,
                '담당 코치': coach,
                '결제 금액': payment_amount,
                '결제 완료 수단': payment_status,
                '할인율': discount_rate,
                # '등록 월': registration_month,
                '등록 경로': registration_source,
                '비고': notes
            }
        elif st.session_state["resistered"] != 1:
            st.warning("일치하는 회원 정보를 찾을 수 없습니다.")
            member_name = st.text_input('회원명')
            age = st.selectbox('연령', age_list)
            gender = st.selectbox('성별', gender_list)
            status = st.selectbox('진행 여부', status_list)
            acquaintance = st.selectbox('지인 여부', acquaintance_list)
            vehicle_number = st.text_input('차량 번호')
            payment_method = st.selectbox('결제 수단', payment_method_list)
            individual_or_group = st.selectbox('개인/그룹', individual_or_group_list)
            start_date = st.date_input('시작일')
            repeat_number = st.number_input('반복 횟수', min_value=0, format="%.d")
            membership_grade = st.selectbox('테니스 Level', membership_grade_list)
            coach = st.selectbox('담당 코치', coach_list)
            payment_amount = st.number_input('결제 금액', min_value=0, format="%.d")
            payment_status = st.selectbox('결제 완료 수단', payment_status_list)
            discount_rate = st.number_input('할인율 (%)', min_value=0.0, max_value=100.0, format="%.2f")
            # registration_month = st.selectbox('등록 월', [f'{i:02d}' for i in range(1, 13)])
            registration_source = st.selectbox('등록 경로', registration_source_list)
            notes = st.text_area('비고')
            st.session_state.member_info = {
                '회원명': member_name,
                '연령': age,
                '성별': gender,
                '진행 여부': status,
                '지인 여부': acquaintance,
                '연락처': contact,
                '차량 번호': vehicle_number,
                '결제 수단': payment_method,
                '개인/그룹': individual_or_group,
                '시작일': start_date,
                '반복 횟수': repeat_number,
                '회원 등급': membership_grade,
                '담당 코치': coach,
                '결제 금액': payment_amount,
                '결제 완료 수단': payment_status,
                '할인율': discount_rate,
                # '등록 월': registration_month,
                '등록 경로': registration_source,
                '비고': notes
            }


        df_member_table = pd.DataFrame.from_dict(st.session_state.member_info, orient='index' )
        print(df_member_table.T)
        st.dataframe(df_member_table.T)

        st.title("요일 및 시간대 선택")
        # 요일 목록
        days_of_week = ["월", "화", "수", "목", "금", "토", "일"]
        # 요일 선택
        selected_day = st.selectbox("요일 선택", days_of_week)
        # 시간대 목록 생성
        time_slots = create_time_slots()
        # 시간대 선택
        selected_time = st.selectbox("시간대 선택", time_slots)
        # 선택 추가 버튼

        col1_day, col2_day = st.columns(2)
        with col1_day:
            if st.button("선택 추가"):
                st.session_state.selected_slots.append((selected_day, selected_time))
                st.success(f"{selected_day} - {selected_time} 추가됨")
        with col2_day:
            if st.button("초기화"):
                st.session_state.selected_slots = []
                st.success("선택이 초기화되었습니다")
        # 선택된 요일 및 시간대 표시
        st.write("선택된 요일 및 시간대:")

        df_time = pd.DataFrame(st.session_state.selected_slots, columns=["요일", "시간대"])

        st.dataframe(df_time)

        # 선택 초기화 버튼

        st.write("")
        st.write("")
        if st.button("회원 정보 DB에 저장 및 캘린더에 박기"):
            try:
                # Example usage
                schedule = []
                for i in range(len(df_time)):
                    # print(df_time.iloc[i,0])
                    dayofweek = df_time.iloc[i,0]
                    timeofday = df_time.iloc[i,1]
                    schedule.append(f"{dayofweek} {timeofday}")
                    print(schedule)

                matching_dates = be.get_matching_dates(schedule, start_date, 2030)
                member_yuji = f"{member_name} {coach}"

                df = pd.read_csv("raw_date.csv", header=0, index_col=0, encoding='cp949')
                # Fill the DataFrame with the schedule
                date_str, time_str = be.fill_dataframe_with_schedule(df, matching_dates, repeat_number,member_yuji)
                if date_str != 0 and time_str != 0:
                    st.warning(f"{date_str}날짜에 {time_str}시간대의 코트 및 강사의 schedule이 꽉 차있습니다. 다른 시간대로 다시 시도하세요")
                else:
                    print(df)
                    csv_file_path = save_member_info(st.session_state.member_info)
                    df.to_csv("raw_date.csv", encoding='cp949')
                    st.success(f'정보가 {csv_file_path}에 저장되었습니다.')



            except Exception as err:
                print(err)
                st.warning(f"저장 실패!! {err}")


    elif tab == "스케줄 변경":
        st.header("스케줄 변경")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("변경 전")
            old_date = st.date_input("날짜 선택", key="old_date", value=datetime.today())
            time_slots = create_time_slots()
            old_start_time = st.selectbox("시간 선택", time_slots, key="old_time")

        with col2:
            st.subheader("변경 후")
            new_date = st.date_input("날짜 선택", key="new_date", value=datetime.today())
            new_start_time = st.selectbox("시간 선택", time_slots, key="new_time")

        if st.button("변경 확인"):
            st.write(f"변경 전 날짜: {old_date}")
            st.write(f"변경 전 시간대: {old_start_time}")
            st.write(f"변경 후 날짜: {new_date}")
            st.write(f"변경 후 시간대: {new_start_time}")

    elif tab == "보강 등록":
        st.header("보강 등록")
        add_date = st.date_input("날짜 선택", key="add_date", value=datetime.today())
        time_slots = create_time_slots()
        add_start_time = st.selectbox("시간 선택", time_slots, key="add_time")



        if st.button("보강 확인"):
            st.write(f"보강 날짜: {add_date}")
            st.write(f"보강 시간대: {add_start_time}")




if __name__ == "__main__":
    main()
