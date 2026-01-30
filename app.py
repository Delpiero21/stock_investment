"""
섹터별 턴어라운드 대시보드
KOSPI, KOSDAQ, 미국 시장의 섹터별/종목별 턴어라운드 시각화
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="섹터별 턴어라운드 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 스타일 적용
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .turnaround-high { color: #00d26a; font-weight: bold; }
    .turnaround-mid { color: #ffc107; font-weight: bold; }
    .turnaround-low { color: #ff6b6b; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #f0f2f6;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


# ============ 데이터 로딩 함수들 ============

@st.cache_data(ttl=3600)
def load_market_data(market: str, use_real_data: bool = False):
    """시장 데이터 로드 (실제 API 또는 샘플 데이터)"""
    
    if use_real_data:
        try:
            return load_real_data(market)
        except Exception as e:
            st.warning(f"실제 데이터 로드 실패: {e}. 샘플 데이터를 사용합니다.")
    
    return generate_sample_data(market)


def load_real_data(market: str):
    """실제 데이터 로드 (FinanceDataReader 사용)"""
    import FinanceDataReader as fdr
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=120)
    
    if market == "KOSPI":
        # KOSPI 섹터별 대표 종목
        sector_stocks = {
            '반도체': ['005930', '000660', '042700'],  # 삼성전자, SK하이닉스, 한미반도체
            '자동차': ['005380', '000270', '012330'],  # 현대차, 기아, 현대모비스
            '금융': ['105560', '055550', '086790'],    # KB금융, 신한지주, 하나금융
            '바이오': ['207940', '068270', '326030'],  # 삼성바이오, 셀트리온, SK바이오팜
            '2차전지': ['373220', '006400', '096770'], # LG에너지솔루션, 삼성SDI, SK이노베이션
            '철강': ['005490', '004020', '001230'],    # POSCO홀딩스, 현대제철, 동국제강
            '화학': ['051910', '010950', '011170'],    # LG화학, S-Oil, 롯데케미칼
            '조선': ['009540', '010620', '042660'],    # 한국조선해양, 현대미포조선, 대우조선해양
        }
    elif market == "KOSDAQ":
        sector_stocks = {
            '바이오': ['196170', '298380', '141080'],  # 알테오젠, 에이비엘바이오, 레고켐바이오
            '2차전지소재': ['247540', '066570', '278280'], # 에코프로비엠, LG전자, 천보
            '게임': ['263750', '112040', '036570'],    # 펄어비스, 위메이드, 엔씨소프트
            'IT서비스': ['035420', '035720', '251270'], # NAVER, 카카오, 넷마블
            '반도체장비': ['036830', '098460', '322310'], # 솔브레인, 고영, 오로스테크놀로지
        }
    else:  # US
        sector_stocks = {
            'Technology': ['NVDA', 'AAPL', 'MSFT', 'GOOGL', 'META'],
            'Healthcare': ['UNH', 'JNJ', 'PFE', 'ABBV', 'MRK'],
            'Financials': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
            'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG'],
            'Consumer': ['AMZN', 'TSLA', 'WMT', 'HD', 'NKE'],
        }
    
    all_data = []
    
    for sector, stocks in sector_stocks.items():
        for stock in stocks:
            try:
                df = fdr.DataReader(stock, start_date, end_date)
                if len(df) > 0:
                    df['Sector'] = sector
                    df['Stock'] = stock
                    all_data.append(df)
            except:
                continue
    
    if all_data:
        return pd.concat(all_data)
    else:
        raise Exception("데이터를 가져올 수 없습니다")


def generate_sample_data(market: str) -> dict:
    """샘플 데이터 생성"""
    
    np.random.seed(42)
    
    sectors_config = {
        'KOSPI': {
            '반도체': ['삼성전자', 'SK하이닉스', 'DB하이텍', '리노공업', '한미반도체'],
            '자동차': ['현대차', '기아', '현대모비스', '만도', 'HL만도'],
            '금융': ['KB금융', '신한지주', '하나금융', '우리금융', '삼성생명'],
            '바이오': ['삼성바이오', '셀트리온', 'SK바이오팜', '유한양행', '녹십자'],
            '2차전지': ['LG에너지솔루션', '삼성SDI', 'SK이노베이션', '에코프로비엠', '포스코퓨처엠'],
            '철강': ['POSCO홀딩스', '현대제철', '동국제강', '세아베스틸', '고려아연'],
            '화학': ['LG화학', 'S-Oil', '롯데케미칼', '금호석유', 'SK케미칼'],
            '조선': ['한국조선해양', '현대미포조선', '삼성중공업', '대우조선해양', 'HD현대'],
            '건설': ['삼성물산', '현대건설', 'GS건설', '대림산업', 'DL이앤씨'],
            '유통': ['삼성물산', '신세계', '현대백화점', '롯데쇼핑', 'BGF리테일'],
        },
        'KOSDAQ': {
            'IT서비스': ['카카오게임즈', '더존비즈온', '위메이드', '컴투스', '네오위즈'],
            '게임': ['크래프톤', '펄어비스', '스마일게이트', '넷마블', '웹젠'],
            '바이오': ['알테오젠', '에이비엘바이오', '레고켐바이오', '펩트론', '메드팩토'],
            '엔터테인먼트': ['하이브', 'JYP엔터', 'SM엔터', '와이지엔터', '큐브엔터'],
            '반도체장비': ['원익IPS', '주성엔지니어링', '피에스케이', '테스', '유진테크'],
            '2차전지소재': ['에코프로', '엘앤에프', '코스모신소재', '나노신소재', '천보'],
            '로봇': ['레인보우로보틱스', '두산로보틱스', '로보스타', '뉴로메카', '티로보틱스'],
            'AI/SW': ['솔트룩스', '마인즈랩', '셀바스AI', '코난테크놀로지', '플리토'],
            '의료기기': ['오스템임플란트', '레이', '바텍', '디오', '덴티움'],
            '신재생에너지': ['씨에스윈드', '한화솔루션', 'OCI', 'SK가스', '두산퓨얼셀'],
        },
        'US': {
            'Technology': ['NVIDIA', 'Apple', 'Microsoft', 'Google', 'Meta'],
            'Healthcare': ['UnitedHealth', 'Johnson & Johnson', 'Pfizer', 'Abbvie', 'Merck'],
            'Financials': ['JPMorgan', 'Bank of America', 'Wells Fargo', 'Goldman Sachs', 'Morgan Stanley'],
            'Energy': ['Exxon Mobil', 'Chevron', 'ConocoPhillips', 'Schlumberger', 'EOG Resources'],
            'Consumer': ['Amazon', 'Tesla', 'Walmart', 'Home Depot', 'Nike'],
            'Industrials': ['Caterpillar', 'Boeing', 'Honeywell', '3M', 'Union Pacific'],
            'Materials': ['Linde', 'Air Products', 'Sherwin-Williams', 'Freeport-McMoRan', 'Nucor'],
            'Real Estate': ['Prologis', 'American Tower', 'Crown Castle', 'Equinix', 'Public Storage'],
            'Utilities': ['NextEra Energy', 'Duke Energy', 'Southern Company', 'Dominion', 'Exelon'],
            'Communication': ['Verizon', 'AT&T', 'T-Mobile', 'Comcast', 'Disney'],
        }
    }
    
    sectors = sectors_config.get(market, sectors_config['KOSPI'])
    
    # 날짜 생성 (최근 90일)
    dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
    
    sector_data = []
    stock_data = []
    
    for sector_name, stocks in sectors.items():
        # 섹터가 턴어라운드 중인지 결정
        is_turnaround = np.random.random() > 0.4
        turnaround_day = np.random.randint(30, 60) if is_turnaround else None
        
        # 섹터 가격 데이터 생성
        base_price = 100
        prices = []
        
        for i in range(len(dates)):
            if is_turnaround:
                if i < turnaround_day:
                    # 하락 구간
                    price = base_price - (turnaround_day - i) * 0.3 + np.random.randn() * 1
                else:
                    # 상승 구간
                    price = base_price + (i - turnaround_day) * 0.4 + np.random.randn() * 1
            else:
                # 횡보 또는 하락
                price = base_price + np.cumsum(np.random.randn(i+1) * 0.5)[-1]
            prices.append(max(price, 50))
        
        prices = np.array(prices)
        
        # 기술적 지표 계산
        ma20 = pd.Series(prices).rolling(20).mean().iloc[-1]
        ma60 = pd.Series(prices).rolling(60).mean().iloc[-1]
        
        # RSI 계산
        delta = pd.Series(prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        low_price = min(prices)
        current_price = prices[-1]
        from_low = ((current_price - low_price) / low_price) * 100
        
        # 거래량 (턴어라운드 시 증가)
        volume_ratio = 150 + np.random.rand() * 50 if is_turnaround else 80 + np.random.rand() * 40
        
        # 외국인 순매수
        foreign_buy = np.random.randn() * 500 + (200 if is_turnaround else -100)
        
        # 턴어라운드 스코어 계산
        score = 0
        score += min(from_low / 2, 30)  # 저점 대비 상승률 (최대 30점)
        score += 20 if ma20 > ma60 else 0  # 골든크로스 (20점)
        score += min(max(rsi - 30, 0) / 2, 25)  # RSI (최대 25점)
        score += min(volume_ratio / 10, 15)  # 거래량 (최대 15점)
        score += 10 if foreign_buy > 0 else 0  # 외국인 순매수 (10점)
        
        sector_data.append({
            'sector': sector_name,
            'prices': prices.tolist(),
            'dates': dates.tolist(),
            'current_price': current_price,
            'from_low': round(from_low, 1),
            'ma20': ma20,
            'ma60': ma60,
            'ma20_vs_ma60': round((ma20 / ma60 - 1) * 100, 2) if ma60 else 0,
            'rsi': round(rsi, 1) if not np.isnan(rsi) else 50,
            'volume_ratio': round(volume_ratio, 1),
            'foreign_buy': round(foreign_buy, 1),
            'turnaround_score': round(min(score, 100)),
            'is_turnaround': is_turnaround,
        })
        
        # 개별 종목 데이터
        for stock_name in stocks:
            stock_turnaround = is_turnaround and np.random.random() > 0.3
            stock_from_low = from_low * (0.7 + np.random.rand() * 0.6)
            stock_rsi = rsi * (0.8 + np.random.rand() * 0.4) if not np.isnan(rsi) else 50
            stock_ma = (ma20 / ma60 - 1) * 100 * (0.7 + np.random.rand() * 0.6) if ma60 else 0
            
            stock_score = 0
            stock_score += min(stock_from_low / 2, 30)
            stock_score += 20 if stock_ma > 0 else 0
            stock_score += min(max(stock_rsi - 30, 0) / 2, 25)
            stock_score += min(volume_ratio / 10, 15) * (0.8 + np.random.rand() * 0.4)
            stock_score += 10 if np.random.random() > 0.5 else 0
            
            stock_data.append({
                'sector': sector_name,
                'stock': stock_name,
                'from_low': round(stock_from_low, 1),
                'ma20_vs_ma60': round(stock_ma, 2),
                'rsi': round(min(max(stock_rsi, 0), 100), 1),
                'volume_ratio': round(volume_ratio * (0.7 + np.random.rand() * 0.6), 1),
                'foreign_buy': round(foreign_buy * (0.5 + np.random.rand()), 1),
                'turnaround_score': round(min(max(stock_score, 0), 100)),
                'is_turnaround': stock_turnaround,
            })
    
    return {
        'sectors': pd.DataFrame(sector_data),
        'stocks': pd.DataFrame(stock_data),
        'dates': dates,
    }


# ============ 시각화 함수들 ============

def create_turnaround_ranking_chart(df: pd.DataFrame):
    """턴어라운드 스코어 랭킹 차트"""
    df_sorted = df.sort_values('turnaround_score', ascending=True)
    
    colors = ['#00d26a' if score >= 70 else '#ffc107' if score >= 50 else '#ff6b6b' 
              for score in df_sorted['turnaround_score']]
    
    fig = go.Figure(go.Bar(
        x=df_sorted['turnaround_score'],
        y=df_sorted['sector'],
        orientation='h',
        marker_color=colors,
        text=df_sorted['turnaround_score'],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>스코어: %{x}<extra></extra>'
    ))
    
    fig.update_layout(
        title='🔥 섹터별 턴어라운드 스코어',
        xaxis_title='스코어',
        yaxis_title='',
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    fig.update_xaxes(range=[0, 110])
    
    return fig


def create_price_trend_chart(data: dict, selected_sectors: list):
    """가격 추이 차트"""
    fig = go.Figure()
    
    colors = px.colors.qualitative.Set2
    
    for i, sector in enumerate(selected_sectors):
        sector_row = data['sectors'][data['sectors']['sector'] == sector].iloc[0]
        
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=sector_row['prices'],
            mode='lines',
            name=sector,
            line=dict(width=2, color=colors[i % len(colors)]),
            hovertemplate='<b>%{fullData.name}</b><br>날짜: %{x}<br>가격: %{y:.1f}<extra></extra>'
        ))
    
    fig.update_layout(
        title='📊 섹터별 가격 추이 (3개월)',
        xaxis_title='날짜',
        yaxis_title='지수 (기준=100)',
        height=400,
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    
    return fig


def create_indicator_chart(df: pd.DataFrame):
    """기술적 지표 종합 차트"""
    df_sorted = df.sort_values('turnaround_score', ascending=False)
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('저점 대비 상승률 & MA 크로스', 'RSI & 거래량'),
        horizontal_spacing=0.1
    )
    
    # 저점 대비 상승률
    colors1 = ['#00d26a' if x > 15 else '#ffc107' if x > 0 else '#ff6b6b' for x in df_sorted['from_low']]
    fig.add_trace(
        go.Bar(
            x=df_sorted['sector'],
            y=df_sorted['from_low'],
            name='저점 대비 상승률(%)',
            marker_color=colors1,
            hovertemplate='%{x}<br>저점 대비: %{y:.1f}%<extra></extra>'
        ),
        row=1, col=1
    )
    
    # MA 크로스 라인
    fig.add_trace(
        go.Scatter(
            x=df_sorted['sector'],
            y=df_sorted['ma20_vs_ma60'],
            name='MA20-MA60(%)',
            mode='lines+markers',
            line=dict(color='#8b5cf6', width=2),
            marker=dict(size=8),
            hovertemplate='%{x}<br>MA크로스: %{y:.1f}%<extra></extra>'
        ),
        row=1, col=1
    )
    
    # RSI
    colors2 = ['#00d26a' if x > 50 else '#ff6b6b' for x in df_sorted['rsi']]
    fig.add_trace(
        go.Bar(
            x=df_sorted['sector'],
            y=df_sorted['rsi'],
            name='RSI',
            marker_color=colors2,
            hovertemplate='%{x}<br>RSI: %{y:.1f}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # RSI 50 기준선
    fig.add_hline(y=50, line_dash="dash", line_color="gray", row=1, col=2)
    
    fig.update_layout(
        height=400,
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.08, xanchor='center', x=0.5),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    fig.update_xaxes(tickangle=45)
    
    return fig


def create_scatter_chart(df: pd.DataFrame):
    """턴어라운드 버블 차트"""
    fig = px.scatter(
        df,
        x='from_low',
        y='rsi',
        size='turnaround_score',
        color='turnaround_score',
        hover_name='sector',
        color_continuous_scale='RdYlGn',
        size_max=50,
        hover_data={
            'from_low': ':.1f',
            'rsi': ':.1f',
            'ma20_vs_ma60': ':.2f',
            'turnaround_score': True
        }
    )
    
    # 사분면 표시
    fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=15, line_dash="dash", line_color="gray", opacity=0.5)
    
    # 주석 추가
    fig.add_annotation(x=30, y=70, text="🚀 강한 턴어라운드", showarrow=False, font=dict(size=12, color="green"))
    fig.add_annotation(x=-5, y=30, text="⚠️ 약세 지속", showarrow=False, font=dict(size=12, color="red"))
    
    fig.update_layout(
        title='🎯 턴어라운드 매트릭스 (저점대비 vs RSI)',
        xaxis_title='저점 대비 상승률 (%)',
        yaxis_title='RSI',
        height=450,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


def create_stock_table(df: pd.DataFrame, sector: str):
    """종목별 상세 테이블"""
    sector_stocks = df[df['sector'] == sector].sort_values('turnaround_score', ascending=False)
    return sector_stocks


# ============ 메인 앱 ============

def main():
    # 헤더
    st.markdown('<p class="main-header">📈 섹터별 턴어라운드 대시보드</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">저점 대비 반등, 이동평균 크로스, RSI 등 턴어라운드 신호 모니터링</p>', unsafe_allow_html=True)
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")
        
        market = st.selectbox(
            "시장 선택",
            options=['KOSPI', 'KOSDAQ', 'US'],
            index=0
        )
        
        st.divider()
        
        use_real_data = st.checkbox(
            "실제 데이터 사용 (FinanceDataReader)",
            value=False,
            help="체크하면 실제 시장 데이터를 가져옵니다. 인터넷 연결이 필요합니다."
        )
        
        st.divider()
        
        sort_by = st.selectbox(
            "정렬 기준",
            options=['turnaround_score', 'from_low', 'rsi', 'ma20_vs_ma60'],
            format_func=lambda x: {
                'turnaround_score': '턴어라운드 스코어',
                'from_low': '저점 대비 상승률',
                'rsi': 'RSI',
                'ma20_vs_ma60': 'MA 크로스'
            }.get(x, x)
        )
        
        st.divider()
        
        st.markdown("### 📖 지표 설명")
        st.markdown("""
        - **턴어라운드 스코어**: 종합 점수 (0-100)
        - **저점 대비**: 3개월 저점 대비 상승률
        - **MA20-MA60**: 골든크로스 신호
        - **RSI**: 50↑ = 상승 모멘텀
        - **거래량**: 평균 대비 비율
        """)
    
    # 데이터 로드
    with st.spinner('데이터 로딩 중...'):
        data = load_market_data(market, use_real_data)
    
    sectors_df = data['sectors'].sort_values(sort_by, ascending=False)
    stocks_df = data['stocks']
    
    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["📊 섹터 분석", "🔍 종목 분석", "📈 상세 차트"])
    
    with tab1:
        # 상단 메트릭
        col1, col2, col3, col4 = st.columns(4)
        
        top_sector = sectors_df.iloc[0]
        turnaround_count = len(sectors_df[sectors_df['is_turnaround']])
        avg_score = sectors_df['turnaround_score'].mean()
        avg_from_low = sectors_df['from_low'].mean()
        
        with col1:
            st.metric(
                label="🏆 Top 섹터",
                value=top_sector['sector'],
                delta=f"스코어: {top_sector['turnaround_score']}"
            )
        with col2:
            st.metric(
                label="🔥 턴어라운드 섹터",
                value=f"{turnaround_count}개",
                delta=f"전체 {len(sectors_df)}개 중"
            )
        with col3:
            st.metric(
                label="📊 평균 스코어",
                value=f"{avg_score:.1f}",
                delta="양호" if avg_score >= 50 else "주의"
            )
        with col4:
            st.metric(
                label="📈 평균 저점대비",
                value=f"{avg_from_low:.1f}%",
                delta="상승" if avg_from_low > 0 else "하락"
            )
        
        st.divider()
        
        # 차트 영역
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.plotly_chart(create_turnaround_ranking_chart(sectors_df), use_container_width=True)
        
        with col_right:
            # 상위 5개 섹터 선택
            top_sectors = sectors_df.head(5)['sector'].tolist()
            st.plotly_chart(create_price_trend_chart(data, top_sectors), use_container_width=True)
        
        # 지표 차트
        st.plotly_chart(create_indicator_chart(sectors_df), use_container_width=True)
        
        # 버블 차트
        st.plotly_chart(create_scatter_chart(sectors_df), use_container_width=True)
    
    with tab2:
        st.subheader("🔍 종목별 턴어라운드 분석")
        
        # 섹터 선택
        selected_sector = st.selectbox(
            "섹터 선택",
            options=sectors_df['sector'].tolist(),
            index=0
        )
        
        # 선택된 섹터 정보
        sector_info = sectors_df[sectors_df['sector'] == selected_sector].iloc[0]
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            score_color = "turnaround-high" if sector_info['turnaround_score'] >= 70 else "turnaround-mid" if sector_info['turnaround_score'] >= 50 else "turnaround-low"
            st.markdown(f"**스코어**<br><span class='{score_color}'>{sector_info['turnaround_score']}</span>", unsafe_allow_html=True)
        with col2:
            st.metric("저점 대비", f"{sector_info['from_low']:.1f}%")
        with col3:
            st.metric("MA 크로스", f"{sector_info['ma20_vs_ma60']:.2f}%")
        with col4:
            st.metric("RSI", f"{sector_info['rsi']:.1f}")
        with col5:
            st.metric("거래량", f"{sector_info['volume_ratio']:.1f}%")
        
        st.divider()
        
        # 종목 테이블
        stock_table = create_stock_table(stocks_df, selected_sector)
        
        # 스타일링된 테이블
        def highlight_turnaround(row):
            score = row['스코어']
            if score >= 70:
                return ['background-color: rgba(0, 210, 106, 0.2)'] * len(row)
            elif score >= 50:
                return ['background-color: rgba(255, 193, 7, 0.2)'] * len(row)
            else:
                return ['background-color: rgba(255, 107, 107, 0.2)'] * len(row)
        
        styled_df = stock_table[['stock', 'from_low', 'ma20_vs_ma60', 'rsi', 'volume_ratio', 'turnaround_score']].copy()
        styled_df.columns = ['종목명', '저점대비(%)', 'MA크로스(%)', 'RSI', '거래량(%)', '스코어']
        
        st.dataframe(
            styled_df.style.apply(highlight_turnaround, axis=1).format({
                '저점대비(%)': '{:.1f}',
                'MA크로스(%)': '{:.2f}',
                'RSI': '{:.1f}',
                '거래량(%)': '{:.1f}',
                '스코어': '{:.0f}'
            }),
            use_container_width=True,
            height=400
        )
    
    with tab3:
        st.subheader("📈 상세 차트 분석")
        
        # 여러 섹터 선택
        selected_sectors = st.multiselect(
            "비교할 섹터 선택 (최대 5개)",
            options=sectors_df['sector'].tolist(),
            default=sectors_df.head(3)['sector'].tolist(),
            max_selections=5
        )
        
        if selected_sectors:
            st.plotly_chart(create_price_trend_chart(data, selected_sectors), use_container_width=True)
            
            # 선택된 섹터들의 상세 비교
            comparison_df = sectors_df[sectors_df['sector'].isin(selected_sectors)]
            
            fig = go.Figure()
            
            categories = ['저점대비', 'RSI', 'MA크로스', '거래량', '스코어']
            
            for _, row in comparison_df.iterrows():
                # 정규화된 값
                values = [
                    min(row['from_low'] / 50 * 100, 100),  # 저점대비 (50% = 100점)
                    row['rsi'],  # RSI (이미 0-100)
                    min(max((row['ma20_vs_ma60'] + 10) / 20 * 100, 0), 100),  # MA크로스 (-10~10% → 0-100)
                    min(row['volume_ratio'], 100),  # 거래량 (100% = 100점)
                    row['turnaround_score']  # 스코어
                ]
                values.append(values[0])  # 레이더 차트 닫기
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories + [categories[0]],
                    fill='toself',
                    name=row['sector'],
                    opacity=0.6
                ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                title='🎯 섹터별 레이더 차트',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("비교할 섹터를 선택해주세요.")
    
    # 푸터
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        💡 <b>Tip:</b> 실제 데이터 연동을 위해 FinanceDataReader 또는 yfinance를 설치하세요<br>
        <code>pip install finance-datareader yfinance</code>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
