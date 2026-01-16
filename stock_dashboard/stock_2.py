# jake님 ver.
from plotly.graph_objs import volume
import streamlit as st
import FinanceDataReader as fdr 
import mplfinance as mpf 
import matplotlib.pyplot as plt 
from datetime import datetime, date, timedelta 

st.title("📈 주가 데이터 시각화")

# ----------------------------------------- 함수 정의 ----------------------------------------- 

# 일정 기간에 따른 특정 종목 주가 데이터를 df로 반환하는 함수 
@st.cache_data # 외부 대규모 데이터에서 값을 가져오기 때문에 캐시를 적용하여 효율을 높임 
def get_stock_data(
        code:str="005930", start = None, end = None):

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
    st.session_state["volume"] = True # 거개량 출력 여부를 결정하는 값 

# 기간 
if "date_start" not in st.session_state:
    st.session_state["date_start"] = date.today() - timedelta(days=365)
if "date_end" not in st.session_state:
    st.session_state["date_end"] = date.today()

# 차트 스타일 
if "chart_style" not in st.session_state:
    st.session_state["chart_style"] = "default"

""
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

    # "---"
    # # ------------------ 2. 기간 선정 ------------------
    # ndays = st.slider("🟢 기간(days)", min_value=5, max_value=720, value=st.session_state["ndays"], step=1)

    "---"
    # ------------------ 3. chart style 선택 ------------------
    chart_style_list = ['binance', 'binancedark', 'blueskies', 'brasil', 'charles', 'checkers', 'classic',
                        'default', 'ibd', 'kenan', 'mike', 'nightclouds', 'sas', 'starsandstripes', 'tradingview', 'yahoo']
    
    chart_style = st.selectbox("🟢 차트 스타일", chart_style_list, index=chart_style_list.index(st.session_state["chart_style"])) # index 인자로 초기값 설정
    
    "---"
    # ------------------ 4. 거개량 설정 ------------------
    ""
    st.write("🟢 거래량 시각화 유무")
    volume = st.checkbox("거래량", value=st.session_state["volume"])

    # ------------------ 5. 폼 제출 버튼 ------------------
    ""
    if st.form_submit_button("제출"):
        # 버튼 눌릴 때 session_state 업데이트 
        st.session_state["code_index"] = code_index 
        # st.session_state["ndays"] = ndays 
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
col1, col2, col3 = st.columns(3, vertical_alignment="center")

with col1:
    if st.button("start date", key="start_btn"):
        date_start = st.date_input("📆 start", value=st.session_state["date_start"])
    else:
        date_start = None

with col2:
    if st.button("end date", key="end_btn"):
        date_end = st.date_input("📆 end", value=st.session_state["date_end"])
    else:
        date_end = None

with col3:
    today_btn = st.button("today date", key="today_btn")
    if today_btn:
        date_today = date.today()

if today_btn: # 오늘 날짜 선택 시 end는 오늘날짜로 할당 
    date_end = date_today

# session_state에 날짜 정보 저장
st.session_state["date_start"] = date_start
st.session_state["date_end"] = date_end

# 주가 데이터 생성 
df = get_stock_data(code, date_start, date_end) # 위에서 만든 get_stock_data 활용 

"---"
# 선택된 종목으로 chart title 생성 
chart_title = choices_list[st.session_state["code_index"]].split(":")[-1] # 인덱스 번호에 해당하는 (코드:종목명)에서 종목명만 추출  
st.write(f"📌 현재 차트: {chart_title}")
st.write("📌 이동평균선(mav): :green[5일], :blue[20일], :orange[60일]")

# 차트 생성 
plot_chart(df)