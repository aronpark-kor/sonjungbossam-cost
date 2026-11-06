import os
import re
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# 1. PAGE CONFIG & SONJEONG BOSSAM BI DESIGN SYSTEM (NON-EXCEL CARD UI)
# ==============================================================================
st.set_page_config(
    page_title="손정보쌈 | 가맹점 원가·레시피·손익 통합 진단 포털",
    page_icon="🥩",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #FAF7F2;
        color: #1A1817;
    }
    .stApp {
        background-color: #FAF7F2;
    }
    /* Top Brand Banner */
    .sj-hero {
        background: linear-gradient(135deg, #1A1817 0%, #2D241E 100%);
        color: #FAF7F2;
        padding: 24px 30px;
        border-radius: 16px;
        border-bottom: 4px solid #CB994F;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 8px 20px rgba(26,24,23,0.12);
    }
    .sj-hero-badge {
        display: inline-block;
        background-color: #CB994F;
        color: #1A1817;
        font-weight: 800;
        font-size: 13px;
        padding: 4px 12px;
        border-radius: 20px;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
    }
    .sj-hero-title {
        font-size: 26px;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
    }
    .sj-hero-sub {
        font-size: 14px;
        color: #D8CFC4;
        margin-top: 4px;
    }
    /* Custom Card UI */
    .sj-card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 20px 22px;
        border: 1px solid #E6DEC8;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 16px;
    }
    .sj-card-gold {
        background: #FFFDF9;
        border-radius: 14px;
        padding: 20px 22px;
        border: 2px solid #CB994F;
        box-shadow: 0 4px 14px rgba(203,153,79,0.12);
        margin-bottom: 16px;
    }
    .sj-card-alert {
        background: #FFF8F7;
        border-radius: 14px;
        padding: 20px 22px;
        border-left: 6px solid #B8332A;
        border-top: 1px solid #F1D2CF;
        border-right: 1px solid #F1D2CF;
        border-bottom: 1px solid #F1D2CF;
        margin-bottom: 16px;
    }
    .sj-card-good {
        background: #F6FBF7;
        border-radius: 14px;
        padding: 20px 22px;
        border-left: 6px solid #2E6F40;
        border-top: 1px solid #CBE5D1;
        border-right: 1px solid #CBE5D1;
        border-bottom: 1px solid #CBE5D1;
        margin-bottom: 16px;
    }
    /* Metric Box */
    .sj-kpi {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 16px 18px;
        border: 1px solid #E6DEC8;
        border-top: 4px solid #CB994F;
        text-align: left;
    }
    .sj-kpi-label {
        font-size: 13px;
        color: #6E655F;
        font-weight: 600;
    }
    .sj-kpi-val {
        font-size: 24px;
        font-weight: 800;
        color: #1A1817;
        margin-top: 4px;
    }
    .sj-kpi-sub {
        font-size: 12px;
        font-weight: 600;
        margin-top: 4px;
    }
    /* Progress Bar for Ingredient Cost Share */
    .sj-prog-bg {
        background-color: #EFECE6;
        border-radius: 8px;
        height: 10px;
        width: 100%;
        overflow: hidden;
        margin-top: 6px;
    }
    .sj-prog-fill {
        background: linear-gradient(90deg, #CB994F 0%, #8C1D18 100%);
        height: 100%;
        border-radius: 8px;
    }
    /* Step Timeline Badge */
    .sj-step {
        display: inline-block;
        background: #1A1817;
        color: #CB994F;
        font-weight: 700;
        font-size: 12px;
        padding: 3px 10px;
        border-radius: 6px;
        margin-right: 8px;
    }
    .sj-tag {
        display: inline-block;
        background: #F4EFE6;
        color: #5C4938;
        font-weight: 600;
        font-size: 12px;
        padding: 3px 9px;
        border-radius: 6px;
        margin-right: 6px;
        border: 1px solid #E2D9C8;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# MENU IMAGE STORAGE (메뉴별 대표사진 1장)
# ==============================================================================
MENU_IMAGE_DIR = Path("menu_images")
MENU_IMAGE_DIR.mkdir(exist_ok=True)

def _safe_menu_key(menu_name: str) -> str:
    """메뉴명을 파일명으로 안전하게 변환합니다."""
    cleaned = re.sub(r'[^0-9A-Za-z가-힣_-]+', '_', str(menu_name)).strip('_')
    return cleaned[:80] or 'menu'

def get_menu_image_path(menu_name: str):
    key = _safe_menu_key(menu_name)
    for ext in ('.png', '.jpg', '.jpeg', '.webp'):
        fp = MENU_IMAGE_DIR / f"{key}{ext}"
        if fp.exists():
            return fp
    return None

def save_menu_image(menu_name: str, uploaded_file):
    """메뉴당 대표사진 1장만 유지합니다. 새 사진 업로드 시 기존 사진을 교체합니다."""
    key = _safe_menu_key(menu_name)
    for old in MENU_IMAGE_DIR.glob(f"{key}.*"):
        try:
            old.unlink()
        except OSError:
            pass
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix not in ('.png', '.jpg', '.jpeg', '.webp'):
        suffix = '.jpg'
    out = MENU_IMAGE_DIR / f"{key}{suffix}"
    out.write_bytes(uploaded_file.getbuffer())
    return out

# ==============================================================================
# 2. EMBEDDED 28-PAGE SUPPLEMENTARY MANUAL DATABASE (보완매뉴얼 26.06.15 최신화)
# ==============================================================================
MANUAL_DB = {
    "가브리보쌈(준비) & 제공중량": {
        "category": "보쌈/핵심전처리",
        "updated": "25.10.28 수정",
        "summary": "가브리살 해동·핏물제거·삶기(40분)·뜸들이기(20분) 및 점심/저녁 정량 기준",
        "specs": [
            "점심 보쌈정식(일반): 120g / 보쌈정식(특): 170g",
            "한우사골칼국수 고기 토핑: 2~3점 (큰 고기 2점 / 작은 고기 3점)",
            "저녁 가브리보쌈(小): 300g / 가브리보쌈(中): 400g / 보쌈추가(고기만): 200g",
            "배합비 ① 가브리살 10kg 기준: 물 23kg + 보쌈분말 600g",
            "배합비 ② 가브리살 5kg 기준: 물 11.5kg + 보쌈분말 300g (전날 미리 준비)"
        ],
        "steps": [
            "1단계 (해동): 전날 가브리살 냉장 해동 진행",
            "2단계 (핏물제거): 해동된 가브리살 1시간 이상 핏물 제거 작업 필수",
            "3단계 (육수배합): 물 + 보쌈분말 정량 배합 후 끓이기",
            "4단계 (삶기 - 40분): 보쌈육수가 끓어오르면 중불로 줄이고 고기 투입 후 40분간 삶기",
            "5단계 (뜸들이기 - 20분): 불을 끄고 뚜껑을 덮은 상태로 20분간 뜸들이기",
            "6단계 (건조/보관): 고기를 꺼내 상온에서 말린 후 진공 포장하여 보관"
        ],
        "caution": "삶기 시간(중불 40분) 및 뜸들이기(20분) 미준수 시 수율 급감(정상 수율 약 22.3%~37.5%) 또는 육질 퍽퍽함 발생 주의"
    },
    "매콤알곤이볶음 & 맵기조절": {
        "category": "메인요리",
        "updated": "26.01.21 / 25.12.23 수정",
        "summary": "통돌이 자동화기계 조리 타임라인(총 4분) 및 2단계 맵기(보통/매운맛) 표준화",
        "specs": [
            "1차 투입: 고추기름 30g(3바퀴), 간마늘 30g, 자숙알 180g, 자숙고니 360g, 고추 40g/대파 40g(총 80g), 생콩나물 300g(남자손 한주먹), 사골육수 200g(샥구)",
            "2차 투입: 볶음분말 100g(중량스푼 2스푼), 참기름 2바퀴",
            "맵기 조절(보통맛): 캡사이신 넣지 않고 기존 조리방식 진행",
            "맵기 조절(매운맛): 조리 완료 후 캡사이신 액상 5~6g 투입 (소형 스푼 '5' 표기선 1스푼)"
        ],
        "steps": [
            "1단계 (초벌 볶음 - 2분): 1차 재료(고추기름~사골육수 200g) 모두 넣고 통돌이에서 2분간 조리",
            "2단계 (분말 배합 - 1분 30초): 볶음분말 100g + 참기름 2바퀴 투입 후 1분 30초 조리 (매운맛 선택 시 캡사이신 1스푼 추가)",
            "3단계 (직화 마무리 - 30초): 직화 30초 불향 입히기 후 달궈진 돌불판에 제공"
        ],
        "caution": "알곤이 찌기 전처리: 끓는 물 찜기에 해동된 알(3개)/곤이(6개)를 올리고 뚜껑 덮어 중불 50분 찐 후 상온 건조 뒤 바트 냉장보관"
    },
    "알곤이 칼국수/전골 토핑 기준": {
        "category": "점심/전골",
        "updated": "26.04.20 수정",
        "summary": "점심 1인분 및 얼큰칼국수전골(2인/3인) 알·곤이·콩나물·면 정량",
        "specs": [
            "1인분 기준: 자숙 알 50g + 자숙 곤이 120g",
            "전골 2인분 기준: 알 100g + 곤이 240g + 콩나물 120g + 칼국수면 400g(2개)",
            "전골 3인분 기준: 알 150g + 곤이 360g + 콩나물 180g + 칼국수면 600g(3개)"
        ],
        "steps": [
            "1단계: 사골육수(염도 0.85%) 정량 투입 후 얼큰다대기 풀기",
            "2단계: 인분 수에 맞춰 사전 소분된 자숙 알·곤이와 콩나물, 칼국수면 정량 세팅"
        ],
        "caution": "알·곤이 과다 투입(오버포셔닝) 시 해산물 원가율이 즉시 급등하므로 소분 박스 정량 준수"
    },
    "알곤이 치즈 파스타 (삶기 & 조리)": {
        "category": "사이드/별미",
        "updated": "26.01.04 수정",
        "summary": "파스타면 7인분 사전 삶기 소분(150g) 및 마무리 치즈 토치 조리법",
        "specs": [
            "파스타 삶기(7인분 기준): 물 4,000ml + 파스타면 500g(1봉) + 식용유 50g(1국자)",
            "1인분 조리 재료: 남은 알곤이 소스 + 소분 파스타 1봉(150g) + 한우사골육수 50ml + 치즈 50g"
        ],
        "steps": [
            "1단계 (면 삶기 - 7분): 끓는 물에 면을 넣고 바닥에 붙지 않게 저어가며 7분간 삶기",
            "2단계 (식히기/소분): 넓은 쟁반에 옮겨 식용유 50g을 버무려 식힌 뒤 위생백에 150g씩 소분 (냉장 5일 권장/최대 7일)",
            "3단계 (본조리): 팬에 남은 소스 + 파스타 150g + 사골육수 50ml를 넣고 중불에서 면이 부드러워질 때까지 볶기 (소스가 충분하면 육수 생략)",
            "4단계 (토치 마무리): 돌판에 볼륨감 있게 담고 치즈 50g을 전체적으로 덮은 뒤 토치로 갈색 그을음을 내어 제공"
        ],
        "caution": "손님 제공 시 '치즈가 잘 녹을 수 있게 잘 저은 후 드세요' 안내 멘트 필수 진행"
    },
    "꼬막 비빔밥": {
        "category": "점심/식사",
        "updated": "26.06.15 수정",
        "summary": "냉동 꼬막 100g 소분(해동 후 80g 수율) 및 정식 접시 플레이팅 표준",
        "specs": [
            "1인분 재료: 자숙꼬막 80g(냉동 소분 100g), 꼬막비빔장 50g(1국자), 미나리 20g, 계란지단 20g, 공깃밥 1ea, 김가루 5g, 참기름 10g(2바퀴), 깨 1g"
        ],
        "steps": [
            "전처리: 미나리는 잎·얇은 대 위주로 4~5cm 절단 / 꼬막은 냉동 상태에서 100g씩 위생봉투 소분 (해동 시 수율 80% ➔ 80g)",
            "1단계: 꼬막을 흐르는 찬물에 약 30초간 세척·해동 후 물기 꼭 짜기",
            "2단계: 정식 접시에 자숙꼬막 80g, 미나리 20g, 계란지단 20g을 가지런히 담기",
            "3단계: 꼬막 위에 꼬막비빔장 1국자(50g) 올리고 통깨 1g 뿌리기",
            "4단계: 면기에 밥 한 공기를 담고 참기름 2바퀴(10g) 두른 뒤 김가루 5g 올려 함께 제공"
        ],
        "caution": "해동 후 물기를 충분히 짜지 않으면 비빔장이 묽어져 맛 편차 발생"
    },
    "미나리 냉국수 & 미나리 무침": {
        "category": "점심/사이드",
        "updated": "26.04.27 수정",
        "summary": "미나리 부위별 분리 사용(줄기=냉국수 / 잎=무침)으로 식자재 로스 제로화",
        "specs": [
            "미나리 냉국수: 미나리(줄기만 0.3cm 세절) 50g + 동치미 냉면육수 2개(1개 액상 + 1개 슬러시) + 냉동소면 1개 + 통깨 1g",
            "미나리 무침: 미나리(잎 위주 4cm 절단) 40g + 초무침소스 10g + 삶은 가브리보쌈 35g(2~3조각) + 참기름 2g + 통깨 1g"
        ],
        "steps": [
            "[냉국수 1] 끓는 물에 냉동소면을 1분간 삶아 찬물 세척·물기 제거 후 면기에 담기",
            "[냉국수 2] 냉면육수 1개는 녹이고 1개는 잘게 부숴 담은 뒤, 면이 안 보이게 미나리 줄기(50g)와 통깨 올리기",
            "[미나리무침 1] 미나리 잎 40g + 초무침 10g + 참기름 2g을 볼에 넣고 가볍게 버무리기",
            "[미나리무침 2] 그릇에 담고 가브리보쌈 35g(2~3점)을 올린 후 통깨 마무리"
        ],
        "caution": "줄기(냉국수)와 잎(무침)을 명확히 분리 사용하여 미나리 폐기율을 0%로 관리"
    },
    "맵불스지": {
        "category": "메인요리",
        "updated": "25.04.08 수정",
        "summary": "삶은 계란 12분 조리법 및 자숙스지+파스타면 3분 중불 조리",
        "specs": [
            "1인분 재료: 자숙스지 230g(1팩), 맵불스지소스 250g, 정제수 250g, 파스타면 150g(1포션), 대파 10g, 삶은계란 1개, 깨 1g"
        ],
        "steps": [
            "삶은계란 준비: 계란이 2~3cm 잠기게 찬물 붓고 강불 가열 ➔ 끓기 시작하면 중불 12분 삶기 ➔ 즉시 찬물 냉각 후 탈각 (냉장 최대 5일)",
            "1단계: 웍에 맵불스지소스 250g + 정제수 250g 넣고 끓이기",
            "2단계: 끓으면 자숙스지 230g + 삶은 파스타면 150g 넣고 중불 3분간 저어가며 끓이기",
            "3단계: 파스타면을 중앙에 일자로 깔고 스지와 소스를 모두 올린 뒤 대파 10g + 2등분 계란(흰자 위로) + 통깨 마무리"
        ],
        "caution": "삶은 직후 바로 찬물에 식히지 않으면 계란 껍질 탈각 시 파손 로스 발생"
    },
    "오징어 초무침 / 문어 슬라이스 / 부추 호박전 / 오이탕탕이": {
        "category": "사이드/별미",
        "updated": "26.04.20 / 26.06.15 수정",
        "summary": "저녁 주류 안주 및 사이드 메뉴 4종 초간단 조리 규격",
        "specs": [
            "오징어 초무침: 알배추 50g + 양파슬라이스 50g + 부추 20g + 초무침소스 150g(2국자) + 참기름 2바퀴 무침 ➔ 깻잎 3장 ➔ 데친 오징어 150g(끓는물 30초) + 콩가루 토핑",
            "문어 슬라이스: 자숙문어다리 1개(해동 후 얇게 슬라이스) + 초대리밥 220g(밥 1공기+초대리 30g) + 레몬웨지 1개 + 기름장 15g + 초장 20g + 와사비 5g + 깨 1g",
            "부추 호박전: 부추전 반죽 1개 + 애호박 40g + 식용유 30g (중불에 반죽 펼치고 애호박 올린 뒤 양면 바삭하게 구워 애호박 면이 위로 가게 제공)",
            "오이탕탕이: 오이 200g(1개, 3~4등분 후 위생비닐에 넣고 접시로 힘있게 눌러 부순 뒤 찢기) + 오이소스 15g(2스푼) 버무림 + 통깨 1g"
        ],
        "steps": [
            "오이탕탕이 주의: 칼등으로 내리치면 안전사고 위험이 있으므로 반드시 위생비닐 + 접시(단단할 시 야스리로 살짝 친 후 접시) 사용"
        ],
        "caution": "사이드 메뉴는 조리 시간 3분 이내 제공으로 저녁 테이블 회전율 및 주류 추가 주문 유도"
    },
    "육수 제조 & 염도 관리 (백사골 0.85 / 해물 0.88)": {
        "category": "소분/육수/소스",
        "updated": "26.05.12 수정",
        "summary": "백사골육수(23그릇분) 및 해물탕육수(14그릇분) 표준 배합과 필수 염도",
        "specs": [
            "백사골육수 (23그릇 기준): 진한백사골육수 2kg(1봉) + 정제수 17kg ➔ 목표 염도 0.85% 필수 준수",
            "해물탕육수 (14그릇 기준): 해물농축액 1L + 정제수 20L ➔ 목표 염도 0.88% 필수 준수"
        ],
        "steps": [
            "백사골육수: 육수통 주걱 '사골 눈금선'까지 물 채우기 ➔ 사골농축액 2kg 투입 후 한소끔 끓이기 ➔ 끓기 전·후 염도계 측정하여 0.85% 맞추기",
            "해물탕육수: 육수통 주걱 '해물 눈금선'까지 물 채우기 ➔ 해물농축액 1L 혼합 ➔ 염도계로 0.88% 맞추기 (높을 시 정제수 추가)"
        ],
        "caution": "사골육수는 끓이기 전과 끓인 후 반드시 염도계로 2회 측정하여 0.85% 유지"
    },
    "다대기·간장·쌈장·김치속 대량 배합표": {
        "category": "소분/육수/소스",
        "updated": "26.01.28 / 26.02.28 수정",
        "summary": "김치속(1·5·10배합), 얼큰/해물 다대기, 간장·새우젓·쌈장 표준 배합",
        "specs": [
            "김치속 1배합(5배합/10배합): 김치속 1봉(5봉/10봉) + 새우젓 100g(500g/1kg) + 까나리액젓 100g(500g/1kg) + 다진마늘 50g(250g/500g) + 물엿 250g(1.25kg/2.5kg) + 설탕 50g(250g/500g) + 미원 10g(50g/100g)",
            "얼큰다대기: 다데기분말 3,000g(3팩) + 후추 60g + 굴소스 360g + 다진마늘 500g + 다진생강 200g 혼합 후 끓인 식용유 450g 부어 고추기름 내기 (전날 제조 후 1일 냉장숙성 필수)",
            "해물칼국수다대기: 고추지 1,000g(2팩, 잘게 다짐) + 고추지국물 400g(후추 50g 먼저 풀기) + 얼큰다데기 1,500g 혼합",
            "알곤이간장: 진간장 500g + 식초 300g + 설탕 130g + 정제수 230g",
            "전/만두간장: 진간장 600g + 식초 400g + 설탕 100g + 정제수 200g + 고춧가루 10g + 참기름 20g + 참깨 10g",
            "새우젓소스: 새우젓 1통 + 사이다 450g + 설탕 25g + 고춧가루 30g / 쌈장소스: 쌈장 말통 1통 + 사이다 1통"
        ],
        "steps": [
            "얼큰다데기 제조 시 끓인 식용유(450g)를 부을 때 거품이 올라오므로 화상 안전사고 절대 주의"
        ],
        "caution": "얼큰다데기는 당일 즉석 사용 시 깊은 맛이 나지 않으므로 반드시 하루 전 제조·숙성"
    },
    "배추/알배추 절이기 & 굴 세척·보관 위생 매뉴얼": {
        "category": "보쌈/핵심전처리",
        "updated": "26.01.21 / 25.11.13 수정",
        "summary": "소금물 재사용으로 소금 원가 절감 및 굴 3.0% 염도 소분 보관법",
        "specs": [
            "배추 절임물 기준(대형용기): 바닥에서 주걱 검정 표시선까지 물 + 천일염 1/6바트 가득 6통 ➔ 염도 평시 6.0 이상 / 겨울철 8.0",
            "1회 작업량: 배추 3통 약 3시간 절인 후 건져내고, 남은 소금물을 버리지 않고 그대로 알배추 2박스 절임에 재사용",
            "굴 세척: 찬물에 소쿠리로 9~10회 헹구며 세척 (손 체온 접촉 최소화, 껍데기 및 갯지렁이 철저 검수)",
            "굴 보관: 물 2,000ml + 천일염 70g(염도 3.0% 준수) 제조 후 [굴 200g + 소금물 200g]씩 위생백 소분 ➔ 얼음물 바트에 잠기게 보관(최대 3일, 마감 시 얼음물 교체)"
        ],
        "steps": [
            "굴 제공 시: 소분된 봉지에서 꺼내 찬물로 3~4회 가볍게 헹군 뒤 물기를 빼서 제공"
        ],
        "caution": "굴 세척 시 이물질(갯지렁이·패각) 혼입 클레임 주의 및 마감 시 얼음물 교체 필수"
    },
    "점심 기본반찬 4종 대량조리 (점심매출 100만원 기준)": {
        "category": "반찬/국",
        "updated": "26.04.30 / 25.12.17 수정",
        "summary": "어묵볶음·콩나물무침·소세지볶음·콩나물국 대량 표준 레시피",
        "specs": [
            "어묵볶음(사각어묵 2봉 기준): 물 300g, 몽고간장 100g, 양파 75g, 미림 25g, 설탕 25g, 탕대파 25g, 고운고춧가루 7g, 청양고춧가루 5g, 미원 5g 넣고 약불 졸이기",
            "콩나물무침(콩나물 2kg 기준): 물 3,000g + 콩나물 2kg 넣고 끓어오르면 뚜껑 닫고 센불 5분 ➔ 찬물 세척·탈수 후 양념(다진마늘 70g, 탕대파 80g, 꽃소금 20g, 다시다 8g, 미원 2g, 참기름) 무침",
            "소세지볶음(점심매출 100만원 기준): 통돌이에 고추기름 50g(4바퀴)+다진마늘 30g 볶기 ➔ 칼집 비엔나 2kg 넣고 칼집 벌어질 때까지 볶기 ➔ 케첩 200g, 굴소스 50g, 미원 15g, 양파 200g, 대파 50g 넣고 2분 볶음",
            "콩나물국(점심매출 100만원 기준): 물 12L + 해물농축액 500ml + 콩나물 1kg 끓이기(전 염도 0.65) ➔ 익으면 대파 200g + 다진마늘 60g(2T) 넣고 한소끔 끓이기(후 염도 0.85)"
        ],
        "steps": [
            "반찬류는 일일 예상 점심 매출액에 비례하여 배치 단위를 조절함으로써 잔반 폐기 로스를 최소화"
        ],
        "caution": "콩나물국은 끓이기 전(0.65%)과 끓인 후(0.85%) 염도를 체크하여 간 편차 방지"
    }
}

# ==============================================================================
# 3. REAL-TIME EXCEL ENGINE (FIXES FORMULA CACHE SHIFT & TRACES CATEGORIES)
# ==============================================================================
@st.cache_data
def load_and_recalculate_all():
    candidates = [
        "cost_data.xlsx",
        "손정보쌈_원가계산_가나다순정리_소분카드정렬_판매가반영.xlsx",
        "손정보쌈_원가계산_가나다순정리_소분카드정렬_판매가반영(1).xlsx",
        "손정보쌈_원가계산_가나다순정리_소분카드정렬_판매가반영_2.xlsx",
        "손정보쌈_원가계산_레시피입력완성.xlsx"
    ]
    file_path = None
    for c in candidates:
        if os.path.exists(c):
            file_path = c
            break
    if file_path is None:
        st.error("엑셀 데이터 파일을 찾을 수 없습니다. 폴더 내 엑셀 파일명을 확인해 주세요.")
        st.stop()

    # 1) Raw Ingredient DB (Sheet 01)
    df_db_full = pd.read_excel(file_path, sheet_name="01_식재료마스터DB", skiprows=3)
    df_raw = df_db_full.iloc[:150, :9].copy()
    df_raw.columns = ["품목코드", "분류", "식재료명", "구매총중량", "구매가격", "손질수율", "실사용중량", "1g당실원가", "비고"]
    df_raw = df_raw.dropna(subset=["식재료명"]).copy()
    for col in ["구매총중량", "구매가격", "손질수율"]:
        df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce").fillna(0.0)
    df_raw["손질수율"] = np.where(df_raw["손질수율"] <= 0, 1.0, df_raw["손질수율"])
    df_raw["실사용중량"] = df_raw["구매총중량"] * df_raw["손질수율"]
    df_raw["1g당실원가"] = np.where(df_raw["실사용중량"] > 0, df_raw["구매가격"] / df_raw["실사용중량"], 0.0)
    df_raw["품목코드"] = [f"ING-{i+1:03d}" for i in range(len(df_raw))]

    unit_cost_map = dict(zip(df_raw["식재료명"].str.strip(), df_raw["1g당실원가"]))
    code_map = dict(zip(df_raw["식재료명"].str.strip(), df_raw["품목코드"]))
    raw_cat_map = dict(zip(df_raw["식재료명"].str.strip(), df_raw["분류"]))

    # 2) Sobun & Sauce Recipes (Sheet 02) - Dynamic Recalculation
    df_sobun_sheet = pd.read_excel(file_path, sheet_name="02_소분및배합레시피")
    sobun_list = []
    sobun_items_dict = {}
    sobun_cat_ratios = {}

    for i in range(30):
        start_row = 35 + i * 17
        if start_row >= len(df_sobun_sheet):
            break
        s_name = df_sobun_sheet.iloc[start_row, 2]
        if pd.isna(s_name) or str(s_name).strip() == "":
            continue
        s_name = str(s_name).strip()
        s_num = f"소분 #{i+1}"
        p_code = f"PREP-{i+1:02d}"
        yield_rate = pd.to_numeric(df_sobun_sheet.iloc[start_row, 6], errors="coerce")
        if pd.isna(yield_rate) or yield_rate <= 0:
            yield_rate = 1.0
        memo = str(df_sobun_sheet.iloc[start_row, 7]) if pd.notna(df_sobun_sheet.iloc[start_row, 7]) else ""

        items = []
        total_w = 0.0
        total_c = 0.0
        for r in range(start_row + 2, start_row + 14):
            ing = df_sobun_sheet.iloc[r, 2]
            qty = pd.to_numeric(df_sobun_sheet.iloc[r, 3], errors="coerce")
            i_memo = str(df_sobun_sheet.iloc[r, 7]) if pd.notna(df_sobun_sheet.iloc[r, 7]) else ""
            if pd.notna(ing) and str(ing).strip() != "":
                ing = str(ing).strip()
                qty_val = float(qty) if pd.notna(qty) else 0.0
                u_c = unit_cost_map.get(ing, 0.0)
                i_c = qty_val * u_c
                total_w += qty_val
                total_c += i_c
                items.append({
                    "품목코드": code_map.get(ing, "자동연동"),
                    "재료명": ing,
                    "투입량(g)": qty_val,
                    "1g단가(원)": u_c,
                    "투입원가(원)": i_c,
                    "메모": i_memo
                })
        final_w = total_w * yield_rate
        unit_c = (total_c / final_w) if final_w > 0 else 0.0
        for it in items:
            it["원가비중(%)"] = (it["투입원가(원)"] / total_c * 100.0) if total_c > 0 else 0.0

        unit_cost_map[s_name] = unit_c
        code_map[s_name] = p_code

        # Decompose sobun into 6 raw categories
        cat_sums = {"육류": 0.0, "해산물": 0.0, "채소/농산": 0.0, "소스/공산품": 0.0, "면/사리류": 0.0, "포장/소모품": 0.0}
        if total_c > 0:
            for it in items:
                ing = it["재료명"]
                c = it["투입원가(원)"]
                if ing in sobun_cat_ratios:
                    for k, v in sobun_cat_ratios[ing].items():
                        cat_sums[k] += c * v
                else:
                    rc = raw_cat_map.get(ing, "소스/공산품")
                    if rc not in cat_sums:
                        rc = "소스/공산품"
                    cat_sums[rc] += c
            sobun_cat_ratios[s_name] = {k: v / total_c for k, v in cat_sums.items()}
        else:
            sobun_cat_ratios[s_name] = {k: 0.0 for k in cat_sums}

        sobun_list.append({
            "소분번호": s_num,
            "품목코드": p_code,
            "소분명": s_name,
            "총투입중량(g)": total_w,
            "수율(%)": yield_rate * 100.0,
            "최종완성중량(g)": final_w,
            "1회배합총원가(원)": total_c,
            "1g당실원가(원)": unit_c,
            "100g당원가(원)": unit_c * 100.0,
            "메모": memo
        })
        sobun_items_dict[s_name] = items

    df_sobun = pd.DataFrame(sobun_list)

    # 3) Menu Recipes & Cost Calculation (Sheet 03)
    df_menu_sheet = pd.read_excel(file_path, sheet_name="03_메뉴별원가계산서")
    default_unconfirmed_prices = {
        "얼큰 알곤이 칼국수 전골(2인)": 24000.0,
        "화산 육칼국수": 11000.0,
        "알곤이 두부 두루치기": 22000.0,
        "직화 매콤 돼지불백(1인)": 10000.0,
        "손이가는 비빔당면": 7000.0
    }

    menu_list = []
    menu_items_dict = {}
    menu_cat_breakdown = {}

    for i in range(20):
        start_row = 25 + i * 17
        if start_row >= len(df_menu_sheet):
            break
        m_num = str(df_menu_sheet.iloc[start_row, 0]).strip()
        m_cat = str(df_menu_sheet.iloc[start_row, 1]).strip()
        m_name = str(df_menu_sheet.iloc[start_row, 2]).strip()
        raw_price = pd.to_numeric(df_menu_sheet.iloc[start_row, 5], errors="coerce")
        raw_price = float(raw_price) if pd.notna(raw_price) else 0.0
        target_rate = pd.to_numeric(df_menu_sheet.iloc[start_row, 7], errors="coerce")
        target_rate = float(target_rate) if pd.notna(target_rate) and target_rate > 0 else 0.30

        m_items = []
        total_c = 0.0
        cat_sums = {"육류": 0.0, "해산물": 0.0, "채소/농산": 0.0, "소스/공산품": 0.0, "면/사리류": 0.0, "포장/소모품": 0.0}

        for r in range(start_row + 2, start_row + 14):
            ing = df_menu_sheet.iloc[r, 2]
            qty = pd.to_numeric(df_menu_sheet.iloc[r, 3], errors="coerce")
            memo = str(df_menu_sheet.iloc[r, 8]) if pd.notna(df_menu_sheet.iloc[r, 8]) else ""
            if pd.notna(ing) and str(ing).strip() != "":
                ing = str(ing).strip()
                u_c = unit_cost_map.get(ing, 0.0)
                qty_val = float(qty) if (pd.notna(qty) and qty > 0) else 0.0
                i_c = qty_val * u_c
                total_c += i_c
                gubun = "자체소분/소스" if ing in sobun_cat_ratios else raw_cat_map.get(ing, "기타")
                m_items.append({
                    "구분": gubun,
                    "품목코드": code_map.get(ing, "-"),
                    "재료명": ing,
                    "투입량": qty_val,
                    "1g단가(원)": u_c,
                    "투입원가(원)": i_c,
                    "메모": memo
                })
                if i_c > 0:
                    if ing in sobun_cat_ratios:
                        for k, v in sobun_cat_ratios[ing].items():
                            cat_sums[k] += i_c * v
                    else:
                        rc = raw_cat_map.get(ing, "소스/공산품")
                        if rc not in cat_sums:
                            rc = "소스/공산품"
                        cat_sums[rc] += i_c
            elif memo != "":
                m_items.append({
                    "구분": "미산정/확인필요",
                    "품목코드": "-",
                    "재료명": "(미등록 재료)",
                    "투입량": 0.0,
                    "1g단가(원)": 0.0,
                    "투입원가(원)": 0.0,
                    "메모": memo
                })

        for it in m_items:
            it["원가비중(%)"] = (it["투입원가(원)"] / total_c * 100.0) if total_c > 0 else 0.0

        is_confirmed = raw_price > 0
        effective_price = raw_price if is_confirmed else default_unconfirmed_prices.get(m_name, 10000.0)
        cost_rate = (total_c / effective_price * 100.0) if effective_price > 0 else 0.0
        margin = effective_price - total_c
        rec_price = np.ceil((total_c / target_rate) / 100.0) * 100.0

        menu_list.append({
            "메뉴번호": m_num,
            "카테고리": m_cat,
            "메뉴명": m_name,
            "엑셀판매가": raw_price,
            "적용판매가": effective_price,
            "판매가확정여부": "확정" if is_confirmed else "미확정(가정값)",
            "1인분총원가": total_c,
            "원가율(%)": cost_rate,
            "1그릇당마진": margin,
            "권장판매가(30%)": rec_price
        })
        menu_items_dict[m_name] = m_items
        menu_cat_breakdown[m_name] = cat_sums

    df_menu = pd.DataFrame(menu_list)
    return df_raw, df_sobun, sobun_items_dict, df_menu, menu_items_dict, menu_cat_breakdown

df_raw, df_sobun, sobun_items_dict, df_menu, menu_items_dict, menu_cat_breakdown = load_and_recalculate_all()

# ==============================================================================
# 4. SIDEBAR BRANDING & NAVIGATION
# ==============================================================================
with st.sidebar:
    logo_candidates = ["logo.jpg", "손정보쌈로고 세로형.jpg", "logo.png", "input_file_17.png"]
    logo_loaded = False
    for lc in logo_candidates:
        if os.path.exists(lc):
            st.image(lc, use_container_width=True)
            logo_loaded = True
            break
    if not logo_loaded:
        st.markdown("""
        <div style='background:#1A1817; padding:18px; border-radius:12px; border:2px solid #CB994F; text-align:center; margin-bottom:12px;'>
            <div style='color:#CB994F; font-size:14px; font-weight:800; letter-spacing:2px;'>손정</div>
            <div style='color:#FFFFFF; font-size:24px; font-weight:900; margin-top:4px;'>손 정 보 쌈</div>
            <div style='color:#D8CFC4; font-size:11px; margin-top:4px;'>정성을 담은 손맛 · 가맹점 통합 포털</div>
        </div>
        """, unsafe_allow_html=True)

    selected_branch = st.selectbox(
        "🏪 관리 대상 가맹점 선택",
        ["본사 표준 모델 (전체)", "당산역점", "가산디지털단지역점", "강서구청점", "은평이마트점", "종로점", "울산명촌점", "과천점"]
    )
    st.markdown("---")
    nav = st.radio(
        "📂 통합 관리 카테고리",
        [
            "📋 1. 원클릭 레시피 & 보완매뉴얼",
            "🥩 2. 메뉴별 원가 & 식자재 단가",
            "🔍 3. 실제 매출·원가 차이 진단기",
            "💰 4. 매장 월간 손익 시뮬레이터"
        ]
    )
    st.markdown("---")
    st.caption("© 2026 (주)육성푸드 메뉴개발·R&D팀 | 실시간 수식 보정 엔진 가동 중")

# Top Hero Banner
st.markdown(f"""
<div class="sj-hero">
    <div>
        <div class="sj-hero-badge">손정 · SONJEONG BOSSAM FRANCHISE SYSTEM</div>
        <h1 class="sj-hero-title">손정보쌈 가맹점 원가 · 레시피 · 실매출 손익 통합 진단 포털</h1>
        <div class="sj-hero-sub">현재 선택 지점: <b>{selected_branch}</b> | 127종 식자재·소분·반찬 DB 및 28P 최신 조리 보완매뉴얼 실시간 연동</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# CATEGORY 1: 📋 원클릭 레시피 & 주방 보완매뉴얼 (28P 통합 뷰어)
# ==============================================================================
if nav == "📋 1. 원클릭 레시피 & 보완매뉴얼":
    t_m1, t_m2, t_m3 = st.tabs([
        "📖 주방 보완매뉴얼 원클릭 뷰어 (28P 전체)",
        "🍲 메뉴별 1인분 정량 레시피 카드 (20종)",
        "🧪 자체 소분·육수·소스·반찬 멀티 배합기 (23종)"
    ])

    with t_m1:
        st.markdown("#### 📖 항목을 클릭하면 조리 타임라인·염도·정량·주의사항이 카드 형태로 즉시 펼쳐집니다")
        cat_filter = st.radio(
            "매뉴얼 분류 선택",
            ["전체 보기", "보쌈/핵심전처리", "메인요리", "점심/전골", "점심/식사", "점심/사이드", "사이드/별미", "소분/육수/소스", "반찬/국"],
            horizontal=True
        )
        filtered_keys = [
            k for k, v in MANUAL_DB.items()
            if cat_filter == "전체 보기" or v["category"] == cat_filter
        ]

        cols_btn = st.columns(3)
        if "selected_manual" not in st.session_state:
            st.session_state.selected_manual = filtered_keys[0]
        for idx, k in enumerate(filtered_keys):
            with cols_btn[idx % 3]:
                if st.button(f"📌 {k}", key=f"m_btn_{idx}", use_container_width=True):
                    st.session_state.selected_manual = k

        sel_k = st.session_state.selected_manual if st.session_state.selected_manual in MANUAL_DB else filtered_keys[0]
        m_data = MANUAL_DB[sel_k]

        st.markdown(f"""
        <div class="sj-card-gold">
            <span class="sj-tag">{m_data['category']}</span>
            <span class="sj-tag">{m_data['updated']}</span>
            <h3 style="margin-top:10px; margin-bottom:6px; color:#1A1817;">{sel_k}</h3>
            <p style="color:#5C4938; font-weight:600; margin-bottom:0;">{m_data['summary']}</p>
        </div>
        """, unsafe_allow_html=True)

        c_left, c_right = st.columns([1, 1.15])
        with c_left:
            specs_html = "".join([f"<li style='margin-bottom:8px; font-weight:600;'>{s}</li>" for s in m_data["specs"]])
            st.markdown(f"""
            <div class="sj-card">
                <h4 style="color:#8C1D18; margin-top:0;">⚖️ 핵심 정량 · 배합 · 염도 기준</h4>
                <ul style="padding-left:20px; margin-bottom:0; line-height:1.6;">{specs_html}</ul>
            </div>
            """, unsafe_allow_html=True)
        with c_right:
            steps_html = "".join([
                f"<div style='padding:10px 12px; background:#FAF7F2; border-radius:8px; margin-bottom:8px; border-left:4px solid #CB994F; font-weight:600;'>{st_txt}</div>"
                for st_txt in m_data["steps"]
            ])
            st.markdown(f"""
            <div class="sj-card">
                <h4 style="color:#1A1817; margin-top:0;">⏱️ 표준 조리 타임라인 & 작업 순서</h4>
                {steps_html}
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="sj-card-alert">
            <b>⚠️ 현장 QSC 및 원가 방어 핵심 주의사항:</b> {m_data['caution']}
        </div>
        """, unsafe_allow_html=True)

    with t_m2:
        st.markdown("#### 🍲 메뉴별 1인분 표준 투입량 및 원가 비중 카드")
        c_sel1, c_sel2 = st.columns([1, 2])
        with c_sel1:
            m_cat_sel = st.selectbox("카테고리 필터", ["전체"] + df_menu["카테고리"].unique().tolist())
            sub_menus = df_menu if m_cat_sel == "전체" else df_menu[df_menu["카테고리"] == m_cat_sel]
            chosen_menu = st.radio("조회할 메뉴 클릭", sub_menus["메뉴명"].tolist())

            st.markdown("##### 📷 메뉴 대표사진")
            current_img = get_menu_image_path(chosen_menu)
            if current_img:
                st.image(str(current_img), use_container_width=True, caption=f"{chosen_menu} 대표사진")
            else:
                st.markdown(
                    """
                    <div style="height:210px; border:2px dashed #D8C9B1; border-radius:14px;
                                background:#FFFDF9; display:flex; align-items:center; justify-content:center;
                                color:#8A7A6D; font-weight:700; text-align:center; padding:18px;">
                        📷 아직 등록된 대표사진이 없습니다.<br>아래에서 메뉴 사진 1장을 업로드해 주세요.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            uploaded_menu_img = st.file_uploader(
                "대표사진 업로드 / 교체",
                type=["png", "jpg", "jpeg", "webp"],
                key=f"menu_img_{_safe_menu_key(chosen_menu)}",
                help="메뉴별 대표사진은 1장만 저장되며, 새 사진을 올리면 기존 사진이 교체됩니다."
            )
            if uploaded_menu_img is not None:
                save_menu_image(chosen_menu, uploaded_menu_img)
                st.success(f"{chosen_menu} 대표사진이 저장되었습니다.")
                st.rerun()

            st.caption("※ 메뉴별 대표사진은 현재 이 Streamlit 실행 폴더의 menu_images 폴더에 저장됩니다.")

        with c_sel2:
            m_row = df_menu[df_menu["메뉴명"] == chosen_menu].iloc[0]
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">적용 판매가 ({m_row['판매가확정여부']})</div><div class="sj-kpi-val">{int(m_row['적용판매가']):,}원</div><div class="sj-kpi-sub" style="color:#6E655F;">권장가: {int(m_row['권장판매가(30%)']):,}원</div></div>""", unsafe_allow_html=True)
            with k2:
                st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">1인분 표준 총원가</div><div class="sj-kpi-val">{int(m_row['1인분총원가']):,}원</div><div class="sj-kpi-sub" style="color:#2E6F40;">실시간 수식 보정 완료</div></div>""", unsafe_allow_html=True)
            with k3:
                rate_val = m_row["원가율(%)"]
                badge_col = "#2E6F40" if rate_val <= 30 else "#B8332A"
                st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">표준 식자재 원가율</div><div class="sj-kpi-val" style="color:{badge_col};">{rate_val:.1f}%</div><div class="sj-kpi-sub" style="color:{badge_col};">{'🟢 적정 (30% 이하)' if rate_val <= 30 else '🔴 주의 (30% 초과)'}</div></div>""", unsafe_allow_html=True)
            with k4:
                st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">1그릇당 매출총이익</div><div class="sj-kpi-val">{int(m_row['1그릇당마진']):,}원</div><div class="sj-kpi-sub" style="color:#6E655F;">식자재 차감 마진</div></div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            items = menu_items_dict[chosen_menu]
            for it in items:
                share = it["원가비중(%)"]
                qty_str = f"{it['투입량']:,.0f}g(개)" if it["투입량"] > 0 else "중량 확인필요"
                cost_str = f"{it['투입원가(원)']:,.0f}원 ({share:.1f}%)" if it["투입원가(원)"] > 0 else "0원 (미산정)"
                memo_badge = f"<div style='font-size:12px; color:#B8332A; margin-top:4px;'>📌 {it['메모']}</div>" if it["메모"] else ""
                st.markdown(f"""
                <div class="sj-card" style="padding:14px 18px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span class="sj-tag">{it['구분']}</span>
                            <b style="font-size:15px;">{it['재료명']}</b>
                            <span style="color:#6E655F; font-size:13px; margin-left:8px;">단가: {it['1g단가(원)']:.2f}원/g</span>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-weight:800; font-size:15px; color:#1A1817;">투입: {qty_str}</span>
                            <span style="margin-left:12px; font-weight:700; color:#8C1D18;">{cost_str}</span>
                        </div>
                    </div>
                    <div class="sj-prog-bg"><div class="sj-prog-fill" style="width:{min(share, 100):.1f}%;"></div></div>
                    {memo_badge}
                </div>
                """, unsafe_allow_html=True)

    with t_m3:
        st.markdown("#### 🧪 자체 소분 및 수제 소스·육수 배합 시뮬레이터 (배수 자동 환산)")
        c_sb1, c_sb2 = st.columns([1, 2])
        with c_sb1:
            chosen_sobun = st.selectbox("소분/소스/반찬 레시피 선택 (23종)", df_sobun["소분명"].tolist())
            batch_mult = st.radio("배합 배수 선택 (대량 조리 환산)", [1, 2, 5, 10], horizontal=True, format_func=lambda x: f"{x}배합")
        with c_sb2:
            sb_row = df_sobun[df_sobun["소분명"] == chosen_sobun].iloc[0]
            st.markdown(f"""
            <div class="sj-card-gold">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span class="sj-tag">{sb_row['소분번호']} ({sb_row['품목코드']})</span>
                        <h3 style="margin:6px 0;">{chosen_sobun} — {batch_mult}배합 기준</h3>
                        <div style="font-size:13px; color:#5C4938;">📌 {sb_row['메모'] if sb_row['메모'] else '표준 수율 반영 자동 계산'}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:13px; color:#6E655F;">총 투입: <b>{sb_row['총투입중량(g)']*batch_mult:,.0f}g</b> ➔ 완성: <b>{sb_row['최종완성중량(g)']*batch_mult:,.0f}g</b> (수율 {sb_row['수율(%)']:.1f}%)</div>
                        <div style="font-size:20px; font-weight:800; color:#8C1D18; margin-top:4px;">배합 총원가: {sb_row['1회배합총원가(원)']*batch_mult:,.0f}원 <span style="font-size:14px; color:#1A1817;">(1g당 {sb_row['1g당실원가(원)']:.2f}원)</span></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            for it in sobun_items_dict[chosen_sobun]:
                st.markdown(f"""
                <div class="sj-card" style="padding:12px 18px; margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between;">
                        <div><span class="sj-tag">{it['품목코드']}</span> <b>{it['재료명']}</b></div>
                        <div><b>투입량: {it['투입량(g)']*batch_mult:,.1f}g</b> | 원가: {it['투입원가(원)']*batch_mult:,.0f}원 ({it['원가비중(%)']:.1f}%)</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ==============================================================================
# CATEGORY 2: 🥩 메뉴별 원가 & 식자재 단가 비주얼 분석
# ==============================================================================
elif nav == "🥩 2. 메뉴별 원가 & 식자재 단가":
    st.markdown("#### 🥩 전 메뉴 원가율 신호등 카드 & 121종 식자재 마스터 검색")
    sub_t1, sub_t2 = st.tabs(["📊 20종 메뉴 원가율 & 품목군 구성비 카드", "📦 식자재 & 자체소분 마스터 DB (127종)"])

    with sub_t1:
        # Summary KPIs
        confirmed_df = df_menu[df_menu["판매가확정여부"] == "확정"]
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">전체 등록 메뉴 수</div><div class="sj-kpi-val">20종</div><div class="sj-kpi-sub">판매가 확정 15종 / 미확정 5종</div></div>""", unsafe_allow_html=True)
        with k2:
            st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">확정 15종 평균 원가율</div><div class="sj-kpi-val" style="color:#2E6F40;">{confirmed_df['원가율(%)'].mean():.1f}%</div><div class="sj-kpi-sub">중앙값 {confirmed_df['원가율(%)'].median():.1f}% (목표 30% 이하)</div></div>""", unsafe_allow_html=True)
        with k3:
            st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">20종 평균 1인분 원가</div><div class="sj-kpi-val">{int(df_menu['1인분총원가'].mean()):,}원</div><div class="sj-kpi-sub">최소 269원 ~ 최대 10,698원</div></div>""", unsafe_allow_html=True)
        with k4:
            st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">원가율 30% 초과 주의 메뉴</div><div class="sj-kpi-val" style="color:#B8332A;">3종</div><div class="sj-kpi-sub">맵불스지·부추호박전·얼큰알곤이</div></div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        grid_cols = st.columns(2)
        for idx, row in df_menu.iterrows():
            with grid_cols[idx % 2]:
                r_pct = row["원가율(%)"]
                status_color = "#2E6F40" if r_pct <= 25 else ("#CB994F" if r_pct <= 30 else "#B8332A")
                status_text = "🟢 우수 (25% 이하)" if r_pct <= 25 else ("🟡 적정 (25~30%)" if r_pct <= 30 else "🔴 관리필요 (30% 초과)")
                cats = menu_cat_breakdown[row["메뉴명"]]
                top_cats = sorted([(k, v) for k, v in cats.items() if v > 0], key=lambda x: x[1], reverse=True)
                cat_badges = " ".join([f"<span class='sj-tag'>{k}: {int(v):,}원</span>" for k, v in top_cats[:3]])
                st.markdown(f"""
                <div class="sj-card" style="padding:16px 20px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span class="sj-tag">{row['메뉴번호']} · {row['카테고리']}</span>
                            <b style="font-size:17px;">{row['메뉴명']}</b>
                        </div>
                        <span style="font-weight:800; color:{status_color}; font-size:14px;">{status_text}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-top:10px; font-size:14px;">
                        <span>판매가: <b>{int(row['적용판매가']):,}원</b> ({row['판매가확정여부']})</span>
                        <span>1인분 원가: <b style="color:#8C1D18;">{int(row['1인분총원가']):,}원 ({r_pct:.1f}%)</b></span>
                        <span>그릇당 마진: <b style="color:#2E6F40;">{int(row['1그릇당마진']):,}원</b></span>
                    </div>
                    <div class="sj-prog-bg"><div class="sj-prog-fill" style="width:{min(r_pct*2.5, 100):.1f}%;"></div></div>
                    <div style="margin-top:8px;">{cat_badges}</div>
                </div>
                """, unsafe_allow_html=True)

    with sub_t2:
        f_col1, f_col2 = st.columns([1.2, 2])
        with f_col1:
            sel_ing_cat = st.selectbox("품목군 필터", ["전체"] + df_raw["분류"].unique().tolist())
        with f_col2:
            q_str = st.text_input("🔍 식자재명 또는 거래처 검색", placeholder="예: 가브리살, 명태곤이, 사골, 지우푸드...")

        f_df = df_raw.copy()
        if sel_ing_cat != "전체":
            f_df = f_df[f_df["분류"] == sel_ing_cat]
        if q_str:
            f_df = f_df[f_df["식재료명"].str.contains(q_str, na=False) | f_df["비고"].str.contains(q_str, na=False)]

        st.markdown(f"총 **{len(f_df)}종**의 원재료가 조회되었습니다.")
        ing_cols = st.columns(3)
        for i, (_, r_ing) in enumerate(f_df.iterrows()):
            with ing_cols[i % 3]:
                st.markdown(f"""
                <div class="sj-card" style="padding:14px 16px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between;">
                        <span class="sj-tag">{r_ing['품목코드']} · {r_ing['분류']}</span>
                        <b style="color:#8C1D18;">1g(개)당 {r_ing['1g당실원가']:,.2f}원</b>
                    </div>
                    <div style="font-size:15px; font-weight:800; margin-top:6px;">{r_ing['식재료명']}</div>
                    <div style="font-size:13px; color:#5C4938; margin-top:4px;">구매규격: {r_ing['구매총중량']:,.0f}g(개) | 구매가: <b>{int(r_ing['구매가격']):,}원</b></div>
                    <div style="font-size:11px; color:#888; margin-top:4px;">{r_ing['비고'] if pd.notna(r_ing['비고']) else ''}</div>
                </div>
                """, unsafe_allow_html=True)

# ==============================================================================
# CATEGORY 3: 🔍 가맹점 실제 매출(음식+주류) vs 실사용 원가 차이(Variance) 정밀 진단기
# ==============================================================================
elif nav == "🔍 3. 실제 매출·원가 차이 진단기":
    st.markdown("""
    <div class="sj-card-gold">
        <h3 style="margin-top:0; color:#1A1817;">🔍 가맹점 [실제 POS 매출 vs 실제 매입·사용 원가] 차이(Variance) 정밀 진단 시스템</h3>
        <p style="margin-bottom:0; color:#5C4938; font-weight:600;">
        이론적인 식자재 레시피 원가만 보는 것을 넘어, 매장에서 실제 판매한 <b>음식 + 주류/음료 총매출</b>과 <b>본사물류 + 지정식자재 + 주류도매 + 개인구매(마트/시장 사입) 실사용 금액</b>을 대조하여 <b>어느 파트에서 원가가 새어 나갔는지</b> 원인과 개선 처방전을 자동 도출합니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_step1, col_step2 = st.columns([1.15, 1])

    with col_step1:
        st.markdown("#### 1️⃣ 당월 가맹점 실제 판매량 입력 (음식 20종 + 주류/음료)")
        default_sales_qty = [380, 140, 260, 220, 45, 0, 190, 0, 0, 0, 160, 110, 85, 130, 65, 90, 120, 95, 150, 110]
        pos_df = pd.DataFrame({
            "메뉴명": df_menu["메뉴명"],
            "실판매가(원)": df_menu["적용판매가"].astype(int),
            "표준원가(원)": df_menu["1인분총원가"].round(0).astype(int),
            "월판매수량": default_sales_qty
        })
        edited_pos = st.data_editor(
            pos_df,
            column_config={
                "메뉴명": st.column_config.TextColumn("메뉴명", disabled=True),
                "실판매가(원)": st.column_config.NumberColumn("실판매가(원)", min_value=0, step=500, format="%d원"),
                "표준원가(원)": st.column_config.NumberColumn("1인분 표준원가", disabled=True, format="%d원"),
                "월판매수량": st.column_config.NumberColumn("당월 판매량(그릇)", min_value=0, step=10, format="%d개")
            },
            hide_index=True,
            use_container_width=True,
            height=380
        )

        st.markdown("##### 🍶 주류 및 음료 당월 판매 실적 입력")
        bev_df = pd.DataFrame([
            {"품목명": "소주 (참이슬/처음처럼/새로 등)", "판매단가(원)": 5000, "표준원가(원)": 1350, "월판매수량": 650},
            {"품목명": "맥주 (카스/테라/켈리 등)", "판매단가(원)": 5000, "표준원가(원)": 1650, "월판매수량": 420},
            {"품목명": "전통주/막걸리/청하", "판매단가(원)": 5000, "표준원가(원)": 1500, "월판매수량": 120},
            {"품목명": "탄산음료 (콜라/사이다 캔·병)", "판매단가(원)": 2000, "표준원가(원)": 650, "월판매수량": 350},
        ])
        edited_bev = st.data_editor(
            bev_df,
            column_config={
                "품목명": st.column_config.TextColumn("주류/음료 품목", disabled=True),
                "판매단가(원)": st.column_config.NumberColumn("판매가(원)", step=500, format="%d원"),
                "표준원가(원)": st.column_config.NumberColumn("병/캔당 매입원가", step=50, format="%d원"),
                "월판매수량": st.column_config.NumberColumn("당월 판매수량(병/캔)", step=10, format="%d병")
            },
            hide_index=True,
            use_container_width=True
        )

    # Compute Theoretical Revenue & Theoretical Cost by Category
    food_rev = float((edited_pos["실판매가(원)"] * edited_pos["월판매수량"]).sum())
    bev_rev = float((edited_bev["판매단가(원)"] * edited_bev["월판매수량"]).sum())
    total_actual_rev = food_rev + bev_rev

    theo_cat_totals = {
        "육류 (가브리살/스지 등)": 0.0,
        "해산물 (알/곤이/꼬막/오징어)": 0.0,
        "채소/농산 (배추/미나리/야채)": 0.0,
        "소스/공산품 (육수/분말/양념)": 0.0,
        "면/사리류 (칼국수/파스타/당면)": 0.0,
        "주류/음료 (소주/맥주/음료)": float((edited_bev["표준원가(원)"] * edited_bev["월판매수량"]).sum()),
        "포장/소모품 및 반찬류": 0.0
    }

    for _, r_pos in edited_pos.iterrows():
        m_name = r_pos["메뉴명"]
        qty = float(r_pos["월판매수량"])
        if qty <= 0:
            continue
        c_map = menu_cat_breakdown.get(m_name, {})
        theo_cat_totals["육류 (가브리살/스지 등)"] += c_map.get("육류", 0.0) * qty
        theo_cat_totals["해산물 (알/곤이/꼬막/오징어)"] += c_map.get("해산물", 0.0) * qty
        theo_cat_totals["채소/농산 (배추/미나리/야채)"] += c_map.get("채소/농산", 0.0) * qty
        theo_cat_totals["소스/공산품 (육수/분말/양념)"] += c_map.get("소스/공산품", 0.0) * qty
        theo_cat_totals["면/사리류 (칼국수/파스타/당면)"] += c_map.get("면/사리류", 0.0) * qty
        theo_cat_totals["포장/소모품 및 반찬류"] += c_map.get("포장/소모품", 0.0) * qty

    # Estimate standard side dish (어묵/콩나물/소세지/콩나물국) & packaging allowance (~2.2% of food revenue)
    theo_cat_totals["포장/소모품 및 반찬류"] += food_rev * 0.022
    total_theo_cost = sum(theo_cat_totals.values())

    with col_step2:
        st.markdown("#### 2️⃣ 당월 실제 매입·사용 금액 입력 (물류업체 + 개인 구매 합산)")
        st.caption("본사/지정 물류 명세서 금액과 가맹점에서 마트·시장·개인카드로 직접 구매한 금액을 품목군별로 입력해 주세요.")

        default_logistics = [
            int(theo_cat_totals["육류 (가브리살/스지 등)"] * 1.12),
            int(theo_cat_totals["해산물 (알/곤이/꼬막/오징어)"] * 1.10),
            int(theo_cat_totals["채소/농산 (배추/미나리/야채)"] * 0.85),
            int(theo_cat_totals["소스/공산품 (육수/분말/양념)"] * 1.03),
            int(theo_cat_totals["면/사리류 (칼국수/파스타/당면)"] * 1.02),
            int(theo_cat_totals["주류/음료 (소주/맥주/음료)"] * 1.03),
            int(theo_cat_totals["포장/소모품 및 반찬류"] * 0.90)
        ]
        default_personal = [
            150000,
            120000,
            680000,
            90000,
            30000,
            40000,
            240000
        ]

        spend_input_df = pd.DataFrame({
            "품목군": list(theo_cat_totals.keys()),
            "표준원가(원)": [int(v) for v in theo_cat_totals.values()],
            "물류/주류업체 매입(원)": default_logistics,
            "개인구매/사입(원)": default_personal
        })

        edited_spend = st.data_editor(
            spend_input_df,
            column_config={
                "품목군": st.column_config.TextColumn("품목군", disabled=True),
                "표준원가(원)": st.column_config.NumberColumn("POS 기준 표준원가", disabled=True, format="%d원"),
                "물류/주류업체 매입(원)": st.column_config.NumberColumn("본사/물류/주류업체 명세서", min_value=0, step=50000, format="%d원"),
                "개인구매/사입(원)": st.column_config.NumberColumn("개인구매(마트/시장/인터넷)", min_value=0, step=10000, format="%d원")
            },
            hide_index=True,
            use_container_width=True
        )

        inv_adj = st.number_input("📦 월말 재고 증감 보정액 (기초재고 - 기말재고, 없으면 0원)", value=0, step=50000)

    # Calculate Variance & Diagnostic Results
    edited_spend["실제사용원가(원)"] = edited_spend["물류/주류업체 매입(원)"] + edited_spend["개인구매/사입(원)"]
    edited_spend["원가차액(실제-표준)"] = edited_spend["실제사용원가(원)"] - edited_spend["표준원가(원)"]
    edited_spend["초과율(%)"] = np.where(
        edited_spend["표준원가(원)"] > 0,
        (edited_spend["원가차액(실제-표준)"] / edited_spend["표준원가(원)"]) * 100.0,
        0.0
    )

    total_logistics = float(edited_spend["물류/주류업체 매입(원)"].sum())
    total_personal = float(edited_spend["개인구매/사입(원)"].sum())
    total_actual_cost = total_logistics + total_personal + float(inv_adj)
    total_variance = total_actual_cost - total_theo_cost

    theo_rate_pct = (total_theo_cost / total_actual_rev * 100.0) if total_actual_rev > 0 else 0.0
    actual_rate_pct = (total_actual_cost / total_actual_rev * 100.0) if total_actual_rev > 0 else 0.0
    rate_gap_pctp = actual_rate_pct - theo_rate_pct

    # Save to session_state for Category 4 P&L integration
    st.session_state["sim_actual_rev"] = total_actual_rev
    st.session_state["sim_actual_cost"] = total_actual_cost
    st.session_state["sim_theo_cost"] = total_theo_cost

    st.markdown("---")
    st.markdown("#### 3️⃣ 표준원가 vs 실제원가 비교 대시보드 & 과다 지출 부위 색출")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">당월 실제 총매출 (음식+주류)</div><div class="sj-kpi-val">{int(total_actual_rev):,}원</div><div class="sj-kpi-sub">음식 {int(food_rev):,}원 / 주류 {int(bev_rev):,}원 ({bev_rev/total_actual_rev*100 if total_actual_rev>0 else 0:.1f}%)</div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">POS 판매량 기준 표준원가</div><div class="sj-kpi-val">{int(total_theo_cost):,}원</div><div class="sj-kpi-sub" style="color:#2E6F40;">표준 원가율: {theo_rate_pct:.1f}%</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">실제 총 사용원가 (물류+개인사입)</div><div class="sj-kpi-val" style="color:#8C1D18;">{int(total_actual_cost):,}원</div><div class="sj-kpi-sub" style="color:#8C1D18;">실제 원가율: {actual_rate_pct:.1f}% (개인사입 {int(total_personal):,}원)</div></div>""", unsafe_allow_html=True)
    with m4:
        var_color = "#B8332A" if total_variance > 0 else "#2E6F40"
        st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">원가 차액 (실제 - 표준 누수액)</div><div class="sj-kpi-val" style="color:{var_color};">{int(total_variance):+,}원</div><div class="sj-kpi-sub" style="color:{var_color};">원가율 격차: {rate_gap_pctp:+.1f}%p ({'초과 누수 발생' if total_variance > 0 else '원가 절감 우수'})</div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # Category-by-Category Variance Visual Cards
    sorted_var = edited_spend.sort_values("원가차액(실제-표준)", ascending=False)
    v_cols = st.columns(2)
    for idx, (_, r_v) in enumerate(sorted_var.iterrows()):
        with v_cols[idx % 2]:
            diff_v = r_v["원가차액(실제-표준)"]
            pct_v = r_v["초과율(%)"]
            card_cls = "sj-card-alert" if diff_v > 150000 else ("sj-card" if diff_v > 0 else "sj-card-good")
            badge_str = f"🚨 +{int(diff_v):,}원 초과 (+{pct_v:.1f}%)" if diff_v > 0 else f"✅ {int(diff_v):,}원 절감 ({pct_v:.1f}%)"
            st.markdown(f"""
            <div class="{card_cls}" style="padding:14px 18px; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="font-size:16px;">{r_v['품목군']}</b>
                    <span style="font-weight:800; color:{'#B8332A' if diff_v > 0 else '#2E6F40'};">{badge_str}</span>
                </div>
                <div style="font-size:13px; color:#5C4938; margin-top:6px;">
                    표준원가: <b>{int(r_v['표준원가(원)']):,}원</b> vs 실제원가: <b>{int(r_v['실제사용원가(원)']):,}원</b>
                    (물류 {int(r_v['물류/주류업체 매입(원)']):,}원 + 개인구매 {int(r_v['개인구매/사입(원)']):,}원)
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ==========================================================================
    # AUTOMATIC ROOT-CAUSE CONCLUSION ENGINE (자동 원인 진단 및 결론 처방전)
    # ==========================================================================
    st.markdown("#### 4️⃣ AI 슈퍼바이저 종합 결론 및 현장 개선 처방전")
    worst_row = sorted_var.iloc[0]
    second_row = sorted_var.iloc[1]
    bev_share = (bev_rev / total_actual_rev * 100.0) if total_actual_rev > 0 else 0.0
    personal_share = (total_personal / total_actual_cost * 100.0) if total_actual_cost > 0 else 0.0

    conclusions = []
    # 1. Meat Variance Check
    meat_diff = float(edited_spend.loc[edited_spend["품목군"].str.contains("육류"), "원가차액(실제-표준)"].values[0])
    if meat_diff > 100000:
        conclusions.append(
            f"<li><b>[육류 파트 원가 과다 (+{int(meat_diff):,}원 초과)]</b>: 가브리살 및 자숙스지 실사용량이 POS 판매량 기준 표준치를 초과했습니다. "
            f"① <b>가브리보쌈 삶기 매뉴얼(중불 40분 삶기 + 20분 뜸들이기)</b> 미준수로 인한 수율 저하(정상 수율 대비 중량 손실), "
            f"② 점심 보쌈정식(일반 <b>120g</b> / 특 <b>170g</b>) 및 저녁 보쌈(소 <b>300g</b> / 중 <b>400g</b>) 슬라이스 시 전자저울 미사용으로 인한 <b>과다 제공(오버포셔닝)</b> 여부를 즉시 점검하십시오.</li>"
        )
    # 2. Seafood Variance Check
    sea_diff = float(edited_spend.loc[edited_spend["품목군"].str.contains("해산물"), "원가차액(실제-표준)"].values[0])
    if sea_diff > 80000:
        conclusions.append(
            f"<li><b>[해산물 파트 원가 누수 (+{int(sea_diff):,}원 초과)]</b>: 알·곤이 및 꼬막 원가가 표준 대비 높게 발생했습니다. "
            f"① 알곤이 칼국수/전골 조리 시 <b>1인분 정량(알 50g / 곤이 120g)</b> 및 저녁 알곤이볶음(알 180g / 곤이 360g) 소분 박스 정량 준수 여부와 "
            f"② 알곤이 찌기(중불 50분) 후 보관 폐기 로스, 냉동 꼬막 해동 수율(100g 소분 ➔ 해동 후 <b>80g</b>)을 재점검하십시오.</li>"
        )
    # 3. Vegetable & Personal Purchase Check
    veg_diff = float(edited_spend.loc[edited_spend["품목군"].str.contains("채소"), "원가차액(실제-표준)"].values[0])
    if veg_diff > 80000 or personal_share > 8.0:
        conclusions.append(
            f"<li><b>[채소/농산 및 개인 구매 과다 (채소 {int(veg_diff):+,}원 / 개인사입 비중 {personal_share:.1f}%)]</b>: "
            f"마트·시장 등 개인 구매 금액이 <b>{int(total_personal):,}원</b>에 달합니다. "
            f"① 배추 절이기 작업 시 <b>배추 3통 절임 후 남은 소금물을 버리지 않고 알배추 2박스 절임에 재사용</b>하는 보완매뉴얼을 적용하여 천일염·배추 로스를 줄이고, "
            f"② 미나리는 <b>줄기(냉국수 50g)와 잎(무침 40g)을 분리 사용</b>하며, 점심 기본반찬(어묵·콩나물·소세지볶음)을 점심 매출 규모에 맞게 조절하여 잔반 폐기를 줄이십시오.</li>"
        )
    # 4. Liquor/Beverage Mix Check
    if bev_share < 10.0:
        conclusions.append(
            f"<li><b>[주류/음료 고마진 매출 비중 진단 (현재 {bev_share:.1f}%)]</b>: 원가율이 약 27~33%로 마진 기여도가 높은 주류/음료 매출 비중이 다소 낮습니다. "
            f"저녁 시간대 가브리김치보쌈·매콤알곤이볶음·맵불스지 주문 고객을 대상으로 주류 프로모션 및 <b>마무리 알곤이 치즈 파스타(원가율 18.3%)</b> 추가 주문을 유도하면 매장 평균 원가율을 즉시 1.5%p 이상 낮출 수 있습니다.</li>"
        )

    if not conclusions:
        conclusions.append("<li><b>[전 품목군 원가 관리 우수]</b>: 모든 식자재 파트가 POS 표준 원가 범위 내에서 안정적으로 통제되고 있습니다. 현재의 전자저울 계량 및 소분 매뉴얼을 유지하십시오.</li>")

    conc_html = "".join(conclusions)
    st.markdown(f"""
    <div class="sj-card-gold">
        <h4 style="margin-top:0; color:#8C1D18;">📋 [{selected_branch}] 당월 원가 격차 종합 결론 리포트</h4>
        <p style="font-size:15px; font-weight:700; color:#1A1817;">
            당월 총매출 <b>{int(total_actual_rev):,}원</b> 대비 이론적 표준 원가는 <b>{int(total_theo_cost):,}원({theo_rate_pct:.1f}%)</b>이나,
            실제 매입·사용 원가는 <b>{int(total_actual_cost):,}원({actual_rate_pct:.1f}%)</b>으로 총 <b style="color:#B8332A;">{int(total_variance):+,}원({rate_gap_pctp:+.1f}%p)</b>의 차이가 발생했습니다.
            가장 원가 차이가 큰 핵심 요인은 <b>1순위 [{worst_row['품목군']} ({int(worst_row['원가차액(실제-표준)']):+,}원)]</b> 및 <b>2순위 [{second_row['품목군']} ({int(second_row['원가차액(실제-표준)']):+,}원)]</b>입니다.
        </p>
        <ul style="line-height:1.75; font-size:14px; color:#1A1817; margin-bottom:0;">
            {conc_html}
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# CATEGORY 4: 💰 매장 월간 통합 손익계산서 & 마진 시뮬레이터
# ==============================================================================
elif nav == "💰 4. 매장 월간 손익 시뮬레이터":
    st.markdown("#### 💰 가맹점 월간 최종 손익계산서(P&L) 및 손익분기점 시뮬레이터")
    default_rev = int(st.session_state.get("sim_actual_rev", 45000000))
    default_act_cost = int(st.session_state.get("sim_actual_cost", 13200000))
    default_theo_cost = int(st.session_state.get("sim_theo_cost", 11500000))

    c_p1, c_p2 = st.columns([1, 1])
    with c_p1:
        st.markdown("##### 1️⃣ 월 매출 · 식자재 원가 · 수수료 설정")
        m_rev = st.number_input("당월 총매출액 (음식 + 주류/음료 합산, 원)", value=default_rev, step=500000)
        cost_mode = st.radio("적용할 원가 기준", ["실제 사용 원가 (물류+개인사입 반영)", "표준 레시피 원가 (누수 개선 시 시뮬레이션)"], horizontal=True)
        m_cost = st.number_input(
            "당월 총 식자재·주류 원가 (원)",
            value=default_act_cost if "실제" in cost_mode else default_theo_cost,
            step=100000
        )
        comm_rate = st.slider("평균 결제/배달 플랫폼 수수료율 (%)", min_value=0.0, max_value=25.0, value=6.5, step=0.5)
        m_comm = m_rev * (comm_rate / 100.0)

    with c_p2:
        st.markdown("##### 2️⃣ 매장 월 고정비 입력 (임대료 · 인건비 · 관리비)")
        f_c1, f_c2 = st.columns(2)
        with f_c1:
            rent_cost = st.number_input("월 임대료 및 관리비 (원)", value=2200000, step=100000)
            labor_cost = st.number_input("월 인건비 총액 (주방/홀/파트타임)", value=8500000, step=200000)
        with f_c2:
            util_cost = st.number_input("수도광열비 (전기/가스/수도)", value=950000, step=50000)
            etc_fixed = st.number_input("세무기장·방역·통신·기타 고정비", value=650000, step=50000)

    total_fixed = rent_cost + labor_cost + util_cost + etc_fixed
    gross_profit = m_rev - m_cost - m_comm
    net_profit = gross_profit - total_fixed
    net_margin_pct = (net_profit / m_rev * 100.0) if m_rev > 0 else 0.0
    cost_pct = (m_cost / m_rev * 100.0) if m_rev > 0 else 0.0

    # If cost leaks are eliminated
    potential_saving = max(0, default_act_cost - default_theo_cost)

    st.markdown("---")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">당월 총매출액</div><div class="sj-kpi-val">{int(m_rev):,}원</div><div class="sj-kpi-sub">100.0%</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">식자재·주류 원가 + 수수료</div><div class="sj-kpi-val" style="color:#8C1D18;">{int(m_cost + m_comm):,}원</div><div class="sj-kpi-sub">원가 {cost_pct:.1f}% + 수수료 {comm_rate:.1f}%</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">월 고정비 합계</div><div class="sj-kpi-val">{int(total_fixed):,}원</div><div class="sj-kpi-sub">매출 대비 {(total_fixed/m_rev*100 if m_rev>0 else 0):.1f}%</div></div>""", unsafe_allow_html=True)
    with k4:
        np_col = "#2E6F40" if net_profit > 0 else "#B8332A"
        st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">💰 사장님 월 최종 순수익 (세전)</div><div class="sj-kpi-val" style="color:{np_col};">{int(net_profit):,}원</div><div class="sj-kpi-sub" style="color:{np_col};">순이익률: {net_margin_pct:.1f}%</div></div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sj-card-gold" style="margin-top:16px;">
        <h4 style="margin-top:0; color:#1A1817;">💡 원가 누수 차단 시 추가 순수익 상승 효과</h4>
        <p style="margin-bottom:0; font-size:15px; color:#5C4938;">
        현재 [카테고리 3]에서 진단된 표준원가 대비 초과 누수액(<b>+{int(potential_saving):,}원</b>)을 정량 계량 및 매뉴얼 준수로 잡을 경우,
        매출 증가 없이도 사장님의 월 최종 순수익은 <b>{int(net_profit):,}원 ➔ {int(net_profit + potential_saving):,}원</b>으로 즉시 상승합니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
