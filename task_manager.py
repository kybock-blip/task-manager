import streamlit as st
import pandas as pd

st.set_page_config(page_title="업무 우선순위 관리", layout="wide")
st.title("📌 업무 우선순위 관리 웹 앱")

# 1. session_state 초기화
if "tasks" not in st.session_state:
    st.session_state["tasks"] = []
if "next_id" not in st.session_state:
    st.session_state["next_id"] = 1

def get_priority_level(score):
    if score >= 16:
        return "🔴 최우선"
    elif score >= 9:
        return "🟡 일반"
    else:
        return "🟢 낮음"

# 2. 사이드바: 업무 입력 폼
st.sidebar.header("➕ 새 업무 등록")
task_name = st.sidebar.text_input("업무명 입력", placeholder="예: 주간 보고서 작성")
importance = st.sidebar.slider("중요도 (1~5)", min_value=1, max_value=5, value=3)
urgency = st.sidebar.slider("긴급도 (1~5)", min_value=1, max_value=5, value=3)
allow_duplicate = st.sidebar.checkbox("동일 업무명 중복 등록 허용", value=False)

if st.sidebar.button("업무 추가", use_container_width=True):
    clean_name = task_name.strip()
    if not clean_name:
        st.sidebar.error("⚠️ 업무명을 입력해 주세요. (빈 업무명은 등록할 수 없습니다)")
    else:
        existing_names = [t["업무명"] for t in st.session_state["tasks"]]
        if not allow_duplicate and clean_name in existing_names:
            st.sidebar.warning("⚠️ 이미 등록된 업무명입니다. 중복 등록하려면 위 체크박스를 선택하세요.")
        else:
            score = importance * urgency
            level = get_priority_level(score)
            st.session_state["tasks"].append({
                "id": st.session_state["next_id"],
                "업무명": clean_name,
                "중요도": importance,
                "긴급도": urgency,
                "점수": score,
                "등급": level
            })
            st.session_state["next_id"] += 1
            st.sidebar.success(f"✅ '{clean_name}' 업무가 등록되었습니다! ({score}점 / {level})")

# 3. 메인 화면: 등록된 업무 표시 및 관리
if not st.session_state["tasks"]:
    st.info("👈 왼쪽 사이드바에서 새로운 업무를 추가해 주세요.")
else:
    df = pd.DataFrame(st.session_state["tasks"])
    df_sorted = df.sort_values(by=["점수", "id"], ascending=[False, True]).reset_index(drop=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("전체 업무", f"{len(df_sorted)}건")
    col2.metric("🔴 최우선 (16점↑)", f"{len(df_sorted[df_sorted['점수'] >= 16])}건")
    col3.metric("🟡 일반 (9~15점)", f"{len(df_sorted[(df_sorted['점수'] >= 9) & (df_sorted['점수'] <= 15)])}건")
    col4.metric("🟢 낮음 (8점↓)", f"{len(df_sorted[df_sorted['점수'] <= 8])}건")

    st.markdown("---")

    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        st.subheader("📋 등록된 업무 목록 (점수 높은 순)")

    filter_level = st.radio(
        "등급 필터",
        ["전체", "🔴 최우선", "🟡 일반", "🟢 낮음"],
        horizontal=True
    )

    if filter_level != "전체":
        display_df = df_sorted[df_sorted["등급"] == filter_level]
    else:
        display_df = df_sorted

    export_df = display_df[["등급", "업무명", "점수", "중요도", "긴급도"]]

    # [추천 추가 기능] 업무 목록 CSV 다운로드 버튼
    with head_col2:
        csv_data = export_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 현재 목록 CSV 다운로드",
            data=csv_data,
            file_name="업무_우선순위_목록.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.dataframe(export_df, use_container_width=True, hide_index=True)
    st.markdown("---")

    # 4. 업무 선택 및 삭제 기능
    st.subheader("🗑️ 업무 삭제 및 초기화")
    col_del1, col_del2 = st.columns([3, 1])

    with col_del1:
        options = {
            f"[{row['등급']}] {row['업무명']} ({row['점수']}점 - 중요도:{row['중요도']}, 긴급도:{row['긴급도']}) #{row['id']}": row["id"]
            for _, row in df_sorted.iterrows()
        }
        selected_labels = st.multiselect("삭제할 업무를 선택하세요 (다중 선택 가능)", options=list(options.keys()))

    with col_del2:
        st.write("")
        st.write("")
        if st.button("선택 업무 삭제", use_container_width=True):
            if not selected_labels:
                st.warning("삭제할 업무를 먼저 선택해 주세요.")
            else:
                ids_to_remove = {options[label] for label in selected_labels}
                st.session_state["tasks"] = [
                    t for t in st.session_state["tasks"] if t["id"] not in ids_to_remove
                ]
                st.rerun()

        if st.button("전체 목록 초기화", use_container_width=True):
            st.session_state["tasks"] = []
            st.rerun()
