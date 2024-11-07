import streamlit as st


def toggle_toggle():
    st.session_state.toggle = not st.session_state[st.session_state.toggle_key]
    st.session_state.toggle_key += 1

if "toggle" not in st.session_state:
    st.session_state.toggle = True  # Default to on

if "toggle_key" not in st.session_state:
    st.session_state.toggle_key = 1


col1, col2 = st.columns([9, 2])
with col1:
    st.title("my page")
    st.subheader("welcome to my page ID")
with col2:
    toggle = st.toggle(
        "밝은 모드", value=st.session_state.toggle, key=st.session_state["toggle_key"]
    )
st.image("https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png",width=100)

progress_text = "나의 매너점수"
my_bar = st.progress(30, text=progress_text)
st.write("")



st.button("내 정보 수정하기",use_container_width=True)
st.button("디스플레이 모드 변경",use_container_width=True,on_click=toggle_toggle)
st.button("알람 설정하기",use_container_width=True)
st.button("관심목록",icon='💗',use_container_width=True)
st.button("로그아웃",use_container_width=True)










