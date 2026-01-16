# cloaud ver.
"""
📈 주가 대시보드 (Stock Dashboard)
- 깔끔하고 직관적인 UI/UX
- 효율적인 상태 관리
- 확장 가능한 구조
"""

import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date, timedelta
import numpy as np

# ==================== 페이지 설정 ====================
st.set_page_config(
    page_title="주가 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 유틸리티 함수 ====================

@st.cache_data(ttl=3600)  # 1시간 캐시
def load_stock_list(market="KOSPI"):
    """주식 목록 로드 (시총 순)"""
    try:
        df = fdr.StockListing(market)
        df = df.sort_values("Marcap", ascending=False)
        # 사용 가능한 컬럼만 선택
        available_cols = ["Code", "Name", "Marcap"]
        if "Market" in df.columns:
            available_cols.insert(2, "Market")
        if "Sector" in df.columns:
            available_cols.insert(3, "Sector")
        return df[available_cols]
    except Exception as e:
        st.error(f"주식 목록 로드 실패: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)  # 5분 캐시
def load_stock_data(code, start_date, end_date):
    """주가 데이터 로드"""
    try:
        df = fdr.DataReader(code, start_date, end_date)
        if df.empty:
            return None
        return df
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return None

def calculate_indicators(df):
    """기술적 지표 계산"""
    if df is None or df.empty:
        return df
    
    # 이동평균선
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()
    
    # 일간 변동률
    df['Daily_Return'] = df['Close'].pct_change() * 100
    
    # 볼린저 밴드
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
    
    return df

def create_candlestick_chart(df, stock_name, show_volume=True, show_ma=True, show_bb=False):
    """Plotly를 사용한 캔들스틱 차트 생성"""
    if df is None or df.empty:
        return None
    
    # 서브플롯 설정
    rows = 2 if show_volume else 1
    row_heights = [0.7, 0.3] if show_volume else [1]
    
    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,  # 수정: shared_xaxis -> shared_xaxes
        vertical_spacing=0.03,
        row_heights=row_heights,
        subplot_titles=(f'{stock_name} 주가 차트', '거래량') if show_volume else (f'{stock_name} 주가 차트',)
    )
    
    # 캔들스틱
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC',
            increasing_line_color='#FF4B4B',
            decreasing_line_color='#4B8BFF'
        ),
        row=1, col=1
    )
    
    # 이동평균선
    if show_ma:
        ma_configs = [
            ('MA5', '#00CC96', '5일'),
            ('MA20', '#AB63FA', '20일'),
            ('MA60', '#FFA15A', '60일')
        ]
        for ma_col, color, name in ma_configs:
            if ma_col in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df[ma_col],
                        name=name,
                        line=dict(color=color, width=1.5),
                        opacity=0.7
                    ),
                    row=1, col=1
                )
    
    # 볼린저 밴드
    if show_bb and 'BB_Upper' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_Upper'],
                name='BB Upper',
                line=dict(color='gray', width=1, dash='dash'),
                opacity=0.3
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_Lower'],
                name='BB Lower',
                line=dict(color='gray', width=1, dash='dash'),
                fill='tonexty',
                opacity=0.1
            ),
            row=1, col=1
        )
    
    # 거래량
    if show_volume:
        colors = ['#FF4B4B' if close >= open else '#4B8BFF' 
                  for close, open in zip(df['Close'], df['Open'])]
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Volume'],
                name='거래량',
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )
    
    # 레이아웃
    fig.update_layout(
        height=700,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        template='plotly_white',
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='lightgray')
    
    return fig

def calculate_stats(df):
    """통계 정보 계산"""
    if df is None or df.empty:
        return {}
    
    period_return = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100)
    
    return {
        'current_price': df['Close'].iloc[-1],
        'change': df['Close'].iloc[-1] - df['Close'].iloc[-2] if len(df) > 1 else 0,
        'change_pct': df['Daily_Return'].iloc[-1] if 'Daily_Return' in df.columns else 0,
        'high': df['High'].max(),
        'low': df['Low'].min(),
        'volume_avg': df['Volume'].mean(),
        'volume_current': df['Volume'].iloc[-1],
        'period_return': period_return,
        'volatility': df['Daily_Return'].std() if 'Daily_Return' in df.columns else 0
    }

