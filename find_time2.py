import streamlit as st
from datetime import datetime, time, timedelta

#二つの時間を比べ、共通の空き時間を算出する関数
def intersect_two_lists(list1, list2):
    result = []
    #一人目の時間
    for s1, e1 in list1:
        #二人目の時間
        for s2, e2 in list2:
            #遅い方の開始時間と早いほうの終了時間を算出
            start = max(s1, s2)
            end = min(e1, e2)
            #もし開始時間が終了時間より前であれば、共通の空き時間として追加
            if start < end:
                result.append((start, end))
    return result

#複数人の空き時間リストを受け取り、共通の空き時間を算出する関数
def find_common_times(free_times_list):
    #もし空き時間のリストが空なら、空のリストを返す
    if not free_times_list:
        return []
    #最初の人の空き時間を基準として、順番に共通の空き時間を算出する
    current = free_times_list[0]
    #順番に共通の空き時間を算出していく
    for times in free_times_list[1:]:
        current = intersect_two_lists(current, times)
        #もし共通の空き時間がなくなったら、早期に空のリストを返す
        if not current:
            return []
    #共通の空き時間を返す    
    return current

#二つの時間を受け取り、重なり合う時間を一つの時間にまとめる関数
def merge_intervals(intervals):
    #もし空き時間のリストが空なら、空のリストを返す
    if not intervals:
        return []
    #空き時間のリストを開始時間順に並べる
    intervals = sorted(intervals)
    #最初の空き時間を基準する
    merged = [intervals[0]]
    #順番に空き時間を順番に取得する
    for s, e in intervals[1:]:
        #最後に追加した空き時間の終了時間を取得する
        last_s, last_e = merged[-1]
        #もし最後に追加した空き時間の終了時間が、現在の空き時間の開始時間よりも後であればまとめる
        if s <= last_e:
            merged[-1] = (last_s, max(last_e, e))

        #違ければ追加する    
        else:
            merged.append((s, e))
    return merged


st.title("共通空き時間候補自動提案ツール　ver.2")
st.write("参加人数を指定し、各自の空き時間を入力してください。")

date_range = st.date_input("対象日（範囲を選択可能）", value=(datetime(2026, 1, 1).date(), datetime(2026, 1, 1).date()))
#もし日付範囲がタプルまたはリストであれば、開始日と終了日を取得する。そうでなければ、開始日と終了日を同じ日に設定する。
if isinstance(date_range, tuple) or isinstance(date_range, list):
    start_date, end_date = date_range[0], date_range[1]
else:
    start_date = end_date = date_range
#参加人数を指定するための数値入力欄
num_people = st.number_input("参加人数", min_value=2, value=3, step=1)

people_free_inputs = []
#各参加者の空き時間を入力するためのループ
for i in range(1, num_people + 1):
    st.subheader(f"{i}人目の空き時間")
    count_key = f"p{i}_count"
    if count_key not in st.session_state:
        st.session_state[count_key] = 1
#ボタンを横並びに配置する
    col1, col2 = st.columns([1, 1])
    #ボタンが押されたら、カウントを増減する
    if col1.button("区間を追加", key=f"p{i}_add"):
        st.session_state[count_key] += 1
    if col2.button("最後の区間を削除", key=f"p{i}_remove"):
        if st.session_state[count_key] > 1:
            st.session_state[count_key] -= 1
#空き時間の入力欄を表示するためのループ
    intervals = []
    for j in range(1, st.session_state[count_key] + 1):
        s = st.time_input(f"開始時間 {j}", time(0, 0), key=f"p{i}_s{j}")
        e = st.time_input(f"終了時間 {j}", time(0, 0), key=f"p{i}_e{j}")
        intervals.append((s, e))
    people_free_inputs.append(intervals)

#空き時間を計算するボタンが押されたときの処理
if st.button("空き時間を計算する"):
    all_results = []  
    valid = True
    cur = start_date
    #日付範囲内でループして、各日の共通の空き時間を計算する
    while cur <= end_date:
        day_free = []
        for i, intervals in enumerate(people_free_inputs, start=1):
            person_list = []
            for idx, (s, e) in enumerate(intervals, start=1):
                dt_s = datetime.combine(cur, s)
                dt_e = datetime.combine(cur, e)
                #もし開始時間が終了時間よりも後であれば、警告を表示して処理を停止する
                if dt_s >= dt_e:
                    st.warning(f"{i}人目の{idx}番目の区間は開始時刻が終了時刻より前になるよう入力してください。")
                    valid = False
                #そうでなければ、空き時間リストに追加する
                person_list.append((dt_s, dt_e))
            person_list = merge_intervals(sorted(person_list))
            day_free.append(person_list)
        #もし入力が無効であれば、処理を停止する
        if not valid:
            st.stop()
        #共通の空き時間を計算する
        common = find_common_times(day_free)
        all_results.append((cur, common))
        cur += timedelta(days=1)
    #結果を表示する
    st.subheader("提案時間")
    any_found = False
    for d, slots in all_results:
        st.write(f"■ {d.isoformat()}")
        if not slots:
            st.info("  共通の空き時間はありません")
        else:
            any_found = True
            for s, e in slots:
                st.success("  候補時間: " + s.strftime('%H:%M') + " ~ " + e.strftime('%H:%M'))

            