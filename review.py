import streamlit as st

st.title("review")


st.sidebar.title('🌸')

select_multi_species = st.sidebar.multiselect(
    'type',
    ['Italian food','fast food','korean food','chinese food'],

)

select_multi_species = st.sidebar.multiselect(
    'region',
    ['soeul','busan','deagu','ulsan'],

)
st.sidebar.button(
    "filter apply "
)

st.button("포스팅 검색하기",icon='🖊️',use_container_width=True)
st.button("포스팅 작성하기",icon='🔍',use_container_width=True)
tab1, tab2, tab3,tab4 = st.tabs(['Italian food','fast food','korean food','chinese food'])


with tab1:
    st.header("Italian food")
    col1,col2=st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("브로밀")
            st.image("https://cdn.pixabay.com/photo/2019/01/25/21/36/spaghetti-3955377_960_720.jpg")
            st.write("위치: 서울 은평구 불광로 16-19 1층 브로밀")
            st.write("대표 메뉴 : 짬뽕파스타")
            st.button("더보기", use_container_width=True,key=1)

    with col2:
        with st.container(border=True):
            st.subheader("대디스 바베큐")
            st.image("https://cdn.pixabay.com/photo/2019/01/25/21/35/restaurant-3955372_960_720.jpg",
                     use_column_width='auto', caption='내가 가장 좋아하는 음식, 바베큐')
            st.write("위치: 경기 양평군 옥천면 옥천문화마을3길 15-24")
            st.write("대표 메뉴 : 항아리 바베큐")
            st.button("더보기",use_container_width=True,key=2)
with tab2:
    st.header("fast food")
    st.image("https://cdn.pixabay.com/photo/2020/10/05/19/55/hamburger-5630646_960_720.jpg", width=700,caption='햄버거가 건강에 나쁘다는 것은 편견')
with tab3:
    st.header("Korean food")
    st.image("https://cdn.pixabay.com/photo/2019/09/05/01/08/food-4452839_960_720.jpg", width=700,caption='역시 제육')

with tab4:
    st.header("Chinese food")
    st.image("https://cdn.pixabay.com/photo/2015/07/29/18/29/crayfish-866400_960_720.jpg", width=700)