# ==================== 세션 상태 초기화 ====================

def init_session_state():
    """세션 상태 초기화"""
    defaults = {
        'selected_market': 'KOSPI',
        'selected_stock_idx': 0,
        'start_date': date.today() - timedelta(days=180),
        'end_date': date.today(),
        'show_volume': True,
        'show_ma': True,
        'show_bb': False,
        'period_preset': '6개월'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ==================== 사이드바 ====================

with st.sidebar:
    st.header("⚙️ 설정")
    
    # 시장 선택
    market = st.selectbox(
        "시장",
        options=['KOSPI', 'KOSDAQ', 'KONEX'],
        index=['KOSPI', 'KOSDAQ', 'KONEX'].index(st.session_state.selected_market),
        key='market_select'
    )
    
    if market != st.session_state.selected_market:
        st.session_state.selected_market = market
        st.session_state.selected_stock_idx = 0
        st.rerun()
    
    # 주식 목록 로드
    stocks_df = load_stock_list(st.session_state.selected_market)
    
    if not stocks_df.empty:
        # 검색 기능
        search_query = st.text_input("🔍 종목 검색", placeholder="종목명 또는 코드 입력")
        
        if search_query:
            mask = (stocks_df['Name'].str.contains(search_query, case=False, na=False) | 
                    stocks_df['Code'].str.contains(search_query, case=False, na=False))
            filtered_stocks = stocks_df[mask]
        else:
            filtered_stocks = stocks_df.head(100)  # 상위 100개만 표시
        
        # 종목 선택
        stock_options = [f"{row['Code']} - {row['Name']}" for _, row in filtered_stocks.iterrows()]
        
        if stock_options:
            selected = st.selectbox(
                "종목 선택",
                options=stock_options,
                index=min(st.session_state.selected_stock_idx, len(stock_options) - 1),
                key='stock_select'
            )
            
            selected_idx = stock_options.index(selected)
            selected_code = filtered_stocks.iloc[selected_idx]['Code']
            selected_name = filtered_stocks.iloc[selected_idx]['Name']
        else:
            st.warning("검색 결과가 없습니다.")
            selected_code = None
            selected_name = None
    else:
        st.error("종목 목록을 불러올 수 없습니다.")
        selected_code = None
        selected_name = None
    
    st.divider()
    
    # 기간 설정
    st.subheader("📅 조회 기간")
    
    period_preset = st.selectbox(
        "기간 프리셋",
        options=['1개월', '3개월', '6개월', '1년', '3년', '5년', '직접 설정'],
        index=['1개월', '3개월', '6개월', '1년', '3년', '5년', '직접 설정'].index(st.session_state.period_preset)
    )
    
    if period_preset != '직접 설정':
        period_map = {
            '1개월': 30,
            '3개월': 90,
            '6개월': 180,
            '1년': 365,
            '3년': 1095,
            '5년': 1825
        }
        st.session_state.start_date = date.today() - timedelta(days=period_map[period_preset])
        st.session_state.end_date = date.today()
        st.session_state.period_preset = period_preset
    else:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "시작일",
                value=st.session_state.start_date,
                max_value=date.today()
            )
        with col2:
            end_date = st.date_input(
                "종료일",
                value=st.session_state.end_date,
                max_value=date.today()
            )
        
        st.session_state.start_date = start_date
        st.session_state.end_date = end_date
        st.session_state.period_preset = '직접 설정'
    
    st.divider()
    
    # 차트 옵션
    st.subheader("📊 차트 설정")
    st.session_state.show_volume = st.checkbox("거래량 표시", value=st.session_state.show_volume)
    st.session_state.show_ma = st.checkbox("이동평균선 표시", value=st.session_state.show_ma)
    st.session_state.show_bb = st.checkbox("볼린저 밴드 표시", value=st.session_state.show_bb)

