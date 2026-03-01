"""
Algo Hunter 🎯
스마트스토어 알고리즘 최적화 분석기
"""

import streamlit as st
import os
from analyzer import analyze_product_name, generate_optimized_name, get_competitor_analysis

# 네이버 API 키 (환경변수 우선, 없으면 sidebar 입력)
NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET", "")

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

# 사이드바 - API 키 + 히스토리
with st.sidebar:
    st.markdown("### ⚙️ 설정")
    naver_id = st.text_input("네이버 Client ID", value=NAVER_CLIENT_ID, type="password",
                              help="네이버 개발자 API 키 입력 시 실제 경쟁 상품 분석 활성화")
    naver_secret = st.text_input("네이버 Client Secret", value=NAVER_CLIENT_SECRET, type="password")
    
    if naver_id and naver_secret:
        st.success("✅ 경쟁 분석 활성화됨")
    else:
        st.info("💡 네이버 API 키 입력 시 실제 경쟁 상품 비교 가능\n[발급하기](https://developers.naver.com/apps/#/register)")

    st.markdown("---")
    st.markdown("### 📋 분석 히스토리")
    if "history" not in st.session_state:
        st.session_state.history = []
    if st.session_state.history:
        for h in reversed(st.session_state.history[-5:]):
            color = h["color"]
            st.markdown(
                f'<div style="background:#1a1a2e; border-left:3px solid {color}; '
                f'padding:6px 10px; margin:4px 0; border-radius:4px; font-size:12px;">'
                f'<b style="color:{color}">{h["potential"]}%</b> '
                f'<span style="color:#ccc">{h["name"][:20]}...</span></div>',
                unsafe_allow_html=True
            )
        if st.button("히스토리 지우기"):
            st.session_state.history = []
    else:
        st.caption("분석하면 여기에 기록됩니다")

# 헤더
st.markdown("# 🎯 Algo Hunter")
st.markdown("**스마트스토어 전용 상품명 최적화 체크리스트**")
st.markdown("<small style='color:#888'>네이버 쇼핑 로직 기반 · 실제 경쟁 상품 비교 · 무료 · 로그인 없음</small>", unsafe_allow_html=True)
st.markdown("---")

# ─────────────────────────────────────────────
# 탭
# ─────────────────────────────────────────────
tab1, tab2 = st.tabs(["📊 단일 분석", "⚖️ A/B 비교"])


def make_share_text(result, product_name):
    """공유용 텍스트 생성"""
    potential = result["potential"]
    total = result["total_score"]
    label = result["status_label"]
    issues_text = "\n".join([f"  ❌ {i}" for i in result["issues"]]) if result["issues"] else "  ✅ 없음"
    suggest_text = "\n".join([f"  💡 {s}" for s in result["suggestions"][:3]]) if result["suggestions"] else "  ✅ 최적화 완료"
    
    return f"""🎯 Algo Hunter 상품명 분석 결과

📦 상품명: {product_name[:40]}{"..." if len(product_name)>40 else ""}
📊 최적화 잠재력: {potential}% ({label})
🏅 현재 점수: {total}/100

🚨 발견된 문제:
{issues_text}

💡 개선 제안:
{suggest_text}

👉 내 상품명 무료 분석: https://algo-hunter-production.up.railway.app
(로그인 없이 바로 사용!)"""


