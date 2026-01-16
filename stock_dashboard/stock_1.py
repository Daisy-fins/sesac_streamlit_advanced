"""
주가 대시보드 - 초급자 버전
7일차 파이썬 학습자를 위한 간단한 코드
"""

import streamlit as st
import FinanceDataReader as fdr
from datetime import datetime, timedelta

# 제목
st.title("📈 주가 보기")

# ========== 사이드바 ==========
st.sidebar.header("⚙️ 설정하기")

# 1. 종목 선택 - 간단하게 유명한 종목만
stock_list = {
    "삼성전자": "005930",
    "SK하이닉스": "000660",
    "네이버": "035420",
    "카카오": "035720",
    "현대차": "005380",
    "LG에너지솔루션": "373220",
    "삼성바이오로직스": "207940",
    "셀트리온": "068270",
    "POSCO홀딩스": "005490",
    "KB금융": "105560"
}

# 종목 고르기
choice = st.sidebar.selectbox("종목을 선택하세요", list(stock_list.keys()))
code = stock_list[choice]  # 선택한 종목의 코드 가져오기

# 2. 기간 선택 - 간단하게
period = st.sidebar.radio(
    "기간을 선택하세요",
    ["1개월", "3개월", "6개월", "1년"]
)

# 기간을 숫자로 바꾸기
days_str = ["1개월", "3개월", "6개월", "1년"]
days_int = [30, 90, 180, 365]
days_mapped = dict(zip(days_str, days_int))

# # 기간을 숫자로 바꾸기
# if period == "1개월":
#     days = 30
# elif period == "3개월":
#     days = 90
# elif period == "6개월":
#     days = 180
# else:  # 1년
#     days = 365

# 시작일, 종료일 계산
end_date = datetime.now()
start_date = end_date - timedelta(days=days_mapped[period])

# 3. 거래량 보기 여부
show_volume = st.sidebar.checkbox("거래량 보기", value=True)

# ========== 메인 화면 ==========

st.write(f"## {choice} 주가")
st.write(f"기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")

# 데이터 가져오기
try:
    # 주가 데이터 불러오기
    df = fdr.DataReader(code, start_date, end_date)
    
    # 데이터가 있는지 확인
    if len(df) == 0:
        st.warning("데이터가 없습니다.")
    else:
        # 1. 중요한 숫자 보여주기
        st.write("### 주요 정보")
        
        # 4개 칸 만들기
        col1, col2, col3, col4 = st.columns(4)
        
        # 현재 가격 (맨 마지막 종가)
        current_price = df['Close'].iloc[-1]
        col1.metric("현재 가격", f"{current_price:,.0f}원")
        
        # 최고 가격
        max_price = df['High'].max()
        col2.metric("최고 가격", f"{max_price:,.0f}원")
        
        # 최저 가격
        min_price = df['Low'].min()
        col3.metric("최저 가격", f"{min_price:,.0f}원")
        
        # 평균 거래량
        avg_volume = df['Volume'].mean()
        col4.metric("평균 거래량", f"{avg_volume:,.0f}")
        
        # 2. 그래프 그리기
        st.write("### 주가 그래프")
        
        # 선 그래프 (간단하게)
        st.line_chart(df['Close'])
        
        # 거래량 그래프 (선택한 경우만)
        if show_volume:
            st.write("### 거래량 그래프")
            st.bar_chart(df['Volume'])
        
        # 3. 표로 보기 (펼치기/접기 가능)
        with st.expander("📊 데이터 표로 보기"):
            # 최근 것부터 보이게 뒤집기
            df_show = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            df_show.columns = ['시가', '고가', '저가', '종가', '거래량']
            
            # 날짜 최신순으로 정렬
            df_show = df_show.sort_index(ascending=False)
            
            st.dataframe(df_show)

except Exception as e:
    # 에러가 나면 메시지 보여주기
    st.error(f"오류가 발생했습니다: {e}")
    st.info("다른 종목이나 기간을 선택해보세요.")

# 하단 설명
st.write("---")
st.caption("💡 FinanceDataReader를 사용해서 주가 데이터를 가져옵니다.")