# ==================== 메인 화면 ====================

st.title("📈 주가 대시보드")

if selected_code:
    # 데이터 로드
    with st.spinner('데이터 로딩 중...'):
        df = load_stock_data(
            selected_code,
            st.session_state.start_date,
            st.session_state.end_date
        )
    
    if df is not None and not df.empty:
        # 지표 계산
        df = calculate_indicators(df)
        stats = calculate_stats(df)
        
        # 종목 정보 헤더
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"## {selected_name} ({selected_code})")
        with col2:
            if st.button("🔄 새로고침", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        
        # 주요 지표 카드
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            change_color = "normal" if stats['change'] >= 0 else "inverse"
            st.metric(
                "현재가",
                f"{stats['current_price']:,.0f}원",
                f"{stats['change']:+,.0f}원 ({stats['change_pct']:+.2f}%)",
                delta_color=change_color
            )
        
        with col2:
            st.metric("기간 수익률", f"{stats['period_return']:+.2f}%")
        
        with col3:
            st.metric("최고가", f"{stats['high']:,.0f}원")
        
        with col4:
            st.metric("최저가", f"{stats['low']:,.0f}원")
        
        with col5:
            st.metric("변동성", f"{stats['volatility']:.2f}%")
        
        st.divider()
        
        # 차트
        fig = create_candlestick_chart(
            df,
            selected_name,
            show_volume=st.session_state.show_volume,
            show_ma=st.session_state.show_ma,
            show_bb=st.session_state.show_bb
        )
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # 상세 통계
        with st.expander("📊 상세 통계", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 가격 정보")
                st.markdown(f"- **현재가**: {stats['current_price']:,.0f}원")
                st.markdown(f"- **전일 대비**: {stats['change']:+,.0f}원 ({stats['change_pct']:+.2f}%)")
                st.markdown(f"- **기간 최고가**: {stats['high']:,.0f}원")
                st.markdown(f"- **기간 최저가**: {stats['low']:,.0f}원")
                st.markdown(f"- **기간 수익률**: {stats['period_return']:+.2f}%")
            
            with col2:
                st.markdown("### 거래량 정보")
                st.markdown(f"- **현재 거래량**: {stats['volume_current']:,.0f}")
                st.markdown(f"- **평균 거래량**: {stats['volume_avg']:,.0f}")
                st.markdown(f"- **변동성**: {stats['volatility']:.2f}%")
                
                if 'MA5' in df.columns:
                    st.markdown("### 이동평균")
                    st.markdown(f"- **5일 평균**: {df['MA5'].iloc[-1]:,.0f}원")
                    st.markdown(f"- **20일 평균**: {df['MA20'].iloc[-1]:,.0f}원")
                    st.markdown(f"- **60일 평균**: {df['MA60'].iloc[-1]:,.0f}원")
        
        # 원본 데이터 테이블
        with st.expander("📋 원본 데이터", expanded=False):
            display_df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            display_df.columns = ['시가', '고가', '저가', '종가', '거래량']
            st.dataframe(
                display_df.sort_index(ascending=False),
                use_container_width=True,
                height=400
            )
            
            # CSV 다운로드
            csv = display_df.to_csv(encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv,
                file_name=f"{selected_name}_{selected_code}_{st.session_state.start_date}_{st.session_state.end_date}.csv",
                mime="text/csv"
            )
    
    else:
        st.warning("⚠️ 선택한 기간에 데이터가 없습니다.")

else:
    st.info("👈 왼쪽 사이드바에서 종목을 선택해주세요.")

# ==================== 푸터 ====================

st.divider()
st.caption("💡 데이터 출처: FinanceDataReader | 실시간 데이터가 아닐 수 있습니다.")