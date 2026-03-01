"""
Algo Hunter - 스마트스토어 알고리즘 최적화 분석기
분석 로직 모듈
"""

import re

# 네이버 쇼핑 금칙어 (실제 네이버 정책 기반)
BANNED_WORDS = [
    "최저가", "무료배송", "1+1", "당일발송", "특가", "초특가", "땡처리",
    "재고정리", "덤핑", "세일", "할인", "싸다", "저렴", "공장직판",
    "도매", "정품보장", "100%정품", "A급", "B급"
]

# 네이버 쇼핑 알고리즘이 선호하는 패턴
GOOD_PATTERNS = [
    "브랜드명이 앞에 위치",
    "핵심 키워드 앞 15자 이내",
    "공백으로 의미단위 구분",
    "숫자+단위 조합 (500ml, 2kg 등)",
]

def analyze_product_name(product_name: str, target_keyword: str = "", category: str = "") -> dict:
    """상품명 분석 메인 함수"""
    
    result = {
        "total_score": 0,
        "scores": {},
        "issues": [],
        "suggestions": [],
        "keyword_analysis": {},
        "competitor_strategy": []
    }
    
    # 1. 길이 점수 (20점)
    length = len(product_name)
    if 25 <= length <= 35:
        length_score = 20
        length_msg = f"✅ 최적 길이 ({length}자)"
    elif 20 <= length < 25 or 35 < length <= 40:
        length_score = 14
        length_msg = f"⚠️ 길이 개선 필요 ({length}자, 권장: 25-35자)"
        if length < 25:
            result["suggestions"].append(f"상품명이 짧습니다 ({length}자). 연관 키워드를 추가해 25-35자로 늘리세요.")
        else:
            result["suggestions"].append(f"상품명이 깁니다 ({length}자). 불필요한 단어를 제거해 35자 이하로 줄이세요.")
    elif length < 20:
        length_score = 7
        length_msg = f"❌ 너무 짧음 ({length}자)"
        result["issues"].append(f"상품명이 너무 짧습니다 ({length}자). 최소 20자 이상 권장.")
        result["suggestions"].append("상품 특징(색상, 사이즈, 소재 등)을 추가해 키워드를 늘리세요.")
    else:
        length_score = 5
        length_msg = f"❌ 너무 김 ({length}자)"
        result["issues"].append(f"상품명이 너무 깁니다 ({length}자). 40자 초과 시 검색 노출 불이익.")
        result["suggestions"].append("핵심 키워드만 남기고 나머지는 상세페이지로 이동하세요.")
    
    result["scores"]["length"] = {"score": length_score, "max": 20, "message": length_msg}
    
    # 2. 금칙어 점수 (20점)
    found_banned = [w for w in BANNED_WORDS if w in product_name]
    if not found_banned:
        banned_score = 20
        banned_msg = "✅ 금칙어 없음"
    else:
        banned_score = max(0, 20 - len(found_banned) * 7)
        banned_msg = f"❌ 금칙어 발견: {', '.join(found_banned)}"
        result["issues"].append(f"금칙어 포함: '{', '.join(found_banned)}' → 검색 노출 제한 위험")
        result["suggestions"].append(f"금칙어를 제거하세요: {', '.join(found_banned)}")
    
    result["scores"]["banned_words"] = {"score": banned_score, "max": 20, "message": banned_msg}
    
    # 3. 특수문자 점수 (15점)
    special_chars = re.findall(r'[!@#$%^&*()_+=\[\]{};\'\":,.<>?/\\|`~]', product_name)
    excessive_special = len(special_chars)
    
    if excessive_special == 0:
        special_score = 15
        special_msg = "✅ 특수문자 없음"
    elif excessive_special <= 2:
        special_score = 10
        special_msg = f"⚠️ 특수문자 {excessive_special}개"
        result["suggestions"].append("특수문자 사용을 최소화하세요 (1-2개 이하 권장).")
    else:
        special_score = 3
        special_msg = f"❌ 특수문자 과다 ({excessive_special}개)"
        result["issues"].append(f"특수문자가 너무 많습니다 ({excessive_special}개). 네이버 알고리즘이 스팸으로 분류할 수 있음.")
        result["suggestions"].append("특수문자를 모두 제거하거나 최대 1개만 남기세요.")
    
    result["scores"]["special_chars"] = {"score": special_score, "max": 15, "message": special_msg}
    
    # 4. 키워드 배치 점수 (25점)
    keyword_score = 0
    keyword_msgs = []
    
    if target_keyword:
        # 부분 포함 체크: 키워드를 단어로 쪼개서 개별 포함 여부 확인
        kw_words = target_keyword.split()
        matched_words = [w for w in kw_words if w in product_name]
        full_match = target_keyword in product_name
        partial_match = len(matched_words) == len(kw_words) and not full_match
        
        if full_match:
            keyword_score += 15
            keyword_msgs.append(f"✅ 타겟 키워드 '{target_keyword}' 완전 포함")
            idx = product_name.find(target_keyword)
            if idx <= 15:
                keyword_score += 10
                keyword_msgs.append(f"✅ 앞쪽 배치 완벽 (위치: {idx+1}번째 글자)")
            else:
                keyword_score += 5
                keyword_msgs.append(f"⚠️ 키워드 위치 뒤쪽 ({idx+1}번째 글자) → 앞으로 이동 권장")
                result["suggestions"].append(f"'{target_keyword}'를 상품명 앞쪽(15자 이내)으로 이동하면 노출이 올라갑니다.")
        elif partial_match:
            # 단어는 다 있는데 연속 배치가 안 됨
            keyword_score += 10
            keyword_msgs.append(f"⚠️ 키워드 단어 분산 포함: {', '.join(matched_words)}")
            # 첫 단어 위치 확인
            first_idx = product_name.find(kw_words[0])
            if first_idx <= 15:
                keyword_score += 5
                keyword_msgs.append(f"✅ 첫 키워드 앞쪽 배치")
            else:
                keyword_score += 1
                keyword_msgs.append(f"⚠️ 첫 키워드도 뒤쪽에 위치")
            result["suggestions"].append(f"'{target_keyword}' 단어들이 분산되어 있습니다. 붙여서 앞쪽에 배치하면 점수가 올라갑니다.")
        elif len(matched_words) > 0:
            keyword_score += 5
            keyword_msgs.append(f"⚠️ 일부 키워드만 포함: {', '.join(matched_words)} (누락: {', '.join([w for w in kw_words if w not in product_name])})")
            result["suggestions"].append(f"누락된 키워드 '{' '.join([w for w in kw_words if w not in product_name])}'를 상품명에 추가하세요.")
        else:
            keyword_score += 0
            keyword_msgs.append(f"❌ 타겟 키워드 '{target_keyword}' 미포함")
            result["issues"].append(f"타겟 키워드 '{target_keyword}'가 상품명에 전혀 없습니다.")
            result["suggestions"].append(f"'{target_keyword}'를 상품명 맨 앞에 추가하세요.")
    else:
        keyword_score = 15  # 키워드 미입력시 기본점수
        keyword_msgs.append("ℹ️ 타겟 키워드 미입력 (입력하면 더 정확한 분석)")
    
    result["scores"]["keyword"] = {"score": keyword_score, "max": 25, "message": " | ".join(keyword_msgs)}
    
    # 5. 가독성 점수 (20점)
    readability_score = 20
    readability_msgs = []
    
    # 중복 단어 체크
    words = product_name.split()
    duplicates = [w for w in set(words) if words.count(w) > 1 and len(w) > 1]
    if duplicates:
        readability_score -= 8
        readability_msgs.append(f"❌ 중복 단어: {', '.join(duplicates)}")
        result["issues"].append(f"단어 중복: '{', '.join(duplicates)}' → 검색 품질 점수 하락")
        result["suggestions"].append(f"중복 단어를 제거하고 다른 연관 키워드로 교체하세요.")
    
    # 연속 공백 체크
    if "  " in product_name:
        readability_score -= 5
        readability_msgs.append("❌ 연속 공백 발견")
        result["suggestions"].append("연속 공백을 제거하세요.")
    
    # 숫자+단위 패턴 (긍정)
    if re.search(r'\d+(ml|L|kg|g|cm|mm|m|개|세트|팩|박스)', product_name):
        readability_msgs.append("✅ 규격 정보 포함 (알고리즘 선호)")
    
    if not readability_msgs:
        readability_msgs.append("✅ 가독성 양호")
    
    result["scores"]["readability"] = {"score": readability_score, "max": 20, "message": " | ".join(readability_msgs)}
    
    # 총점 계산
    total = sum(v["score"] for v in result["scores"].values())
    result["total_score"] = total
    
    # 등급
    if total >= 85:
        result["grade"] = "S"
        result["grade_desc"] = "최상위 노출 최적화 상태"
        result["grade_color"] = "#00C851"
    elif total >= 70:
        result["grade"] = "A"
        result["grade_desc"] = "양호 — 소폭 개선으로 상위권 진입 가능"
        result["grade_color"] = "#33b5e5"
    elif total >= 55:
        result["grade"] = "B"
        result["grade_desc"] = "보통 — 개선 필요, 경쟁에서 밀릴 수 있음"
        result["grade_color"] = "#ffbb33"
    elif total >= 40:
        result["grade"] = "C"
        result["grade_desc"] = "미흡 — 즉시 수정 권장"
        result["grade_color"] = "#ff8800"
    else:
        result["grade"] = "D"
        result["grade_desc"] = "위험 — 노출 심각하게 낮을 가능성"
        result["grade_color"] = "#CC0000"
    
    # 경쟁자 전략 팁 (카테고리별)
    result["competitor_strategy"] = get_category_tips(category)
    
    return result


