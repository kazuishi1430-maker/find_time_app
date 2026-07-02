import streamlit as st
from datetime import datetime,time

def find_match_times(free_times_a, free_times_b):
    match_times = []
    
    for start_a, end_a in free_times_a:
        for start_b, end_b in free_times_b:
            # 2つの時間帯の「最も遅い開始時刻」と「最も早い終了時刻」を取得
            overlap_start = max(start_a, start_b)
            overlap_end = min(end_a, end_b)
            
            # 開始時刻が終了時刻より前であれば、その時間は「重なっている」
            if overlap_start < overlap_end:
                match_times.append((overlap_start, overlap_end))
                
    return match_times
st.title("共通空き時間候補自動提案ツール")
st.write("お互いの空き時間を入力してください")
target_date = st.date_input("対象日",datetime(2026,7,5))
st.subheader("一人目の空き時間")
a_start = st.time_input("開始時間",time(0,0),key="a.start")
a_end = st.time_input("終了時間",time(0,0),key="a_end")
b_free = st.subheader("二人目の空き時間")
b_start = st.time_input("開始時間",time(0,0),key="b.start")
b_end = st.time_input("終了時間",time(0,0),key="b_end")

if st.button("空き時間を計算する"):
    dt_a_start = datetime.combine(target_date, a_start)
    dt_a_end = datetime.combine(target_date, a_end)
    dt_b_start = datetime.combine(target_date, b_start)
    dt_b_end = datetime.combine(target_date, b_end)

    a_free = [(dt_a_start, dt_a_end)]
    b_free = [(dt_b_start, dt_b_end)]
    
    result = find_match_times(a_free, b_free)
    
    st.subheader("提案時間")
    if not result:
        st.warning("共通の空き時間が見つかりませんでした。")
    else:
        for start, end in result:
            st.success("候補時間:"+str(start.strftime('%H:%M'))+"~"+str(end.strftime('%H:%M')))