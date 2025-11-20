import streamlit as st
import pandas as pd
import requests
import numpy as np
import plotly.express as px
from datetime import datetime

# [NEW] Supabase 라이브러리 추가
try:
    from supabase import create_client, Client
except ImportError:
    st.error("Supabase 라이브러리가 설치되지 않았습니다. 터미널에 'pip install supabase'를 입력하세요.")

# -----------------------------------------------------------
# 1. 페이지 설정 & 초기화
# -----------------------------------------------------------
st.set_page_config(
    page_title="LOAN.NAV - 금융 네비게이션", 
    page_icon="🧭", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🚨 API 키
API_KEY = "915bf715f20037800930f1adda0261dd" 

# Supabase 연결
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except:
        return None

supabase = init_supabase()

# -----------------------------------------------------------
# 2. UI/UX 커스텀 (Clean White 테마 고정)
# -----------------------------------------------------------

st.markdown("""
    <style>
    /* 전체 배경 및 폰트 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
    
    .stApp { 
        background-color: #F8F9FA; 
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    /* 브랜드 로고 스타일 */
    .brand-logo {
        font-size: 40px;
        font-weight: 900;
        background: linear-gradient(to right, #4F46E5, #2563EB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .brand-slogan {
        font-size: 14px;
        color: #6B7280;
        margin-top: -10px;
        margin-bottom: 30px;
        font-weight: 500;
    }
    
    /* 카드 디자인 (그림자 강화) */
    .grid-card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
        border: 1px solid #F3F4F6;
        transition: all 0.3s ease;
        height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .grid-card:hover {
        transform: translateY(-5px);
        border-color: #4F46E5;
        box-shadow: 0 20px 25px -5px rgba(79, 70, 229, 0.1), 0 8px 10px -6px rgba(79, 70, 229, 0.1);
    }
    
    /* 탭 디자인 (알약 형태) */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 8px; 
        background-color: #FFFFFF; 
        padding: 10px; 
        border-radius: 12px; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: transparent;
        border-radius: 8px;
        padding: 0 24px;
        font-weight: 700;
        border: none;
        color: #6B7280;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4F46E5 !important;
        color: white !important;
        box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
    }

    /* 뱃지 스타일 */
    .badge-rank {
        background-color: #4F46E5; color: white; 
        padding: 4px 10px; border-radius: 8px; font-size: 12px; font-weight: 800;
    }
    .badge-bank {
        background-color: #EEF2FF; color: #4F46E5;
        padding: 4px 8px; border-radius: 8px; font-size: 12px; font-weight: 700;
    }
    
    /* 텍스트 강조 */
    .highlight-rate { font-size: 28px; font-weight: 800; color: #EF4444; letter-spacing: -0.5px; }
    .sub-text { color: #6B7280; font-size: 13px; }
    
    /* 결과 박스 */
    .result-box {
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 20px;
        text-align: center;
        background-color: white;
        border: 2px solid #E5E7EB;
    }
    .result-safe { border-color: #10B981; background-color: #F0FDF4; }
    .result-warning { border-color: #F59E0B; background-color: #FFFBEB; }
    .result-danger { border-color: #EF4444; background-color: #FEF2F2; }
    
    .big-score { font-size: 36px; font-weight: 900; margin-bottom: 10px; color: #1F2937; }

    /* 입력 필드 강조 (선택적) */
    .stNumberInput label { font-weight: bold; color: #4F46E5; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# 3. 데이터 핸들링 함수
# -----------------------------------------------------------
@st.cache_data(show_spinner=False)
def fetch_loan_data(api_key, loan_type="credit"):
    if loan_type == "credit":
        url = f"http://finlife.fss.or.kr/finlifeapi/creditLoanProductsSearch.json?auth={api_key}&topFinGrpNo=020000&pageNo=1&resultType=json"
    else:
        url = f"http://finlife.fss.or.kr/finlifeapi/mortgageLoanProductsSearch.json?auth={api_key}&topFinGrpNo=020000&pageNo=1&resultType=json"
    
    try:
        response = requests.get(url)
        data = response.json()
        if 'result' not in data or data['result']['err_cd'] != '000': return None
        
        base_df = pd.DataFrame(data['result']['baseList'])
        option_df = pd.DataFrame(data['result']['optionList'])
        merged_df = pd.merge(option_df, base_df, on='fin_prdt_cd')
        return merged_df
    except:
        return None

# -----------------------------------------------------------
# 4. 사이드바 콘텐츠 (브랜딩 강화)
# -----------------------------------------------------------
with st.sidebar:
    # [NEW] 브랜딩 영역
    st.markdown('<div class="brand-logo">LOAN.NAV</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-slogan">사회초년생을 위한 금융 나침반 🧭</div>', unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 👤 &nbsp; 마이 프로필")
    user_name = st.text_input("이름", value="사회초년생")
    monthly_income = st.number_input("월 실수령액 (만원)", value=300, step=10)
    annual_income = monthly_income * 12
    
    st.caption(f"💰 연봉 환산: 약 {annual_income:,}만 원")
    
    st.write("") # 간격
    
    st.markdown("### 🎯 신용 정보")
    score_mapping = {
        "1~2등급 (900점↑)": "crdt_grad_1",
        "3~4등급 (800점↑)": "crdt_grad_4",
        "5~6등급 (700점↑)": "crdt_grad_5",
        "7등급 이하": "crdt_grad_6"
    }
    selected_score = st.selectbox("내 신용점수 구간", list(score_mapping.keys()))
    target_col = score_mapping[selected_score] 
    
    existing_loan = st.number_input("기존 대출 잔액 (만원)", value=0, step=100)
    
    st.divider()
    
    # 찜 목록 버튼 스타일링
    if st.button("❤️ 내 찜 목록 확인", use_container_width=True, type="primary"):
        if supabase:
            try:
                response = supabase.table("loans_bookmark").select("*").execute()
                if response.data:
                    st.toast(f"총 {len(response.data)}개의 상품이 저장되어 있습니다.")
                    with st.expander("📂 저장된 상품 리스트", expanded=True):
                        st.dataframe(pd.DataFrame(response.data)[['bank_name', 'product_name', 'interest_rate']], hide_index=True)
                else:
                    st.toast("찜한 상품이 없습니다.", icon="📭")
            except Exception as e:
                st.error("DB 연결 오류")
        else:
            st.warning("DB 설정이 필요합니다.")

# -----------------------------------------------------------
# 5. 메인 화면 구성
# -----------------------------------------------------------
st.title(f"👋 반가워요, {user_name}님!")
st.markdown("은행에 가기 전, **LOAN.NAV**에서 내 대출 체력을 먼저 확인하세요.")

# 탭 구성
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💵 신용대출 찾기", 
    "🏠 주택담보대출 찾기",
    "🚦 승인 확률 진단", 
    "📅 상환 시뮬레이션", 
    "🩺 금리인하 진단기"
])

# ===========================================================
# TAB 1: 신용대출 (Grid View)
# ===========================================================
with tab1:
    # [UX 개선] 헤더와 입력창을 좌우로 배치하여 강조
    c_header, c_input = st.columns([2, 1])
    
    with c_header:
        st.markdown("### 🏃🏻 급한 생활비/비상금 (신용대출)")
        st.markdown("금융감독원 실시간 데이터를 분석하여 **최저금리 순**으로 추천합니다.")
        if annual_income > 0: # 연봉 정보가 있을 때만
             st.caption(f"💡 {user_name}님의 연봉({annual_income:,}만원) 기준 안전 한도를 고려하세요.")

    with c_input:
        # 입력창을 우측 상단에 두드러지게 배치
        credit_amount = st.number_input("필요 금액 (만원)", 100, 10000, 2000, step=100, key="credit_amt")
    
    st.divider() # 구분선 추가로 헤더 영역과 리스트 영역 분리

    if credit_amount > annual_income:
        st.warning(f"⚠️ 연봉({annual_income}만원)보다 높은 금액은 1금융권 대출 승인이 어려울 수 있습니다.")

    with st.spinner("전국 은행 금리 스캔 중... 🔍"):
        df_credit = fetch_loan_data(API_KEY, "credit")
        
    if df_credit is not None:
        df_c = df_credit[df_credit[target_col].notnull()].copy()
        df_c[target_col] = pd.to_numeric(df_c[target_col])
        df_c = df_c.sort_values(by=target_col).drop_duplicates(['fin_prdt_cd'], keep='first').head(9)
        
        cols_per_row = 3
        products = [row for _, row in df_c.iterrows()]
        rows = [products[i:i + cols_per_row] for i in range(0, len(products), cols_per_row)]

        for row_idx, row_items in enumerate(rows):
            cols = st.columns(cols_per_row)
            for col_idx, product in enumerate(row_items):
                current_rank = (row_idx * cols_per_row) + col_idx + 1
                rate = product[target_col]
                rate_type = product.get('crdt_lend_rate_type_nm', '변동금리')
                monthly_int = int(credit_amount * 10000 * rate / 100 / 12)
                
                with cols[col_idx]:
                    st.markdown(f"""
                    <div class="grid-card">
                        <div>
                            <div style="display:flex; justify-content:space-between; align-items:start;">
                                <span class="badge-rank">TOP {current_rank}</span>
                                <span class="badge-bank">{product['kor_co_nm']}</span>
                            </div>
                            <h4 style="margin-top:20px; margin-bottom:10px; line-height:1.4; min-height:50px;">{product['fin_prdt_nm']}</h4>
                            <div class="sub-text">
                                {rate_type} | {product['join_way']}
                            </div>
                        </div>
                        <div style="text-align:right; margin-top:20px;">
                            <div class="sub-text">내 등급 기준 금리</div>
                            <div class="highlight-rate">{rate}%</div>
                            <div style="font-size:15px; font-weight:600; color:#374151;">월 이자 {monthly_int:,}원</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    b_col1, b_col2 = st.columns(2)
                    with b_col1:
                        with st.popover("📄 상세 분석", use_container_width=True):
                            st.markdown(f"### {product['kor_co_nm']} - {product['fin_prdt_nm']}")
                            st.divider()
                            period = 12
                            monthly_rate_dec = rate / 100 / 12
                            payment = (credit_amount * 10000 * monthly_rate_dec * (1+monthly_rate_dec)**period) / ((1+monthly_rate_dec)**period - 1)
                            total_interest = (payment * period) - (credit_amount * 10000)
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                st.metric("적용 금리", f"{rate}%")
                                st.metric("기간 (예시)", "12개월")
                            with c2:
                                st.metric("월 납입금", f"{int(payment):,}원")
                                st.metric("총 이자비용", f"{int(total_interest):,}원")
                            
                            st.caption("*원리금균등상환 기준 시뮬레이션입니다.")
                            st.markdown("---")
                            st.markdown("**상품 특징:** " + str(product.get('etc_note', '특이사항 없음')))
                    
                    with b_col2:
                        if st.button("찜하기 ❤️", key=f"c_like_{current_rank}", use_container_width=True):
                            if supabase:
                                try:
                                    supabase.table("loans_bookmark").insert({
                                        "user_name": user_name,
                                        "bank_name": product['kor_co_nm'],
                                        "product_name": product['fin_prdt_nm'],
                                        "interest_rate": float(rate)
                                    }).execute()
                                    st.toast(f"저장 완료!", icon="✅")
                                except:
                                    st.error("저장 실패")
                            else:
                                st.toast("DB 미연결", icon="⚠️")
    else:
        st.error("데이터를 불러오지 못했습니다.")

# ===========================================================
# TAB 2: 주택담보대출
# ===========================================================
with tab2:
    # [UX 개선] 헤더와 입력창 좌우 배치
    c_header, c_input = st.columns([2, 1])
    
    with c_header:
        st.markdown("### 🏠 내 집 마련의 꿈 (주택담보대출)")
        st.info("💡 주담대는 개인 신용보다 '담보물 가치'와 '시장 금리'의 영향을 받으므로, 최저~최고 금리 범위로 제공됩니다.")
    
    with c_input:
        house_amount = st.number_input("대출 희망 금액 (만원)", 5000, 100000, 20000, step=1000, key="house_amt")

    st.divider()

    with st.spinner("상품 스캔 중..."):
        df_mortgage = fetch_loan_data(API_KEY, "mortgage")

    if df_mortgage is not None and 'lend_rate_min' in df_mortgage.columns:
        df_m = df_mortgage.sort_values(by='lend_rate_min').drop_duplicates(['fin_prdt_cd'], keep='first').head(6)
        
        cols_per_row = 3
        products = [row for _, row in df_m.iterrows()]
        rows = [products[i:i + cols_per_row] for i in range(0, len(products), cols_per_row)]

        for row_idx, row_items in enumerate(rows):
            cols = st.columns(cols_per_row)
            for col_idx, product in enumerate(row_items):
                current_rank = (row_idx * cols_per_row) + col_idx + 1
                min_rate = product['lend_rate_min']
                max_rate = product['lend_rate_max']
                monthly_int = int(house_amount * 10000 * min_rate / 100 / 12)
                
                with cols[col_idx]:
                    st.markdown(f"""
                    <div class="grid-card">
                        <div>
                            <div style="display:flex; justify-content:space-between; align-items:start;">
                                <span class="badge-rank">TOP {current_rank}</span>
                                <span class="badge-bank">{product['kor_co_nm']}</span>
                            </div>
                            <h4 style="margin-top:20px; margin-bottom:10px; line-height:1.4; min-height:50px;">{product['fin_prdt_nm']}</h4>
                            <div class="sub-text">
                                {product.get('mrtg_type_nm', '아파트')} | {product.get('rpay_type_nm', '분할상환')}
                            </div>
                        </div>
                        <div style="text-align:right; margin-top:20px;">
                            <div class="sub-text">최저 금리 기준</div>
                            <div class="highlight-rate" style="color:#10B981;">{min_rate}%</div>
                            <div style="font-size:15px; font-weight:600; color:#374151;">월 이자 {monthly_int:,}원~</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    b_col1, b_col2 = st.columns(2)
                    with b_col1:
                        with st.popover("📄 상세 분석", use_container_width=True):
                            st.markdown(f"### {product['kor_co_nm']} - {product['fin_prdt_nm']}")
                            st.divider()
                            period = 360 
                            monthly_rate_dec = min_rate / 100 / 12
                            payment = (house_amount * 10000 * monthly_rate_dec * (1+monthly_rate_dec)**period) / ((1+monthly_rate_dec)**period - 1)
                            total_interest = (payment * period) - (house_amount * 10000)
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                st.metric("최저 금리", f"{min_rate}%")
                                st.metric("상환 기간", "30년 (가정)")
                            with c2:
                                st.metric("월 납입", f"{int(payment):,}원")
                                st.metric("총 이자", f"{int(total_interest/10000):,}만 원")
                            st.markdown("---")
                    
                    with b_col2:
                        if st.button("찜하기 ❤️", key=f"m_like_{current_rank}", use_container_width=True):
                            if supabase:
                                try:
                                    supabase.table("loans_bookmark").insert({
                                        "user_name": user_name,
                                        "bank_name": product['kor_co_nm'],
                                        "product_name": product['fin_prdt_nm'],
                                        "interest_rate": float(min_rate)
                                    }).execute()
                                    st.toast(f"저장 완료!", icon="✅")
                                except:
                                    st.error("저장 실패")
                            else:
                                st.toast("DB 미연결", icon="⚠️")
    else:
        st.error("데이터 로딩 실패")

# ===========================================================
# TAB 3: 승인 확률 진단
# ===========================================================
with tab3:
    # [UX 개선] 헤더와 핵심 입력(금액) 좌우 배치
    c_header, c_input = st.columns([2, 1])
    
    with c_header:
        st.header("🚦 AI 대출 승인 예측")
        st.info("나의 소득, 신용점수, 기존 대출 정보를 분석하여 1금융권 승인 가능성을 진단합니다.")
    
    with c_input:
        # '진단할 금액'을 우측 상단으로 올려서 강조
        diag_amount = st.number_input("신청할 대출금 (만원)", 100, 20000, 3000, step=100, key='diag_amt')
    
    st.divider()

    # 진단 로직
    total_loan = existing_loan + diag_amount
    estimated_annual_payment = total_loan * 0.25
    
    dsr_ratio = (estimated_annual_payment / annual_income * 100) if annual_income > 0 else 0
    lti_ratio = (total_loan / annual_income * 100) if annual_income > 0 else 0
    
    risk_score = 0
    reject_reasons = []
    
    if "7등급" in selected_score:
        risk_score += 3
        reject_reasons.append("신용점수가 1금융권 커트라인(6등급)보다 낮습니다.")
    elif "5~6등급" in selected_score:
        risk_score += 1
    
    if dsr_ratio > 70: 
        risk_score += 3
        reject_reasons.append(f"연 소득 대비 상환 부담(DSR)이 너무 큽니다. ({dsr_ratio:.1f}%)")
    elif dsr_ratio > 40:
        risk_score += 1
        reject_reasons.append("DSR 규제(40%)에 걸릴 위험이 있습니다.")
        
    if lti_ratio > 200:
        risk_score += 2
        reject_reasons.append(f"연봉의 2배({lti_ratio:.0f}%)를 초과하는 대출은 거절될 수 있습니다.")

    # 결과 표시
    st.markdown("#### 📊 진단 결과 리포트")
    
    if risk_score == 0:
        st.markdown(f"""
        <div class="result-box result-safe">
            <div class="big-score" style="color:#10B981;">승인 유력 🟢</div>
            <h3>"충분히 승인될 가능성이 높습니다!"</h3>
            <p style="color:#6B7280;">신용점수와 소득 대비 대출 규모가 안정권입니다.<br>
            1금융권 최저금리 상품을 적극적으로 공략해보세요.</p>
        </div>
        """, unsafe_allow_html=True)
    elif risk_score <= 2:
        st.markdown(f"""
        <div class="result-box result-warning">
            <div class="big-score" style="color:#D97706;">주의 필요 🟡</div>
            <h3>"승인은 가능하나 한도가 깎일 수 있습니다."</h3>
            <p style="color:#6B7280;">약간의 위험 요소가 발견되었습니다. <br>
            주거래 은행을 이용하거나, 대출 금액을 조금 줄여보세요.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="result-box result-danger">
            <div class="big-score" style="color:#DC2626;">거절 위험 🔴</div>
            <h3>"현재 조건으로는 승인이 어려울 수 있습니다."</h3>
            <p style="color:#6B7280;">주요 원인을 먼저 해결해야 합니다.</p>
        </div>
        """, unsafe_allow_html=True)
        
    c1, c2, c3 = st.columns(3)
    c1.metric("나의 DSR (예상)", f"{dsr_ratio:.1f}%", delta="40% 이하 권장", delta_color="inverse")
    c2.metric("연봉 대비 대출비율", f"{lti_ratio:.0f}%", delta="150% 이하 권장", delta_color="inverse")
    c3.metric("신용 안전도", selected_score.split('(')[0], delta="높을수록 좋음")
    
    if reject_reasons:
        st.error("🚨 **위험 요인 발견:**")
        for reason in reject_reasons:
            st.write(f"- {reason}")

# ===========================================================
# TAB 4: 상환 시뮬레이션
# ===========================================================
with tab4:
    # [UX 개선] 헤더와 핵심 입력(금액) 좌우 배치
    c_header, c_input = st.columns([2, 1])
    with c_header:
        st.header("📅 상환 계획 & 월급 쪼개기")
        st.markdown("빌리려는 금액과 이자율을 입력하면 **월급에서 얼마가 빠져나가는지** 계산해드립니다.")
    with c_input:
        sim_amt = st.number_input("빌릴 돈 (만원)", value=3000, key='sim_amt')

    st.divider()
    
    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        st.subheader("1️⃣ 추가 조건 설정")
        sim_rate = st.number_input("이자율 (%)", value=5.5)
        sim_period = st.slider("기간 (개월)", 12, 120, 36)
        monthly_rate = sim_rate / 100 / 12
        monthly_payment = (sim_amt * 10000 * monthly_rate * (1+monthly_rate)**sim_period) / ((1+monthly_rate)**sim_period - 1)
        
        st.markdown(f"""
        <div style="background-color:#EEF2FF; padding:20px; border-radius:10px; margin-top:20px;">
            <h4 style="margin:0; color:#4F46E5;">매달 갚아야 할 돈</h4>
            <h1 style="margin:0; color:#1F2937;">{int(monthly_payment):,}원</h1>
        </div>
        """, unsafe_allow_html=True)

    with col_sim2:
        st.subheader("2️⃣ 월급 방어력")
        rem_salary = (monthly_income * 10000) - monthly_payment
        fig = px.pie(values=[monthly_payment, max(0, rem_salary)], names=['상환금', '생활비'], 
                     color_discrete_sequence=['#EF4444', '#10B981'], hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("📋 월별 납입 스케줄표 확인하기 (클릭)"):
        schedule = []
        balance = sim_amt * 10000
        for i in range(sim_period):
            interest = balance * monthly_rate
            principal = monthly_payment - interest
            balance -= principal
            schedule.append({
                "회차": i+1,
                "납입금": int(monthly_payment),
                "원금": int(principal),
                "이자": int(interest),
                "남은 대출금": int(max(0, balance))
            })
        st.dataframe(pd.DataFrame(schedule), hide_index=True, use_container_width=True)

# ===========================================================
# TAB 5: 금리인하요구권 진단기
# ===========================================================
with tab5:
    st.header("🩺 금리인하요구권 진단기")
    st.markdown("이미 대출이 있다면, 이자를 깎아달라고 요구할 수 있습니다! (**법적 권리**)")
    
    col_chk1, col_chk2 = st.columns(2)
    with col_chk1:
        check1 = st.checkbox("회사에서 승진했다 (직위 상승)")
        check2 = st.checkbox("연봉이 올랐다")
        check3 = st.checkbox("전문자격증을 땄다")
    with col_chk2:
        check4 = st.checkbox("신용점수가 올랐다")
        check5 = st.checkbox("자산이 크게 늘었다")
        check6 = st.checkbox("은행의 우수고객으로 선정됐다")

    checked_count = sum([check1, check2, check3, check4, check5, check6])
    
    st.divider()
    if checked_count >= 1:
        st.balloons()
        st.markdown(f"""
        <div class="result-box result-safe">
            <div class="big-score" style="color:#10B981;">가능성 높음! 🎉</div>
            <p>총 <b>{checked_count}가지</b> 사유가 확인되었습니다. 은행에 신청해보세요!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("아직 해당 사항이 없네요. 조금 더 힘내봐요! 💪")