def generate_optimized_name(product_name: str, target_keyword: str, suggestions: list) -> str:
    """최적화된 상품명 예시 생성"""
    if not target_keyword:
        return ""
    
    # 간단한 재구성 로직
    # 타겟 키워드를 맨 앞으로
    name = product_name
    if target_keyword in name:
        name = name.replace(target_keyword, "").strip()
        name = target_keyword + " " + name
    else:
        name = target_keyword + " " + name
    
    # 40자 초과시 자르기
    if len(name) > 40:
        name = name[:40]
    
    return name.strip()


def get_category_tips(category: str) -> list:
    """카테고리별 경쟁 전략 팁"""
    tips = {
        "패션/의류": [
            "소재+핏+색상 조합 필수 (예: '면 루즈핏 화이트 티셔츠')",
            "시즌 키워드 앞에 배치 (봄여름/가을겨울)",
            "사이즈 범위 명시하면 롱테일 검색 유입↑"
        ],
        "식품/음료": [
            "용량+수량 정확히 명시 (500g 2팩)",
            "원산지 표기 시 신뢰도↑",
            "조리방법/섭취방법 키워드 추가 효과적"
        ],
        "생활용품": [
            "사용 공간 명시 (주방/욕실/거실)",
            "세트 구성 명확히 (3종세트, 5개입)",
            "브랜드명보다 기능 키워드 먼저"
        ],
        "디지털/가전": [
            "모델번호 포함 시 정확 검색 유입↑",
            "호환 기기 명시 (갤럭시/아이폰)",
            "세대/버전 정보 필수"
        ],
        "기타": [
            "핵심 기능어를 상품명 가장 앞에 배치",
            "타겟 고객층 키워드 추가 (남성/여성/아동/반려동물)",
            "상품 특장점 1개만 압축해서 포함"
        ]
    }
    return tips.get(category, tips["기타"])