def show_result(result, product_name, target_keyword, naver_id="", naver_secret=""):
    """분석 결과 공통 출력 함수"""
    potential = result["potential"]
    color = result["potential_color"]
    total = result["total_score"]

    # 히스토리 저장
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.append({
        "name": product_name,
        "potential": potential,
        "score": total,
        "color": color
    })

    st.markdown(f"""
    <div class="score-box">
        <p style="color: #aaa; font-size: 14px; margin: 0 0 4px;">최적화 잠재력</p>
        <p class="grade-text" style="color: {color};">{potential}%</p>
        <p class="score-num">현재 점수: {total} / 100</p>
        <p style="color: #aaa; margin: 4px 0 0;">{result['potential_desc']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 공유 버튼
    share_text = make_share_text(result, product_name)
    with st.expander("📤 결과 공유하기 (카페/단톡방용)", expanded=False):
        st.markdown("**아래 텍스트를 복사해서 카페나 단톡방에 공유하세요!**")
        st.text_area("공유 텍스트", share_text, height=200, key=f"share_{hash(product_name)}")
        st.caption("💡 텍스트 선택 → Ctrl+A → Ctrl+C 로 전체 복사")
    
    # 🔥 경쟁 상품 실제 비교 (네이버 API 있을 때)
    if target_keyword and naver_id and naver_secret:
        with st.spinner("실제 경쟁 상품명 분석 중..."):
            comp = get_competitor_analysis(target_keyword, naver_id, naver_secret)
        if comp["available"]:
            d = comp["data"]
            st.markdown("### 🏆 실제 경쟁 상품 비교 (네이버 쇼핑 상위 노출)")
            st.caption(f"'{target_keyword}' 검색 상위 {d['count']}개 상품명 실제 분석")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                my_len = len(product_name)
                avg_len = d["avg_length"]
                diff = my_len - avg_len
                icon = "✅" if abs(diff) <= 5 else ("⬆️" if diff > 0 else "⬇️")
                st.metric("내 상품명 길이", f"{my_len}자", f"{diff:+.0f} vs 경쟁사 평균({avg_len}자)")
            with c2:
                st.metric("경쟁사 길이 범위", f"{d['min_length']}~{d['max_length']}자", f"평균 {avg_len}자")
            with c3:
                st.metric("경쟁사 특수문자 사용", f"{d['special_char_rate']}%", "낮을수록 좋음")
            
            if d["common_keywords"]:
                st.markdown("**경쟁 상품 공통 키워드:**")
                kw_html = " ".join([
                    f'<span style="background:#1b2d1b; border:1px solid #44ff44; border-radius:12px; '
                    f'padding:2px 10px; margin:2px; display:inline-block; color:#44ff44; font-size:13px;">{kw}</span>'
                    for kw in d["common_keywords"]
                ])
                st.markdown(kw_html, unsafe_allow_html=True)
                missing = [kw for kw in d["common_keywords"] if kw not in product_name]
                if missing:
                    st.warning(f"⚠️ 경쟁 상품에 많은 키워드가 내 상품명에 없음: **{', '.join(missing)}**")
            
            with st.expander("🔍 경쟁 상품명 전체 보기"):
                for i, t in enumerate(d["titles"], 1):
                    st.markdown(f"`{i}.` {t} ({len(t)}자)")

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
            show_result(result, product_name.strip(), target_keyword.strip(), naver_id, naver_secret)


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
            
            # A/B 비교 공유 텍스트
            winner_name = name_a.strip() if score_a >= score_b else name_b.strip()
            winner_score = max(score_a, score_b)
            loser_score = min(score_a, score_b)
            ab_share = f"""🎯 Algo Hunter A/B 상품명 비교 결과

🅰️ {name_a.strip()[:35]}
   → 점수: {score_a}/100 | 잠재력: {res_a['potential']}%

🅱️ {name_b.strip()[:35]}
   → 점수: {score_b}/100 | 잠재력: {res_b['potential']}%

✅ 승자: {'🅰️ A' if score_a >= score_b else '🅱️ B'} (차이: {abs(score_a-score_b)}점)

👉 내 상품명 무료 분석: https://algo-hunter-production.up.railway.app"""
            with st.expander("📤 비교 결과 공유하기", expanded=False):
                st.text_area("공유 텍스트", ab_share, height=180, key="ab_share")


# 하단 정보
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#666; font-size:12px;'>"
    "Algo Hunter v0.3 · 스마트스토어 전용 상품명 최적화 체크리스트 · 실제 경쟁 상품 비교"
    "</div>",
    unsafe_allow_html=True
)
