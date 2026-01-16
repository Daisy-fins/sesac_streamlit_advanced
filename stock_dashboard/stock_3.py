# claude 통해 jake님 코드 수정 버전 
import streamlit as st
import FinanceDataReader as fdr 
import mplfinance as mpf 
import matplotlib.pyplot as plt 
from datetime import datetime, date, timedelta 

st.title("📈 주가 데이터 시각화")

# ----------------------------------------- 함수 정의 ----------------------------------------- 

# 일정 기간에 따른 특정 종목 주가 데이터를 df로 반환하는 함수 
@st.cache_data # 외부 대규모 데이터에서 값을 가져오기 때문에 캐시를 적용하여 효율을 높임 
def get_stock_data(code:str="005930", start=None, end=None):
    # 기본값 처리
    if start is None:
        start = date.today() - timedelta(days=365)
    if end is None:
        end = date.today()

    # start 처리 
    if isinstance(start, date):
        start_formatted = start.strftime("%Y-%m-%d")
    else:
        start_formatted = datetime.strptime(start, "%Y-%m-%d").strftime("%Y-%m-%d")

    # end 처리
    if isinstance(end, date):
        end_formatted = end.strftime("%Y-%m-%d")
    else:
        end_formatted = datetime.strptime(end, "%Y-%m-%d").strftime("%Y-%m-%d")
    
    # df 반환 
    return fdr.DataReader(code, start_formatted, end_formatted)

# 회사명과 시가 총액을 기준으로 정렬된 종목 코드를 df로 반환하는 함수
@st.cache_data
def get_stock_code(market="KOSPI", sort="Marcap"):
    df = fdr.StockListing(market)
    df.sort_values(by=sort, ascending=False, inplace=True) # sort를 기준으로 정렬 (내림차순)
    return df[["Code", "Name", "Marcap"]] # 종목 코드, 회사명, 시총 반환 

# ----------------------------------------- 세션 정의 ----------------------------------------- 

# 종목 코드 
if "code_index" not in st.session_state:
    st.session_state["code_index"] = 0

# 거래량
if "volume" not in st.session_state:
    st.session_state["volume"] = True # 거래량 출력 여부를 결정하는 값 

# 기간 
if "date_start" not in st.session_state:
    st.session_state["date_start"] = date.today() - timedelta(days=365)
if "date_end" not in st.session_state:
    st.session_state["date_end"] = date.today()

# 차트 스타일 
if "chart_style" not in st.session_state:
    st.session_state["chart_style"] = "default"

# ----------------------------------------- 사이드바 설정 ----------------------------------------- 

# 사이드바에서 여러 요소들을 입력받아 메인의 차트로 출력할 수 있도록 폼으로 구성 
with st.sidebar.form(key="side_form"):
    st.header("입력값 설정")

    #  ------------------ 1. 종목 코드 선택 ------------------
    
    # selectbox의 options 매개변수에 전달할 리스트 생성 
    codes_df = get_stock_code()
    choices_tuple = zip(codes_df["Code"], codes_df["Name"]) # 종목 코드와 종목명을 1:1로 매칭
    choices_list = [" : ".join(i) for i in choices_tuple] # selectbox에서 options 매개변수에 전달할 리스트 생성 

    # selectbox에서 선택된 항목의 index를 활용하여 code_index(session_state 업뎃용)와 code(df 생성 시 전달할 인수) 추출
    choice = st.selectbox("🟢 종목", options=choices_list, index=st.session_state["code_index"]) # index 인자로 초기값 설정 
    code_index = choices_list.index(choice) # session_state에 업데이트할 code의 index 추출
    code = choice.split(" : ")[0] # choice에서 index에 해당하는 종목 code 추출 -> df 생성에 전달할 인수 

    "---"
    # ------------------ 2. chart style 선택 ------------------
    chart_style_list = ['binance', 'binancedark', 'blueskies', 'brasil', 'charles', 'checkers', 'classic',
                        'default', 'ibd', 'kenan', 'mike', 'nightclouds', 'sas', 'starsandstripes', 'tradingview', 'yahoo']
    
    chart_style = st.selectbox("🟢 차트 스타일", chart_style_list, index=chart_style_list.index(st.session_state["chart_style"])) # index 인자로 초기값 설정
    
    "---"
    # ------------------ 3. 거래량 설정 ------------------
    st.write("🟢 거래량 시각화 유무")
    volume = st.checkbox("거래량", value=st.session_state["volume"])

    # ------------------ 4. 폼 제출 버튼 ------------------
    ""
    if st.form_submit_button("제출"):
        # 버튼 눌릴 때 session_state 업데이트 
        st.session_state["code_index"] = code_index 
        st.session_state["chart_style"] = chart_style 
        st.session_state["volume"] = volume 
        st.rerun()

