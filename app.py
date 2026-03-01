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
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
    }
    .issue-box {
        background: #2d1b1b;
        border-left: 4px solid #ff4444;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 6px 0;
        color: #ffffff;
    }
    .suggest-box {
        background: #1b2d1b;
        border-left: 4px solid #44ff44;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 6px 0;
        color: #ffffff;
    }
    .tip-box {
        background: #1b1b2d;
        border-left: 4px solid #4488ff;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 6px 0;
        color: #ffffff;
    }
    .compare-winner {
        background: linear-gradient(135deg, #1a2e1a 0%, #162e16 100%);
        border: 2px solid #44ff44;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .compare-loser {
        background: linear-gradient(135deg, #2e1a1a 0%, #2e1616 100%);
        border: 2px solid #ff4444;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .stProgress > div > div {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("# 🎯 Algo Hunter")
st.markdown("**노출 막는 상품명, 10초 만에 잡아냅니다.**")
st.markdown("---")

# ─────────────────────────────────────────────
# 탭
# ─────────────────────────────────────────────
tab1, tab2 = st.tabs(["📊 단일 분석", "⚖️ A/B 비교"])


def show_result(result, product_name, target_keyword):
    """분석 결과 공통 출력 함수"""
    potential = result["potential"]
    color = result["potential_color"]
    total = result["total_score"]

    st.markdown(f"""
    <div class="score-box">
        <p style="color: #aaa; font-size: 14px; margin: 0 0 4px;">최적화 잠재력</p>
        <p class="grade-text" style="color: {color};">{potential}%</p>
        <p class="score-num">현재 점수: {total} / 100</p>
        <p style="color: #aaa; margin: 4px 0 0;">{result['potential_desc']}</p>
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
            st.markdown(
                f"<div style='text-align:center; padding-top:8px;'>"
                f"<b style='font-size:20px'>{s['score']}</b>"
                f"<span style='color:#888'>/{s['max']}</span></div>",
                unsafe_allow_html=True
            )
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
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**현재**")
                st.info(product_name)
                st.caption(f"{len(product_name)}자")
            with c2:
                st.markdown("**개선안**")
                st.success(optimized)
                st.caption(f"{len(optimized)}자")
            st.markdown("")

    # 연관 키워드
    if result.get("golden_keywords"):
        st.markdown("### 🏅 연관 키워드 추천")
        st.caption("네이버 쇼핑 자동완성 기반 — 클릭하면 경쟁 강도 직접 확인!")
        for gk in result["golden_keywords"]:
            st.markdown(
                f'<div class="suggest-box">🔍 <b>{gk["keyword"]}</b>'
                f'&nbsp;&nbsp;<a href="{gk["naver_url"]}" target="_blank" style="color:#4af; font-size:12px;">네이버에서 확인 →</a></div>',
                unsafe_allow_html=True
            )
        st.markdown("")
    elif target_keyword:
        naver_url = f"https://search.shopping.naver.com/search/all?query={target_keyword}"
        st.markdown("### 📊 경쟁 강도 확인")
        st.markdown(
            f'<div class="tip-box">🔍 <a href="{naver_url}" target="_blank" style="color:#4af;">'
            f'"{target_keyword}" 네이버 쇼핑에서 직접 확인하기 →</a></div>',
            unsafe_allow_html=True
        )
        st.markdown("")

    # 경쟁 전략 팁
    st.markdown("### 🏆 카테고리 경쟁 전략")
    for tip in result["competitor_strategy"]:
        st.markdown(f'<div class="tip-box">💡 {tip}</div>', unsafe_allow_html=True)

    st.markdown("---")

    if total < 85:
        st.markdown("### 🔄 개선 후 다시 분석해보세요!")
        st.caption("수정한 상품명을 위에서 다시 분석하면 점수 변화를 바로 확인할 수 있습니다.")


# ─────────────────────────────────────────────
# TAB 1: 단일 분석
# ─────────────────────────────────────────────
with tab1:
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

    if submitted:
        if not product_name.strip():
            st.error("상품명을 입력해주세요.")
        else:
            with st.spinner("알고리즘 분석 중..."):
                result = analyze_product_name(product_name.strip(), target_keyword.strip(), category)
            show_result(result, product_name.strip(), target_keyword.strip())


# ─────────────────────────────────────────────
# TAB 2: A/B 비교
# ─────────────────────────────────────────────
with tab2:
    st.markdown("두 상품명을 나란히 비교해보세요. 어느 쪽이 알고리즘에 더 유리한지 바로 확인!")
    
    with st.form("compare_form"):
        cat_ab = st.selectbox(
            "📂 카테고리",
            ["기타", "패션/의류", "식품/음료", "생활용품", "디지털/가전"],
            key="cat_ab"
        )
        kw_ab = st.text_input(
            "🔍 타겟 키워드 (선택)",
            placeholder="예: 루즈핏 티셔츠",
            key="kw_ab"
        )
        col_a, col_b = st.columns(2)
        with col_a:
            name_a = st.text_input("🅰️ 상품명 A", placeholder="현재 상품명", key="name_a")
        with col_b:
            name_b = st.text_input("🅱️ 상품명 B", placeholder="수정 후 상품명", key="name_b")
        
        compare_submitted = st.form_submit_button("⚡ 비교 시작", use_container_width=True, type="primary")

    if compare_submitted:
        if not name_a.strip() or not name_b.strip():
            st.error("두 상품명을 모두 입력해주세요.")
        else:
            with st.spinner("비교 분석 중..."):
                res_a = analyze_product_name(name_a.strip(), kw_ab.strip(), cat_ab)
                res_b = analyze_product_name(name_b.strip(), kw_ab.strip(), cat_ab)
            
            score_a = res_a["total_score"]
            score_b = res_b["total_score"]
            pot_a = res_a["potential"]
            pot_b = res_b["potential"]
            col_a2, col_b2 = st.columns(2)
            
            if score_a >= score_b:
                winner_a, winner_b = "compare-winner", "compare-loser"
                verdict = "🅰️ A가 더 유리!"
                diff = score_a - score_b
            else:
                winner_a, winner_b = "compare-loser", "compare-winner"
                verdict = "🅱️ B가 더 유리!"
                diff = score_b - score_a

            # 결과 요약
            st.markdown(f"## {verdict}  (점수 차이: {diff}점)")
            
            with col_a2:
                st.markdown(
                    f'<div class="{winner_a}">'
                    f'<p style="font-size:13px; color:#aaa; margin:0;">🅰️ {name_a.strip()[:30]}{"..." if len(name_a)>30 else ""}</p>'
                    f'<p style="font-size:48px; font-weight:900; color:{res_a["potential_color"]}; margin:4px 0;">{pot_a}%</p>'
                    f'<p style="color:#fff; font-size:18px; margin:0;">점수 {score_a}/100</p>'
                    f'<p style="color:#aaa; font-size:12px; margin:4px 0 0;">{res_a["status_label"]}</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with col_b2:
                st.markdown(
                    f'<div class="{winner_b}">'
                    f'<p style="font-size:13px; color:#aaa; margin:0;">🅱️ {name_b.strip()[:30]}{"..." if len(name_b)>30 else ""}</p>'
                    f'<p style="font-size:48px; font-weight:900; color:{res_b["potential_color"]}; margin:4px 0;">{pot_b}%</p>'
                    f'<p style="color:#fff; font-size:18px; margin:0;">점수 {score_b}/100</p>'
                    f'<p style="color:#aaa; font-size:12px; margin:4px 0 0;">{res_b["status_label"]}</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.markdown("---")
            
            # 세부 항목 비교 테이블
            st.markdown("### 📊 항목별 비교")
            score_labels = {
                "length": "📏 길이",
                "banned_words": "🚫 금칙어",
                "special_chars": "✏️ 특수문자",
                "keyword": "🔍 키워드",
                "readability": "📖 가독성"
            }
            for key, label in score_labels.items():
                sa = res_a["scores"][key]["score"]
                sb = res_b["scores"][key]["score"]
                mx = res_a["scores"][key]["max"]
                ca, cb = st.columns([1, 1])
                with ca:
                    icon = "✅" if sa >= sb else "❌"
                    st.markdown(f"{icon} **A** {label}: **{sa}/{mx}**")
                with cb:
                    icon = "✅" if sb >= sa else "❌"
                    st.markdown(f"{icon} **B** {label}: **{sb}/{mx}**")
            
            st.markdown("---")
            
            # 각각 개선 제안
            st.markdown("### 💡 각 상품명 개선 포인트")
            exp_a = st.expander("🅰️ A 개선 제안")
            with exp_a:
                if res_a["issues"]:
                    for issue in res_a["issues"]:
                        st.markdown(f'<div class="issue-box">❌ {issue}</div>', unsafe_allow_html=True)
                if res_a["suggestions"]:
                    for sug in res_a["suggestions"]:
                        st.markdown(f'<div class="suggest-box">✅ {sug}</div>', unsafe_allow_html=True)
                if not res_a["issues"] and not res_a["suggestions"]:
                    st.success("개선 사항 없음!")
            
            exp_b = st.expander("🅱️ B 개선 제안")
            with exp_b:
                if res_b["issues"]:
                    for issue in res_b["issues"]:
                        st.markdown(f'<div class="issue-box">❌ {issue}</div>', unsafe_allow_html=True)
                if res_b["suggestions"]:
                    for sug in res_b["suggestions"]:
                        st.markdown(f'<div class="suggest-box">✅ {sug}</div>', unsafe_allow_html=True)
                if not res_b["issues"] and not res_b["suggestions"]:
                    st.success("개선 사항 없음!")


# 하단 정보
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#666; font-size:12px;'>"
    "Algo Hunter MVP v0.2 · 스마트스토어 셀러를 위한 무료 알고리즘 분석 도구"
    "</div>",
    unsafe_allow_html=True
)
