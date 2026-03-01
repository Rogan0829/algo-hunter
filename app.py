"""
Algo Hunter 🎯
스마트스토어 알고리즘 최적화 분석기
"""

import streamlit as st
from analyzer import analyze_product_name, generate_optimized_name

# 페이지 설정
st.set_page_config(
    page_title="Algo Hunter - 스마트스토어 알고리즘 분석기",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS 커스텀
st.markdown("""
<style>
    .main { padding-top: 1rem; }
    .score-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin: 16px 0;
    }
    .grade-text {
        font-size: 72px;
        font-weight: 900;
        margin: 0;
        line-height: 1;
    }
    .score-num {
        font-size: 36px;
        font-weight: 700;
        color: #ffffff;
    }
    .issue-box {
        background: #2d1b1b;
        border-left: 4px solid #ff4444;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 6px 0;
    }
    .suggest-box {
        background: #1b2d1b;
        border-left: 4px solid #44ff44;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 6px 0;
    }
    .tip-box {
        background: #1b1b2d;
        border-left: 4px solid #4488ff;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 6px 0;
    }
    .stProgress > div > div {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("# 🎯 Algo Hunter")
st.markdown("**스마트스토어 상품명 알고리즘 최적화 분석기**")
st.markdown("---")

# 입력 폼
with st.form("analysis_form"):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        product_name = st.text_input(
            "📦 상품명 입력",
            placeholder="예: 국산 면 루즈핏 반팔 티셔츠 여성 여름 흰색 S~2XL",
            help="분석할 스마트스토어 상품명을 입력하세요"
        )
    
    with col2:
        category = st.selectbox(
            "📂 카테고리",
            ["기타", "패션/의류", "식품/음료", "생활용품", "디지털/가전"]
        )
    
    target_keyword = st.text_input(
        "🔍 타겟 키워드 (선택)",
        placeholder="예: 루즈핏 티셔츠",
        help="노출 목표로 하는 핵심 키워드를 입력하면 더 정확한 분석이 가능합니다"
    )
    
    submitted = st.form_submit_button("🚀 분석 시작", use_container_width=True, type="primary")

# 분석 실행
if submitted:
    if not product_name.strip():
        st.error("상품명을 입력해주세요.")
    else:
        with st.spinner("알고리즘 분석 중..."):
            result = analyze_product_name(product_name.strip(), target_keyword.strip(), category)
        
        # 총점 표시
        grade = result["grade"]
        color = result["grade_color"]
        total = result["total_score"]
        
        st.markdown(f"""
        <div class="score-box">
            <p class="grade-text" style="color: {color};">{grade}</p>
            <p class="score-num">{total} / 100점</p>
            <p style="color: #aaa; margin: 4px 0 0;">{result['grade_desc']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 세부 점수
        st.markdown("### 📊 세부 분석")
        
        score_labels = {
            "length": "📏 상품명 길이",
            "banned_words": "🚫 금칙어 검사",
            "special_chars": "✏️ 특수문자",
            "keyword": "🔍 키워드 최적화",
            "readability": "📖 가독성"
        }
        
        for key, label in score_labels.items():
            s = result["scores"][key]
            pct = s["score"] / s["max"]
            col_l, col_r = st.columns([3, 1])
            with col_l:
                st.markdown(f"**{label}**")
                st.progress(pct)
                st.caption(s["message"])
            with col_r:
                st.markdown(f"<div style='text-align:center; padding-top:8px;'><b style='font-size:20px'>{s['score']}</b><span style='color:#888'>/{s['max']}</span></div>", unsafe_allow_html=True)
            st.markdown("")
        
        st.markdown("---")
        
        # 문제점
        if result["issues"]:
            st.markdown("### 🚨 발견된 문제점")
            for issue in result["issues"]:
                st.markdown(f'<div class="issue-box">❌ {issue}</div>', unsafe_allow_html=True)
            st.markdown("")
        
        # 개선 제안
        if result["suggestions"]:
            st.markdown("### 💡 개선 제안")
            for i, sug in enumerate(result["suggestions"], 1):
                st.markdown(f'<div class="suggest-box">✅ <b>{i}.</b> {sug}</div>', unsafe_allow_html=True)
            st.markdown("")
        
        # 최적화 상품명 예시
        if target_keyword:
            optimized = generate_optimized_name(product_name, target_keyword, result["suggestions"])
            if optimized and optimized != product_name:
                st.markdown("### ✨ 최적화 상품명 예시")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**현재**")
                    st.info(f"{product_name}")
                    st.caption(f"{len(product_name)}자")
                with col2:
                    st.markdown("**개선안**")
                    st.success(f"{optimized}")
                    st.caption(f"{len(optimized)}자")
                st.markdown("")
        
        # 경쟁 전략 팁
        st.markdown("### 🏆 카테고리 경쟁 전략")
        for tip in result["competitor_strategy"]:
            st.markdown(f'<div class="tip-box">💡 {tip}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 다시 분석 유도
        if total < 85:
            st.markdown("### 🔄 개선 후 다시 분석해보세요!")
            st.caption("제안사항을 반영해 상품명을 수정한 뒤 위에서 다시 분석하면 점수 변화를 확인할 수 있습니다.")

# 하단 정보
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#666; font-size:12px;'>"
    "Algo Hunter MVP v0.1 · 스마트스토어 셀러를 위한 무료 알고리즘 분석 도구"
    "</div>",
    unsafe_allow_html=True
)