# ----------------------------------------- 메인화면 설정 ----------------------------------------- 

# 차트 생성 함수 정의 (항상 입력값이 달라지기 때문에 캐시 적용 X)
def plot_chart(df):
    chart_style = st.session_state["chart_style"]
    marketcolors = mpf.make_marketcolors(up="red", down="blue")
    mpf_style = mpf.make_mpf_style(base_mpf_style=chart_style, marketcolors=marketcolors)

    fig, _ = mpf.plot(
        data=df,
        type="candle",
        style=mpf_style,
        figsize=(12, 7),
        fontscale=1.0,
        mav=(5, 20, 60),
        mavcolors=("green", "blue", "orange"),
        returnfig=True,
        volume=st.session_state["volume"]
    )   

    return st.pyplot(fig)

# 날짜 지정 
st.subheader("📅 기간 설정")

with st.form(key="date_form"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        new_date_start = st.date_input(
            "📆 시작일",
            value=st.session_state["date_start"],
            key="date_start_input"
        )
    
    with col2:
        new_date_end = st.date_input(
            "📆 종료일",
            value=st.session_state["date_end"],
            key="date_end_input"
        )
    
    with col3:
        st.write("")  # 정렬을 위한 공백
        set_today = st.checkbox("종료일을 오늘로 설정", value=False)
    
    # 폼 제출 버튼
    col_submit1, col_submit2, col_submit3 = st.columns([1, 1, 1])
    with col_submit2:
        submit_date = st.form_submit_button("📅 기간 적용", use_container_width=True)
    
    if submit_date:
        st.session_state["date_start"] = new_date_start
        if set_today:
            st.session_state["date_end"] = date.today()
        else:
            st.session_state["date_end"] = new_date_end
        st.rerun()

# 현재 설정된 기간 표시
st.info(f"📌 현재 조회 기간: **{st.session_state['date_start']}** ~ **{st.session_state['date_end']}**")

"---"

# 선택된 종목 정보 표시
codes_df = get_stock_code()
choices_tuple = zip(codes_df["Code"], codes_df["Name"])
choices_list = [" : ".join(i) for i in choices_tuple]
chart_title = choices_list[st.session_state["code_index"]].split(":")[-1].strip()

st.write(f"📌 현재 차트: **{chart_title}**")
st.write("📌 이동평균선(mav): :green[5일], :blue[20일], :orange[60일]")

"---"

# 주가 데이터 생성 및 차트 출력
try:
    code = choices_list[st.session_state["code_index"]].split(" : ")[0]
    df = get_stock_data(
        code, 
        st.session_state["date_start"], 
        st.session_state["date_end"]
    )
    
    if df.empty:
        st.warning("⚠️ 선택한 기간에 데이터가 없습니다. 다른 기간을 선택해주세요.")
    else:
        # 차트 생성 
        plot_chart(df)
        
        # 간단한 통계 정보 표시
        st.subheader("📊 주요 지표")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("최고가", f"{df['High'].max():,.0f}원")
        with col2:
            st.metric("최저가", f"{df['Low'].min():,.0f}원")
        with col3:
            st.metric("평균 거래량", f"{df['Volume'].mean():,.0f}")
        with col4:
            st.metric("최근 종가", f"{df['Close'].iloc[-1]:,.0f}원")
            
except Exception as e:
    st.error(f"❌ 데이터를 불러오는 중 오류가 발생했습니다: {str(e)}")
    st.info("💡 다른 종목이나 기간을 선택해보세요.")