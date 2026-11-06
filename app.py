import os
import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# 1. 페이지 기본 설정 & 손정보쌈(手:정) 전용 디자인 시스템 (한 줄 정렬 및 가시성 최적화)
# ==============================================================================
st.set_page_config(
    page_title="손정보쌈 | 가맹점 원가·레시피·손익 통합 진단 포털",
    page_icon="🥩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 메뉴별 사진 저장용 폴더 생성
PHOTO_DIR = "menu_photos"
os.makedirs(PHOTO_DIR, exist_ok=True)

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
    /* 상단 브랜드 배너 */
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
        font-size: 25px;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .sj-hero-sub {
        font-size: 14px;
        color: #D8CFC4;
        margin-top: 4px;
    }
    /* 카드 UI 공통 */
    .sj-card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 18px 20px;
        border: 1px solid #E6DEC8;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 14px;
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
        padding: 18px 20px;
        border-left: 6px solid #B8332A;
        border-top: 1px solid #F1D2CF;
        border-right: 1px solid #F1D2CF;
        border-bottom: 1px solid #F1D2CF;
        margin-bottom: 14px;
    }
    .sj-card-good {
        background: #F6FBF7;
        border-radius: 14px;
        padding: 18px 20px;
        border-left: 6px solid #2E6F40;
        border-top: 1px solid #CBE5D1;
        border-right: 1px solid #CBE5D1;
        border-bottom: 1px solid #CBE5D1;
        margin-bottom: 14px;
    }
    /* 핵심 지표(KPI) 박스 */
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
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .sj-kpi-val {
        font-size: 22px;
        font-weight: 800;
        color: #1A1817;
        margin-top: 4px;
        white-space: nowrap;
    }
    .sj-kpi-sub {
        font-size: 12px;
        font-weight: 600;
        margin-top: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    /* 메뉴명 및 원가 상태 한 줄 정렬 */
    .sj-nowrap-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
        flex-wrap: nowrap;
        width: 100%;
    }
    .sj-menu-title-wrap {
        display: flex;
        align-items: center;
        gap: 8px;
        min-width: 0;
        flex: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .sj-menu-name {
        font-size: 16px;
        font-weight: 800;
        color: #1A1817;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .sj-status-badge {
        display: inline-block;
        font-weight: 800;
        font-size: 13px;
        padding: 4px 10px;
        border-radius: 20px;
        white-space: nowrap;
        flex-shrink: 0;
    }
    .sj-nowrap-metrics {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 8px;
        margin-top: 10px;
        font-size: 13.5px;
        white-space: nowrap;
        flex-wrap: nowrap;
    }
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
    .sj-tag {
        display: inline-block;
        background: #F4EFE6;
        color: #5C4938;
        font-weight: 600;
        font-size: 12px;
        padding: 3px 9px;
        border-radius: 6px;
        margin-right: 4px;
        border: 1px solid #E2D9C8;
        white-space: nowrap;
        flex-shrink: 0;
    }
    .sj-photo-placeholder {
        background: #FAF7F2;
        border: 2px dashed #CB994F;
        border-radius: 12px;
        padding: 24px 14px;
        text-align: center;
        color: #6E655F;
        font-size: 13px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. 주방 조리 매뉴얼 데이터베이스 (29개 항목 개별 분리)
# ==============================================================================
MANUAL_DB = {
    "1. 가브리보쌈 삶기 및 사전 준비": {
        "category": "보쌈/핵심손질",
        "updated": "개정일: 25.10.28",
        "summary": "가브리살 해동 · 핏물 빼기(1시간 이상) · 삶기(40분) · 뜸들기(20분) 표준 순서",
        "specs": [
            "대량 배합 ① (가브리살 10kg 기준): 물 23kg + 보쌈분말 600g",
            "소량 배합 ② (가브리살 5kg 기준): 물 11.5kg + 보쌈분말 300g (전날 미리 준비)",
            "권장 조리 시간: 중불 40분 삶기 후 불 끄고 20분 뜸들이기"
        ],
        "steps": [
            "1단계 (해동): 전날 가브리살을 냉장고에서 해동합니다.",
            "2단계 (핏물 빼기): 해동된 가브리살을 찬물에 담가 1시간 이상 핏물을 충분히 빼줍니다.",
            "3단계 (육수 배합): 고기 양에 맞춰 물과 보쌈분말을 정량대로 섞어 끓입니다.",
            "4단계 (삶기 - 40분): 육수가 끓어오르면 중불로 줄이고 고기를 넣어 40분간 삶습니다.",
            "5단계 (뜸들이기 - 20분): 불을 끄고 뚜껑을 덮은 채로 20분간 뜸을 들입니다.",
            "6단계 (건조 및 보관): 고기를 건져 상온에서 겉면을 말린 뒤 진공 포장하여 보관합니다."
        ],
        "caution": "중불 40분 삶기와 20분 뜸들이기 시간을 지키지 않으면 고기가 줄어들어 실제 사용 가능한 양이 크게 줄거나 고기가 퍽퍽해집니다."
    },
    "2. 가브리보쌈 메뉴별 제공 중량 기준": {
        "category": "보쌈/핵심손질",
        "updated": "개정일: 25.10.28",
        "summary": "점심 정식·칼국수 고기 고명·저녁 보쌈 메뉴별 정량 제공 기준",
        "specs": [
            "점심 보쌈정식 (일반): 120g 정량 제공",
            "점심 보쌈정식 (특): 170g 정량 제공",
            "한우사골칼국수 고기 고명: 2~3점 (큰 고기는 2점 / 작은 고기는 3점)",
            "저녁 가브리김치보쌈 (소): 300g 정량 제공",
            "저녁 가브리김치보쌈 (중): 400g 정량 제공",
            "보쌈 고기 추가 (단품): 200g 정량 제공"
        ],
        "steps": [
            "1단계: 고기를 썰 때 반드시 전자저울 위에 접시(또는 종이호일)를 올리고 영점(0g)을 맞춥니다.",
            "2단계: 메뉴별 정량(120g / 170g / 300g / 400g)을 정확히 달아서 나갑니다."
        ],
        "caution": "눈대중으로 고기를 썰어 정량보다 20~30g씩 더 나가면 월말 고기 원가가 크게 치솟으므로 반드시 저울로 달아서 제공해 주세요."
    },
    "3. 매콤알곤이볶음 (저녁 메인 조리법)": {
        "category": "메인요리",
        "updated": "개정일: 26.01.21",
        "summary": "통돌이 자동 볶음기 조리 순서(총 4분) 및 1·2차 재료 정량 투입법",
        "specs": [
            "1차 투입 재료: 고추기름 30g(3바퀴), 간마늘 30g, 삶은 알 180g, 삶은 곤이 360g, 고추 40g + 대파 40g(합 80g), 생콩나물 300g(성인 남성 한 주먹), 사골육수 200g(국자 1샥구)",
            "2차 투입 재료: 볶음분말 100g(계량스푼 2스푼), 참기름 2바퀴"
        ],
        "steps": [
            "1단계 (초벌 볶음 - 2분): 1차 재료(고추기름~사골육수 200g)를 모두 넣고 통돌이 기계에서 2분간 조리합니다.",
            "2단계 (양념 배합 - 1분 30초): 볶음분말 100g과 참기름 2바퀴를 넣고 1분 30초간 더 볶습니다.",
            "3단계 (불향 입히기 - 30초): 직화로 30초간 불향을 입힌 뒤 뜨겁게 달군 돌불판에 담아 제공합니다."
        ],
        "caution": "콩나물(300g)과 사골육수(200g) 정량을 지켜야 완성 후 국물 농도와 짠맛이 일정하게 유지됩니다."
    },
    "4. 매콤알곤이볶음 맵기 조절 (보통맛·매운맛)": {
        "category": "메인요리",
        "updated": "개정일: 25.12.23",
        "summary": "2단계 맵기(보통맛 / 매운맛) 선택에 따른 캡사이신 정량 투입법",
        "specs": [
            "보통맛 선택 시: 캡사이신을 넣지 않고 기본 조리법대로 진행",
            "매운맛 선택 시: 조리 완료 직전 캡사이신 액상 5~6g 투입 (소형 계량스푼 '5' 눈금선까지 1스푼)"
        ],
        "steps": [
            "1단계: 주문서에서 보통맛 / 매운맛 여부를 먼저 확인합니다.",
            "2단계: 매운맛 주문 시에만 2차 분말 투입 단계 또는 조리 완료 후 소형 스푼 '5' 표기선 맞춰 1스푼(5~6g)을 넣고 골고루 섞어줍니다."
        ],
        "caution": "캡사이신 액상은 소량만 더 들어가도 지나치게 매워지므로 반드시 전용 소형 계량스푼 눈금 '5'를 지켜주세요."
    },
    "5. 알곤이 칼국수 & 전골 토핑 정량 기준": {
        "category": "점심/전골",
        "updated": "개정일: 26.04.20",
        "summary": "점심 얼큰 알곤이 칼국수(1인) 및 전골(2인·3인) 해산물·면·콩나물 정량",
        "specs": [
            "점심 칼국수 1인분 기준: 삶은 알 50g + 삶은 곤이 120g",
            "전골 2인분 기준: 삶은 알 100g + 삶은 곤이 240g + 콩나물 120g + 칼국수면 400g(2개)",
            "전골 3인분 기준: 삶은 알 150g + 삶은 곤이 360g + 콩나물 180g + 칼국수면 600g(3개)"
        ],
        "steps": [
            "1단계: 염도 0.85%로 맞춘 사골육수에 얼큰다대기를 정량 풀어줍니다.",
            "2단계: 미리 인분별로 소분해 둔 삶은 알·곤이와 콩나물, 칼국수면을 정량대로 넣어 조리합니다."
        ],
        "caution": "바쁜 점심시간에 알·곤이를 눈대중으로 집어 넣으면 해산물 원가가 급증하므로 반드시 소분 용기에 미리 계량해 두세요."
    },
    "6. 알곤이 사전 찌기 및 냉장 보관법": {
        "category": "보쌈/핵심손질",
        "updated": "개정일: 25.10.28",
        "summary": "냉동 알·곤이 해동 후 찜기 50분 조리 및 소분 박스 보관 기준",
        "specs": [
            "1회 소분 박스 구성 기준: 알 3개 + 곤이 6개 (낱개 소분 박스 단위)",
            "찜기 조리 시간: 물이 끓어오른 후 뚜껑 덮고 중불 50분"
        ],
        "steps": [
            "1단계: 찜탕기에 물을 붓고 강불로 끓입니다.",
            "2단계: 물이 끓어오르면 해동된 알과 곤이를 찜기에 올립니다.",
            "3단계: 뚜껑을 덮고 중불로 줄여 50분 동안 충분히 쪄줍니다.",
            "4단계: 쪄낸 알과 곤이를 상온에서 넓게 펴서 식히며 수분을 날려준 뒤 바트에 담아 냉장 보관합니다."
        ],
        "caution": "충분히 식히지 않고 뜨거운 상태로 뚜껑을 닫아 냉장고에 넣으면 수분이 차서 쉽게 상할 수 있습니다."
    },
    "7. 알곤이 치즈 파스타 (면 삶기 및 소분)": {
        "category": "사이드/별미",
        "updated": "개정일: 26.01.04",
        "summary": "파스타면 7인분(1봉 500g) 사전 삶기 및 150g 단위 소분 보관법",
        "specs": [
            "7인분 사전 삶기 재료: 물 4,000ml + 건조 파스타면 500g(1봉) + 식용유 50g(1국자)",
            "1인분 소분 중량: 삶은 파스타면 150g씩 위생백 소분 (총 7봉지 완성)",
            "냉장 보관 기한: 5일 이내 사용 권장 (최대 7일)"
        ],
        "steps": [
            "1단계 (삶기 - 7분): 물 4,000ml가 끓기 시작하면 면 500g을 넣고 바닥에 눌어붙지 않게 저어가며 7분간 삶습니다.",
            "2단계 (식히기): 넓은 쟁반에 면을 옮기고 식용유 50g(1국자)을 넣어 골고루 버무린 뒤 넓게 펼쳐 식힙니다.",
            "3단계 (소분): 면이 완전히 식으면 위생백에 150g씩 정확히 달아 소분 후 냉장 보관합니다."
        ],
        "caution": "삶은 면은 최대 보관 기한(5~7일)을 넘기면 식감이 뚝 끊어지므로 예상 판매량에 맞춰 삶아주세요."
    },
    "8. 알곤이 치즈 파스타 (본조리 및 토치 마무리)": {
        "category": "사이드/별미",
        "updated": "개정일: 26.01.04",
        "summary": "남은 알곤이볶음 소스를 활용한 치즈 파스타 즉석 조리 및 제공법",
        "specs": [
            "1인분 조리 재료: 손님이 드시고 남은 알곤이 소스 + 소분 파스타면 1봉(150g) + 한우사골육수 50ml + 모짜렐라 치즈 50g"
        ],
        "steps": [
            "1단계: 팬에 남은 알곤이 소스와 파스타면 150g, 사골육수 50ml를 넣고 중불에서 면이 부드러워질 때까지 잘 저어가며 볶습니다. (남은 소스가 충분하면 사골육수는 넣지 않습니다.)",
            "2단계: 면이 부드러워지면 돌판 중앙에 볼륨감 있게 담아줍니다.",
            "3단계: 파스타 위를 치즈 50g으로 전체적으로 덮어줍니다.",
            "4단계: 토치로 치즈 겉면이 먹음직스러운 갈색이 나도록 구워 제공합니다."
        ],
        "caution": "손님 상에 나갈 때 '치즈가 소스에 잘 녹을 수 있도록 골고루 저어서 드세요'라고 안내 멘트를 꼭 해주세요."
    },
    "9. 꼬막 비빔밥": {
        "category": "점심/식사",
        "updated": "개정일: 26.06.15",
        "summary": "냉동 꼬막 100g 소분(해동 후 80g) 손질 및 정식 접시 담음새 기준",
        "specs": [
            "1인분 재료: 해동 꼬막살 80g(냉동 상태 100g 소분), 꼬막비빔장 50g(1국자), 미나리 20g, 계란지단 20g, 공깃밥 1공기(210g), 김가루 5g, 참기름 10g(2바퀴), 통깨 1g"
        ],
        "steps": [
            "사전 준비: 미나리는 잎과 얇은 줄기 위주로 4~5cm 길이로 썰고, 꼬막은 냉동 상태에서 100g씩 위생봉투에 소분합니다 (해동 후 물기 짜면 80g).",
            "1단계: 소분된 냉동 꼬막을 흐르는 찬물에 약 30초간 씻으며 해동한 뒤 물기를 꼭 짜줍니다.",
            "2단계: 정식 접시에 꼬막 80g, 미나리 20g, 계란지단 20g을 가지런히 담습니다.",
            "3단계: 꼬막 위에 꼬막비빔장 1국자(50g)를 올리고 통깨 1g을 뿌립니다.",
            "4단계: 대접(면기)에 밥 한 공기를 담고 참기름 2바퀴(10g)를 두른 뒤 김가루 5g을 올려 함께 제공합니다."
        ],
        "caution": "해동한 꼬막의 물기를 제대로 짜지 않으면 비빔장이 묽어지고 비린 맛이 날 수 있으니 물기를 꼭 짜주세요."
    },
    "10. 미나리 냉국수": {
        "category": "점심/사이드",
        "updated": "개정일: 26.04.27",
        "summary": "미나리 줄기(0.3cm 세절)와 동치미 살얼음 육수를 활용한 시원한 냉국수 조리법",
        "specs": [
            "1인분 재료: 미나리 줄기 부분 50g(0.3cm 두께로 얇게 썬 것), 동치미 냉면육수 2봉(1봉 액상 + 1봉 살얼음), 냉동소면 1개, 통깨 1g"
        ],
        "steps": [
            "1단계: 미나리는 줄기 부분만 모아 0.3cm 두께로 잘게 썰어 준비합니다.",
            "2단계: 끓는 물에 냉동소면을 넣고 1분간 삶은 뒤 찬물에 비벼 씻어 물기를 완전히 빼고 그릇에 담습니다.",
            "3단계: 동치미 냉면육수 1봉은 녹여서 붓고, 나머지 1봉은 살얼음 상태로 잘게 부숴 넣습니다.",
            "4단계: 면이 보이지 않도록 잘게 썬 미나리 줄기 50g을 소복하게 올리고 통깨 1g을 뿌려 완성합니다."
        ],
        "caution": "미나리 줄기는 냉국수에, 미나리 잎은 미나리무침에 나누어 사용하면 버리는 식자재 없이 100% 활용할 수 있습니다."
    },
    "11. 미나리 무침": {
        "category": "점심/사이드",
        "updated": "개정일: 26.04.27",
        "summary": "미나리 잎(4cm 절단)과 가브리보쌈 고기 고명을 올린 새콤달콤 무침 조리법",
        "specs": [
            "1인분 재료: 미나리 잎 위주 40g(4cm 길이), 초무침소스 10g, 삶은 가브리보쌈 35g(2~3조각), 참기름 2g, 통깨 1g"
        ],
        "steps": [
            "1단계: 미나리는 잎 부분 위주로 4cm 길이로 썰어 준비합니다.",
            "2단계: 볼에 미나리 40g, 초무침소스 10g, 참기름 2g을 넣고 숨이 죽지 않게 가볍게 버무립니다.",
            "3단계: 접시에 미나리무침을 담고 삶은 가브리보쌈 고기 35g(2~3조각)을 위에 올린 뒤 통깨 1g을 뿌려 제공합니다."
        ],
        "caution": "미리 무쳐두면 미나리에서 물이 나오고 숨이 죽으므로 반드시 주문 즉시 버무려 제공하세요."
    },
    "12. 맵불스지 (삶은 계란 & 본조리)": {
        "category": "메인요리",
        "updated": "개정일: 25.04.08",
        "summary": "12분 반숙/완숙 계란 삶기 및 자숙스지·파스타면 3분 조리법",
        "specs": [
            "1인분 재료: 삶은 소힘줄(자숙스지) 230g(1팩), 맵불스지소스 250g, 정수 물 250g, 삶은 파스타면 150g(1봉), 대파 10g, 삶은 계란 1개, 통깨 1g"
        ],
        "steps": [
            "사전 준비 (계란 삶기): 냄비에 계란이 2~3cm 잠기게 찬물을 붓고 강불로 가열 ➔ 물이 팔팔 끓으면 중불로 줄여 12분 삶기 ➔ 즉시 찬물에 담가 식힌 후 껍질 까서 냉장 보관(최대 5일).",
            "1단계: 웍(깊은 팬)에 맵불스지소스 250g과 물 250g을 넣고 끓입니다.",
            "2단계: 소스가 끓으면 스지 230g(1팩)과 삶아둔 파스타면 150g을 넣고 중불에서 3분간 잘 저어가며 끓입니다.",
            "3단계: 그릇 중앙에 파스타면을 일자로 깔고 그 위에 스지와 소스를 모두 부어줍니다.",
            "4단계: 대파 10g과 반으로 자른 삶은 계란 1개(흰자가 위로 보이게)를 올리고 통깨 1g을 뿌려 마무리합니다."
        ],
        "caution": "계란을 삶은 직후 바로 찬물에 식히지 않으면 껍질이 살에 달라붙어 깨지므로 즉시 냉수 냉각을 지켜주세요."
    },
    "13. 오징어 초무침": {
        "category": "사이드/별미",
        "updated": "개정일: 26.04.20",
        "summary": "끓는 물 30초 데친 오징어와 아삭한 야채 초무침 조리법",
        "specs": [
            "1인분 재료: 알배추 50g, 슬라이스 양파 50g, 부추 20g, 초무침소스 150g(2국자), 참기름 2바퀴, 깻잎 3장, 데친 오징어 150g(끓는 물 30초), 콩가루 약간"
        ],
        "steps": [
            "1단계: 볼에 알배추 50g, 양파 50g, 부추 20g, 초무침소스 150g(2국자), 참기름 2바퀴를 넣고 골고루 무쳐 접시에 담습니다.",
            "2단계: 무쳐낸 야채 위에 깻잎 3장을 보기 좋게 깔아줍니다.",
            "3단계: 끓는 물에 30초간 살짝 데친 오징어 150g을 깻잎 위에 올리고 고소한 콩가루를 뿌려 제공합니다."
        ],
        "caution": "오징어를 30초 이상 너무 오래 데치면 질겨지고 중량이 줄어드니 데치는 시간을 정확히 지켜주세요."
    },
    "14. 문어 슬라이스": {
        "category": "사이드/별미",
        "updated": "개정일: 26.04.20",
        "summary": "얇게 썬 문어다리와 새콤달콤 초대리밥 곁들임 플레이팅",
        "specs": [
            "1인분 재료: 자숙문어다리 1개, 초대리밥 220g(공깃밥 1공기 + 초대리 30g), 레몬 조각(웨지) 1개, 기름장 15g, 초장 20g, 생와사비 5g, 통깨 1g"
        ],
        "steps": [
            "1단계: 해동된 자숙문어다리 1개를 결 반대 방향으로 얇게 어슷썰기합니다.",
            "2단계: 따뜻한 밥 1공기에 초대리 30g을 섞어 초대리밥(220g)을 만듭니다.",
            "3단계: 접시에 초대리밥과 얇게 썬 문어를 가지런히 담고 레몬 조각, 기름장(15g), 초장(20g), 와사비(5g), 통깨(1g)를 곁들여 제공합니다."
        ],
        "caution": "문어를 너무 두껍게 썰면 식감이 질기고 접시가 비어 보이므로 최대한 얇고 넓게 썰어 담아주세요."
    },
    "15. 부추 호박전": {
        "category": "사이드/별미",
        "updated": "개정일: 25.03.18",
        "summary": "애호박 고명이 위로 보이게 굽는 바삭한 부추 호박전 조리법",
        "specs": [
            "1인분 재료: 부추전 반죽 1개(1인분 포션), 채 썬 애호박 40g, 식용유 30g"
        ],
        "steps": [
            "1단계: 프라이팬에 식용유 30g을 두르고 중불에서 부추전 반죽을 얇고 둥글게 먼저 펼쳐줍니다.",
            "2단계: 반죽 위로 준비된 애호박 40g을 골고루 올립니다.",
            "3단계: 아랫면이 충분히 노릇하고 바삭해지면 뒤집어서 반대쪽도 똑같이 바삭하게 구워줍니다.",
            "4단계: 전이 다 익으면 애호박이 보이는 면이 위로 향하게 접시에 담아 제공합니다."
        ],
        "caution": "불이 너무 세면 속은 안 익고 겉만 타므로 중불을 유지해 양면을 바삭하게 구워주세요."
    },
    "16. 오이탕탕이": {
        "category": "사이드/별미",
        "updated": "개정일: 26.06.15",
        "summary": "칼 대신 위생비닐과 접시로 안전하게 부숴 만드는 즉석 오이탕탕이",
        "specs": [
            "1인분 재료: 생오이 200g(1개), 오이탕탕이 소스 15g(2스푼), 통깨 1g"
        ],
        "steps": [
            "1단계: 깨끗이 씻은 오이 1개(200g)를 3~4등분하여 위생비닐 안에 넣습니다.",
            "2단계: 접시(단단한 오이는 칼갈이 봉으로 살짝 친 후 접시)를 이용해 힘 있게 눌러 오이를 골고루 부숴줍니다.",
            "3단계: 부서진 오이를 볼에 담고 손으로 먹기 좋은 크기로 찢어줍니다.",
            "4단계: 오이탕탕이 소스 2스푼(15g)을 넣고 양념이 잘 배도록 버무린 뒤 그릇에 담고 통깨 1g을 뿌려 제공합니다."
        ],
        "caution": "칼등으로 오이를 내리치면 칼이 미끄러져 손을 다칠 위험이 크므로 반드시 위생비닐과 접시를 사용해 눌러 부숴주세요."
    },
    "17. 백사골육수 제조 및 염도 맞추기 (0.85%)": {
        "category": "소분/육수/소스",
        "updated": "개정일: 26.05.12",
        "summary": "사골칼국수 23그릇 분량 백사골육수 배합 및 필수 염도(0.85%) 관리",
        "specs": [
            "배합 기준 (23그릇 분량): 진한백사골육수 농축액 2kg(1봉) + 정수 물 17kg",
            "필수 목표 염도: 0.85% (끓이기 전·후 2회 측정 필수)"
        ],
        "steps": [
            "1단계: 육수통에 전용 주걱의 '사골 눈금선'에 맞춰 정수 물(17kg)을 채웁니다.",
            "2단계: 진한백사골육수 1봉(2kg)을 모두 넣고 농축액이 잘 풀리도록 한소끔 끓여줍니다.",
            "3단계: 디지털 염도계를 사용하여 끓이기 전과 끓인 후 염도를 측정하고 정확히 0.85%로 맞춥니다. (염도가 높으면 물을 조금씩 추가해 맞춥니다.)"
        ],
        "caution": "육수가 졸아들면서 짠맛이 강해질 수 있으므로 영업 중에도 수시로 염도 0.85%를 확인해 주세요."
    },
    "18. 해물탕육수 제조 및 염도 맞추기 (0.88%)": {
        "category": "소분/육수/소스",
        "updated": "개정일: 26.05.12",
        "summary": "해물칼국수 14그릇 분량 해물탕육수 배합 및 필수 염도(0.88%) 관리",
        "specs": [
            "배합 기준 (14그릇 분량): 해물농축액 1L + 정수 물 20L",
            "필수 목표 염도: 0.88%"
        ],
        "steps": [
            "1단계: 육수통에 전용 주걱의 '해물 눈금선'에 맞춰 정수 물(20L)을 채웁니다.",
            "2단계: 계량컵(비커)에 해물농축액 1L를 정확히 계량해 넣고 바닥까지 잘 저어 섞어줍니다.",
            "3단계: 염도계로 측정하여 염도 0.88%를 맞춥니다. (염도가 높을 시 물을 추가해 조절합니다.)"
        ],
        "caution": "농축액이 바닥에 가라앉지 않도록 위아래로 충분히 저은 뒤 염도를 측정해야 정확합니다."
    },
    "19. 김치속 (겉절이·보쌈김치 양념) 대량 배합": {
        "category": "소분/육수/소스",
        "updated": "개정일: 26.02.28",
        "summary": "김치속 1배합 · 5배합(1박스) · 10배합 정확한 계량 기준표",
        "specs": [
            "1배합 기준: 김치속 1봉지 + 새우젓 100g + 까나리액젓 100g + 다진마늘 50g + 물엿 250g + 설탕 50g + 미원 10g",
            "5배합(1박스) 기준: 김치속 5봉지 + 새우젓 500g + 까나리액젓 500g + 다진마늘 250g + 물엿 1,250g + 설탕 250g + 미원 50g",
            "10배합 기준: 김치속 10봉지 + 새우젓 1,000g(1통) + 까나리액젓 1,000g + 다진마늘 500g + 물엿 2,500g + 설탕 500g + 미원 100g"
        ],
        "steps": [
            "1단계: 작업할 배수(1배 / 5배 / 10배)에 맞춰 모든 양념 재료를 전자저울로 정확히 계량합니다.",
            "2단계: 대형 믹싱볼에 모든 재료를 넣고 설탕과 물엿이 완전히 녹아 어우러지도록 골고루 섞어 냉장 보관합니다."
        ],
        "caution": "새우젓과 액젓이 바닥에 뭉치지 않도록 주걱으로 바닥까지 긁어가며 고르게 섞어주세요."
    },
    "20. 얼큰다대기 제조 및 숙성법": {
        "category": "소분/육수/소스",
        "updated": "개정일: 26.01.28",
        "summary": "끓인 식용유로 고추기름을 내어 하루 냉장 숙성하는 얼큰다대기 제조법",
        "specs": [
            "1회 배합 재료: 얼큰칼국수 다대기분말 3,000g(3팩) + 후추 60g + 굴소스 360g + 다진마늘 500g + 다진생강 200g + 끓인 식용유 450g"
        ],
        "steps": [
            "1단계: 넓은 스텐 볼에 식용유를 제외한 모든 재료(분말 3,000g, 후추 60g, 굴소스 360g, 마늘 500g, 생강 200g)를 넣고 골고루 섞습니다.",
            "2단계: 별도 냄비에서 뜨겁게 끓인 식용유 450g을 분말 위에 부어 고추기름을 내며 재빨리 섞어줍니다.",
            "3단계: 완성된 다대기는 바트에 담아 냉장고에서 하루 동안 숙성한 뒤 사용합니다."
        ],
        "caution": "뜨거운 식용유를 부을 때 거품이 올라오니 화상에 절대 주의하시고, 깊은 맛을 위해 소진 전날 미리 만들어 하루 숙성해 주세요."
    },
    "21. 해물칼국수 다대기 제조법": {
        "category": "소분/육수/소스",
        "updated": "개정일: 26.01.28",
        "summary": "다진 고추지와 숙성 얼큰다대기를 배합하는 해물칼국수 전용 다대기",
        "specs": [
            "1회 배합 재료: 절인 고추지 건더기 1,000g(2팩) + 고추지 국물 400g + 후추 50g + 숙성 얼큰칼국수 다대기 1,500g"
        ],
        "steps": [
            "1단계: 고추지 2팩에서 건더기(1,000g)와 절인 국물(400g)을 분리한 뒤, 고추지 건더기를 잘게 다져줍니다.",
            "2단계: 볼에 후추 50g과 고추지 국물 400g을 먼저 넣고 섞어 후추가 뭉치지 않게 풀어줍니다.",
            "3단계: 조리용 믹싱볼에 얼큰다대기 1,500g, 다진 고추지 1,000g, 후추 푼 고추지 국물을 순서대로 넣고 골고루 섞어 냉장 보관합니다."
        ],
        "caution": "후추를 가루째 바로 다대기에 넣으면 뭉치므로 반드시 고추지 국물에 먼저 풀어준 뒤 섞어주세요."
    },
    "22. 간장·새우젓·쌈장 소스 4종 배합법": {
        "category": "소분/육수/소스",
        "updated": "개정일: 26.01.02",
        "summary": "알곤이간장 · 전/만두간장 · 보쌈용 새우젓 · 사이다 쌈장 표준 배합비",
        "specs": [
            "[알곤이 간장]: 진간장 500g + 식초 300g + 설탕 130g + 정수 물 230g",
            "[전 / 만두 간장]: 진간장 600g + 식초 400g + 설탕 100g + 정수 물 200g + 고춧가루 10g + 참기름 20g + 참깨 10g",
            "[보쌈 새우젓]: 새우젓 1통 + 사이다 450g + 설탕 25g + 고춧가루 30g",
            "[보쌈 쌈장]: 쌈장 말통 1통 + 사이다 1통"
        ],
        "steps": [
            "1단계: 각 소스별 정량을 계량하여 바닥의 설탕이나 쌈장이 완전히 풀릴 때까지 고르게 저어줍니다.",
            "2단계: 소스 통에 라벨(제조일)을 붙여 냉장 보관하며 선입선출로 사용합니다."
        ],
        "caution": "전/만두 간장과 새우젓은 나가기 전 위아래로 한 번 저어주어야 고춧가루와 참깨가 균일하게 담깁니다."
    },
    "23. 배추 & 알배추 절이기 (소금물 재사용)": {
        "category": "보쌈/핵심손질",
        "updated": "개정일: 26.01.21",
        "summary": "대형용기 배추 3통 절임 후 남은 소금물을 알배추 2박스 절임에 재사용하는 원가 절감법",
        "specs": [
            "소금물 제조 (대형용기 기준): 바닥에서 전용 주걱 검정 표시선까지 물 + 천일염 1/6바트 가득 6통",
            "절임물 목표 염도: 평시 6.0% 이상 (겨울철 8.0%)",
            "1회 작업량: 일반 배추 3통 절임 ➔ 건져낸 후 같은 소금물에 알배추 2박스 절임"
        ],
        "steps": [
            "1단계: 대형용기에 주걱 표시선까지 물을 받고 천일염 6통(1/6바트 기준)을 녹여 염도 6.0%(겨울 8.0%)를 맞춥니다.",
            "2단계: 배추 3통을 넣고 약 3시간 동안 절인 뒤 건져냅니다.",
            "3단계: 배추를 건져낸 소금물을 버리지 않고 그대로 알배추 2박스를 넣어 절이는 데 재사용합니다."
        ],
        "caution": "배추 절임 후 소금물을 매번 버리면 천일염과 수도 요금 낭비가 크므로 반드시 알배추 작업까지 2회 연속 사용하세요."
    },
    "24. 굴 세척 작업 및 이물질 확인": {
        "category": "보쌈/핵심손질",
        "updated": "개정일: 25.11.13",
        "summary": "손의 열기가 닿지 않게 소쿠리로 9~10회 헹궈 껍데기·갯지렁이를 제거하는 위생 수칙",
        "specs": [
            "세척 도구: 구멍 뚫린 스텐 소쿠리 + 찬물",
            "세척 횟수: 찬물에 9~10회 흔들어 헹굼"
        ],
        "steps": [
            "1단계: 굴을 소쿠리에 담고 찬물에 담가 소쿠리를 흔들어가며 9~10회 깨끗이 헹궈 물기를 뺍니다.",
            "2단계: 세척 중 맨손이나 손의 열기가 굴에 직접 닿지 않도록 주의하여 신선도를 유지합니다.",
            "3단계: 굴 사이사이에 붙어 있는 굴 껍데기 조각과 갯지렁이 등 이물질을 눈으로 꼼꼼히 찾아 제거합니다."
        ],
        "caution": "굴에서 껍데기나 갯지렁이가 나오면 심각한 고객 불만으로 이어지므로 세척 단계에서 반드시 철저히 골라내야 합니다."
    },
    "25. 굴 3.0% 소금물 소분 및 얼음물 보관": {
        "category": "보쌈/핵심손질",
        "updated": "개정일: 25.11.13",
        "summary": "염도 3.0% 소금물과 굴을 200g씩 동량 포장하여 얼음물 바트에 보관하는 방법",
        "specs": [
            "보관용 소금물 배합: 물 2,000ml + 천일염 70g (염도계 측정 3.0% 필수 준수)",
            "1봉지 소분 기준: 세척한 굴 200g + 3.0% 소금물 200g",
            "보관 기한: 얼음물 바트 내 최대 3일 (매일 마감 시 얼음물 교체 필수)"
        ],
        "steps": [
            "1단계: 물 2,000ml에 천일염 70g을 녹여 염도 3.0% 소금물을 만듭니다.",
            "2단계: 위생백에 세척한 굴 200g과 소금물 200g을 함께 넣어 묶어줍니다.",
            "3단계: 소분한 굴 봉지들이 완전히 잠기도록 깊은 바트에 얼음물을 채워 냉장 보관합니다 (마감 시마다 새 얼음물로 교체).",
            "4단계: 손님 제공 시 봉지에서 굴을 꺼내 찬물로 3~4회 가볍게 헹군 뒤 물기를 빼서 나갑니다."
        ],
        "caution": "맹물에 보관하면 굴이 불어서 맛과 향이 다 빠지므로 반드시 3.0% 소금물에 담가 얼음물 바트에 보관하세요."
    },
    "26. (기본반찬) 어묵볶음": {
        "category": "반찬/국",
        "updated": "개정일: 25.12.17",
        "summary": "사각어묵 2봉지 기준 간장 양념 조림 표준 레시피",
        "specs": [
            "재료 (사각어묵 2봉지 기준): 물 300g, 몽고간장 100g, 양파 75g, 미림 25g, 설탕 25g, 대파 25g, 고운고춧가루 7g, 청양고춧가루 5g, 미원 5g"
        ],
        "steps": [
            "1단계: 사각어묵 2봉지를 먹기 좋은 사각 모양으로 썰어줍니다.",
            "2단계: 분량의 양념 재료(물 300g, 간장 100g, 미림 25g, 설탕 25g, 고춧가루, 미원)를 섞어 양념장을 만듭니다.",
            "3단계: 팬에 어묵, 채 썬 양파(75g), 대파(25g), 양념장 순서로 넣고 약불에서 윤기 나게 졸여줍니다."
        ],
        "caution": "센 불에서 볶으면 양념이 금방 타버리고 어묵이 딱딱해지니 약불에서 천천히 졸여주세요."
    },
    "27. (기본반찬) 콩나물무침": {
        "category": "반찬/국",
        "updated": "개정일: 25.10.28",
        "summary": "콩나물 2kg 기준 뚜껑 닫고 센 불 5분 삶기 및 아삭한 양념 무침법",
        "specs": [
            "삶기 재료: 물 3,000g + 콩나물 2kg",
            "무침 양념 (콩나물 2kg 기준): 다진마늘 70g, 대파 80g, 꽃소금 20g, 소고기다시다 8g, 미원 2g, 참기름 적당량"
        ],
        "steps": [
            "1단계: 냄비에 물 3,000g과 콩나물 2kg을 넣고 끓입니다.",
            "2단계: 물이 끓어오르면 뚜껑을 닫은 채로 정확히 5분간 센 불로 끓입니다.",
            "3단계: 삶아진 콩나물을 즉시 흐르는 찬물에 씻어 열기를 빼고 물기를 충분히 털어냅니다.",
            "4단계: 분량의 무침 양념(마늘 70g, 꽃소금 20g, 다시다 8g, 미원 2g, 대파 80g, 참기름)을 넣고 가볍게 버무려 완성합니다."
        ],
        "caution": "삶는 도중 뚜껑을 열면 콩나물 비린내가 날 수 있으니 5분 동안 뚜껑을 열지 마세요."
    },
    "28. (기본반찬) 소세지볶음": {
        "category": "반찬/국",
        "updated": "개정일: 26.04.30",
        "summary": "점심 매출 100만 원 기준 통돌이 기계를 활용한 비엔나소세지 케첩 볶음",
        "specs": [
            "재료 (점심 매출 100만 원 기준): 칼집 비엔나소세지 2kg, 고추기름 50g(4바퀴), 다진마늘 30g, 양파 200g, 대파 50g, 케첩 200g, 굴소스 50g, 미원 15g"
        ],
        "steps": [
            "1단계: 통돌이 기계에 고추기름 50g(4바퀴)과 다진마늘 30g을 넣고 마늘 향이 올라올 때까지 볶아줍니다.",
            "2단계: 칼집 비엔나소세지 2kg을 넣고 소세지 칼집이 예쁘게 벌어질 때까지 볶습니다.",
            "3단계: 케첩 200g, 굴소스 50g, 미원 15g, 양파 200g, 대파 50g을 모두 넣고 2분간 더 볶아 마무리합니다."
        ],
        "caution": "매장 일일 예상 점심 매출 규모에 맞춰 조리량을 절반(0.5배) 또는 1배로 조절하여 남아서 버리는 반찬을 줄여주세요."
    },
    "29. (기본반찬) 콩나물국": {
        "category": "반찬/국",
        "updated": "개정일: 26.04.30",
        "summary": "점심 매출 100만 원 기준 끓이기 전(0.65%)·후(0.85%) 염도 맞춤 콩나물국",
        "specs": [
            "재료 (점심 매출 100만 원 기준): 물 12L, 해물농축액 500ml, 콩나물 1kg, 대파 200g, 다진마늘 60g(2큰술)",
            "필수 염도 기준: 끓이기 전 염도 0.65% ➔ 끓인 후 완성 염도 0.85%"
        ],
        "steps": [
            "1단계: 냄비에 물 12L, 해물농축액 500ml, 콩나물 1kg을 넣고 끓이기 전 염도가 0.65%인지 확인한 뒤 끓여줍니다.",
            "2단계: 콩나물이 익으면 대파 200g과 다진마늘 60g(2큰술)을 넣고 한소끔 더 끓입니다.",
            "3단계: 마무리 후 염도계로 측정하여 완성 염도 0.85%를 맞춰 제공합니다."
        ],
        "caution": "콩나물국은 끓이기 전(0.65%)과 끓인 후(0.85%) 두 번 염도를 확인해야 언제나 시원하고 일정한 간이 유지됩니다."
    }
}

# ==============================================================================
# 3. 사진 업로드 및 미리보기 공통 함수 (1칸씩 생성)
# ==============================================================================
def render_photo_uploader(item_key_name, title_label="완성 요리 / 조리 기준 사진"):
    safe_key = "".join([c if c.isalnum() else "_" for c in item_key_name])
    saved_path_jpg = os.path.join(PHOTO_DIR, f"{safe_key}.png")

    st.markdown(f"""
    <div class="sj-card" style="padding:14px 16px;">
        <div style="font-weight:800; font-size:14px; color:#1A1817; margin-bottom:8px;">📸 {title_label}</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        f"'{item_key_name}' 사진 업로드 (JPG/PNG)",
        type=["png", "jpg", "jpeg", "webp"],
        key=f"up_{safe_key}",
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        img_bytes = uploaded_file.getvalue()
        with open(saved_path_jpg, "wb") as f:
            f.write(img_bytes)
        st.session_state[f"photo_{safe_key}"] = img_bytes

    if f"photo_{safe_key}" in st.session_state:
        st.image(st.session_state[f"photo_{safe_key}"], caption=f"[{item_key_name}] 등록 사진", use_container_width=True)
    elif os.path.exists(saved_path_jpg):
        st.image(saved_path_jpg, caption=f"[{item_key_name}] 등록 사진", use_container_width=True)
    else:
        st.markdown("""
        <div class="sj-photo-placeholder">
            📷 <b>[Browse files]</b> 버튼을 눌러<br>사진 1장을 업로드해 보세요.<br>
            <span style="font-size:11.5px; color:#8C1D18;">(업로드 즉시 아래에 크게 표시됩니다)</span>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# 4. 실시간 엑셀 원가 연동 엔진 (cost_data.xlsx 및 logo.jpg 완벽 대응)
# ==============================================================================
@st.cache_data
def load_and_recalculate_all():
    candidates = [
        "cost_data.xlsx",
        "손정보쌈_원가계산_가나다순정리_소분카드정렬_판매가반영.xlsx",
        "손정보쌈_원가계산_가나다순정리_소분카드정렬_판매가반영_2.xlsx",
        "손정보쌈_원가계산_레시피입력완성.xlsx"
    ]
    file_path = None
    for c in candidates:
        if os.path.exists(c):
            file_path = c
            break
    if file_path is None:
        st.error("엑셀 데이터 파일(cost_data.xlsx)을 찾을 수 없습니다. 폴더 내 파일명을 확인해 주세요.")
        st.stop()

    # 1) 식재료 마스터 DB (Sheet 01)
    df_db_full = pd.read_excel(file_path, sheet_name="01_식재료마스터DB", skiprows=3)
    df_raw = df_db_full.iloc[:150, :9].copy()
    df_raw.columns = ["품목코드", "분류", "식재료명", "구매총중량", "구매가격", "손질수율", "실사용중량", "1g당실원가", "비고"]
    df_raw = df_raw.dropna(subset=["식재료명"]).copy()
    for col in ["구매총중량", "구매가격", "손질수율"]:
        df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce").fillna(0.0)
    df_raw["손질수율"] = np.where(df_raw["손질수율"] <= 0, 1.0, df_raw["손질수율"])
    df_raw["실사용중량"] = df_raw["구매총중량"] * df_raw["손질수율"]
    df_raw["1g당실원가"] = np.where(df_raw["실사용중량"] > 0, df_raw["구매가격"] / df_raw["실사용중량"], 0.0)
    df_raw["품목코드"] = [f"식자재-{i+1:03d}" for i in range(len(df_raw))]

    unit_cost_map = dict(zip(df_raw["식재료명"].str.strip(), df_raw["1g당실원가"]))
    code_map = dict(zip(df_raw["식재료명"].str.strip(), df_raw["품목코드"]))
    raw_cat_map = dict(zip(df_raw["식재료명"].str.strip(), df_raw["분류"]))

    # 2) 소분 및 배합 레시피 (Sheet 02)
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
        p_code = f"소분-{i+1:02d}"
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
            "실사용비율(%)": yield_rate * 100.0,
            "최종완성중량(g)": final_w,
            "1회배합총원가(원)": total_c,
            "1g당실원가(원)": unit_c,
            "100g당원가(원)": unit_c * 100.0,
            "메모": memo
        })
        sobun_items_dict[s_name] = items

    df_sobun = pd.DataFrame(sobun_list)

    # 3) 메뉴별 원가계산서 (Sheet 03)
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
                gubun = "매장소분/양념" if ing in sobun_cat_ratios else raw_cat_map.get(ing, "기타")
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
                    "구분": "확인필요",
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
            "판매가확정여부": "확정" if is_confirmed else "예상가",
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

# 9대 고정비 세션 세팅
DEFAULT_FIXED_COSTS = {
    "고정비 1. 임대료 및 관리비 (월세·상가관리비 포함)": 550000,
    "고정비 2. 인건비 (주방·홀 직원 및 알바 총액)": 3200000,
    "고정비 3. 수도 / 광열비 (매장 가스·전기·수도세)": 300000,
    "고정비 4. 기타 고정비 (세무기장·통신·포스기·방역)": 150000,
    "고정비 5. 예비비 / 기타 소모품 (세제·화장지·일회용품)": 100000,
    "고정비 6. 렌탈비용 (제빙기·정수기·키오스크 등)": 50000,
    "고정비 7. 대출 이자 및 원리금 (창업대출 등)": 30000,
    "고정비 8. 보험료 (화재보험·배상책임보험 등)": 50000,
    "고정비 9. 부대비용 (4대보험·퇴직연금 등)": 500000,
}
for fk, fv in DEFAULT_FIXED_COSTS.items():
    if fk not in st.session_state:
        st.session_state[fk] = fv

# ==============================================================================
# 5. 사이드바 로고(logo.jpg) 및 메뉴 이동
# ==============================================================================
with st.sidebar:
    logo_candidates = ["logo.jpg", "손정보쌈로고 세로형.jpg", "손정보쌈로고 세로형_2.jpg", "logo.png"]
    logo_loaded = False
    for lc in logo_candidates:
        if os.path.exists(lc):
            st.image(lc, use_container_width=True)
            logo_loaded = True
            break
    if not logo_loaded:
        st.markdown("""
        <div style='background:#1A1817; padding:18px; border-radius:12px; border:2px solid #CB994F; text-align:center; margin-bottom:12px;'>
            <div style='color:#CB994F; font-size:14px; font-weight:800; letter-spacing:2px;'>手 : 정 (손정)</div>
            <div style='color:#FFFFFF; font-size:24px; font-weight:900; margin-top:4px;'>손 정 보 쌈</div>
            <div style='color:#D8CFC4; font-size:11px; margin-top:4px;'>정성을 다하는 손맛 · 가맹점 통합 포털</div>
        </div>
        """, unsafe_allow_html=True)

    selected_branch = st.selectbox(
        "🏪 관리 대상 가맹점 선택",
        ["본사 표준 모델 (전체)", "당산역점", "가산디지털단지역점", "강서구청점", "은평이마트점", "종로점", "울산명촌점", "과천점"]
    )
    st.markdown("---")
    nav = st.radio(
        "📂 통합 관리 메뉴",
        [
            "📋 1. 원클릭 레시피 & 조리 매뉴얼",
            "🥩 2. 메뉴별 원가 & 식자재 단가표",
            "🔍 3. 실매출 · 원가 · 고정비 통합 진단",
            "💰 4. 매장 월간 순수익 상세 시뮬레이터"
        ]
    )
    st.markdown("---")
    st.caption("© 2026 (주)육성푸드 손정보쌈 본사 | 가맹점 통합 관리 포털")

# 상단 배너 ('手:정 (손정)')
st.markdown(f"""
<div class="sj-hero">
    <div style="min-width:0; width:100%;">
        <div class="sj-hero-badge">手:정 (손정) · SONJEONG BOSSAM FRANCHISE PORTAL</div>
        <h1 class="sj-hero-title">손정보쌈 가맹점 원가 · 레시피 · 실매출 손익 통합 진단 포털</h1>
        <div class="sj-hero-sub">현재 선택 지점: <b>{selected_branch}</b> | 천 단위 콤마(,) 적용 · 개별 메뉴 사진 등록 · 9대 고정비 반영</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 카테고리 1: 📋 원클릭 레시피 & 조리 매뉴얼 (개별 분리 + 사진 업로드 + 1~10배합)
# ==============================================================================
if nav == "📋 1. 원클릭 레시피 & 조리 매뉴얼":
    t_m1, t_m2, t_m3 = st.tabs([
        "📖 주방 조리 매뉴얼 (29개 항목 개별 보기 + 사진 등록)",
        "🍲 메뉴별 1인분 정량 레시피 (20종 개별 보기 + 사진 등록)",
        "🧪 소분·육수·양념 멀티 배합기 (1배~10배 단위 선택)"
    ])

    with t_m1:
        st.markdown("#### 📖 조리 매뉴얼을 메뉴별로 하나씩 선택해 확인하고, 우측에 완성/조리 사진을 1장씩 등록하세요")
        cat_filter = st.radio(
            "📂 매뉴얼 분류 선택",
            ["전체 (29개)", "보쌈/핵심손질", "메인요리", "점심/전골", "점심/식사", "점심/사이드", "사이드/별미", "소분/육수/소스", "반찬/국"],
            horizontal=True
        )
        filtered_keys = [
            k for k, v in MANUAL_DB.items()
            if cat_filter == "전체 (29개)" or v["category"] == cat_filter
        ]

        c_select, c_view = st.columns([1.05, 2.35])
        with c_select:
            sel_k = st.radio(
                "📌 확인할 메뉴/작업 매뉴얼을 하나씩 선택하세요",
                filtered_keys,
                key="manual_single_selector"
            )

        with c_view:
            m_data = MANUAL_DB[sel_k]
            st.markdown(f"""
            <div class="sj-card-gold">
                <div class="sj-nowrap-header">
                    <div class="sj-menu-title-wrap">
                        <span class="sj-tag">{m_data['category']}</span>
                        <span class="sj-menu-name" style="font-size:20px;">{sel_k}</span>
                    </div>
                    <span class="sj-tag">{m_data['updated']}</span>
                </div>
                <p style="color:#5C4938; font-weight:600; margin-top:8px; margin-bottom:0;">{m_data['summary']}</p>
            </div>
            """, unsafe_allow_html=True)

            col_recipe_info, col_photo_box = st.columns([1.45, 1])
            with col_recipe_info:
                specs_html = "".join([f"<li style='margin-bottom:8px; font-weight:600;'>{s}</li>" for s in m_data["specs"]])
                st.markdown(f"""
                <div class="sj-card">
                    <h4 style="color:#8C1D18; margin-top:0;">⚖️ 핵심 정량 · 배합 · 염도 기준</h4>
                    <ul style="padding-left:20px; margin-bottom:0; line-height:1.6;">{specs_html}</ul>
                </div>
                """, unsafe_allow_html=True)

                steps_html = "".join([
                    f"<div style='padding:10px 12px; background:#FAF7F2; border-radius:8px; margin-bottom:8px; border-left:4px solid #CB994F; font-weight:600;'>{st_txt}</div>"
                    for st_txt in m_data["steps"]
                ])
                st.markdown(f"""
                <div class="sj-card">
                    <h4 style="color:#1A1817; margin-top:0;">⏱️ 표준 조리 순서 & 시간</h4>
                    {steps_html}
                </div>
                """, unsafe_allow_html=True)

            with col_photo_box:
                render_photo_uploader(sel_k, title_label="매뉴얼 기준 사진 업로드 & 미리보기")

            st.markdown(f"""
            <div class="sj-card-alert">
                <b>⚠️ 맛·품질·위생 관리 및 식자재 손실 방지 주의사항:</b> {m_data['caution']}
            </div>
            """, unsafe_allow_html=True)

    with t_m2:
        st.markdown("#### 🍲 메뉴를 하나씩 선택하여 1인분 정량과 원가를 확인하고, 메뉴별 완성 사진을 등록하세요")
        c_sel1, c_sel2 = st.columns([1.0, 2.4])
        with c_sel1:
            m_cat_sel = st.selectbox("카테고리 필터", ["전체 (20종)"] + df_menu["카테고리"].unique().tolist())
            sub_menus = df_menu if m_cat_sel == "전체 (20종)" else df_menu[df_menu["카테고리"] == m_cat_sel]
            chosen_menu = st.radio("📌 조회할 메뉴 1개 선택", sub_menus["메뉴명"].tolist())

        with c_sel2:
            m_row = df_menu[df_menu["메뉴명"] == chosen_menu].iloc[0]
            rate_val = m_row["원가율(%)"]
            if rate_val <= 25:
                st_col, st_txt = "#2E6F40", "🟢 우수 (25% 이하)"
            elif rate_val <= 30:
                st_col, st_txt = "#B9770E", "🟡 적정 (25~30%)"
            else:
                st_col, st_txt = "#B8332A", "🔴 관리필요 (30% 초과)"

            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">현재 판매가 ({m_row['판매가확정여부']})</div><div class="sj-kpi-val">{int(m_row['적용판매가']):,}원</div><div class="sj-kpi-sub" style="color:#6E655F;">권장 판매가: {int(m_row['권장판매가(30%)']):,}원</div></div>""", unsafe_allow_html=True)
            with k2:
                st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">1인분 표준 식자재 원가</div><div class="sj-kpi-val">{int(round(m_row['1인분총원가'])):,}원</div><div class="sj-kpi-sub" style="color:#2E6F40;">정량 레시피 기준</div></div>""", unsafe_allow_html=True)
            with k3:
                st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">식자재 원가 비율</div><div class="sj-kpi-val" style="color:{st_col};">{rate_val:.1f}%</div><div class="sj-kpi-sub" style="color:{st_col};">{st_txt}</div></div>""", unsafe_allow_html=True)
            with k4:
                st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">1그릇당 남는 금액 (식자재 차감)</div><div class="sj-kpi-val">{int(round(m_row['1그릇당마진'])):,}원</div><div class="sj-kpi-sub" style="color:#6E655F;">판매가 - 식자재 원가</div></div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            c_ing_list, c_menu_photo = st.columns([1.5, 1])
            with c_ing_list:
                items = menu_items_dict[chosen_menu]
                for it in items:
                    share = it["원가비중(%)"]
                    qty_str = f"{it['투입량']:,.0f}g(개)" if it["투입량"] > 0 else "중량 확인필요"
                    cost_str = f"{int(round(it['투입원가(원)'])):,}원 ({share:.1f}%)" if it["투입원가(원)"] > 0 else "0원 (미산정)"
                    memo_badge = f"<div style='font-size:12px; color:#B8332A; margin-top:4px;'>📌 {it['메모']}</div>" if it["메모"] else ""
                    st.markdown(f"""
                    <div class="sj-card" style="padding:12px 16px; margin-bottom:8px;">
                        <div class="sj-nowrap-header">
                            <div class="sj-menu-title-wrap">
                                <span class="sj-tag">{it['구분']}</span>
                                <span class="sj-menu-name" style="font-size:14.5px;">{it['재료명']}</span>
                                <span style="color:#6E655F; font-size:12px; white-space:nowrap;">({it['1g단가(원)']:,.2f}원/g)</span>
                            </div>
                            <div style="text-align:right; white-space:nowrap; flex-shrink:0;">
                                <span style="font-weight:800; font-size:14px; color:#1A1817;">정량: {qty_str}</span>
                                <span style="margin-left:10px; font-weight:700; color:#8C1D18;">{cost_str}</span>
                            </div>
                        </div>
                        <div class="sj-prog-bg"><div class="sj-prog-fill" style="width:{min(share, 100):.1f}%;"></div></div>
                        {memo_badge}
                    </div>
                    """, unsafe_allow_html=True)

            with c_menu_photo:
                render_photo_uploader(f"메뉴_{chosen_menu}", title_label=f"[{chosen_menu}] 플레이팅 사진 등록")

    with t_m3:
        st.markdown("#### 🧪 매장 자체 소분 · 육수 · 수제 소스 멀티 배합기 (1배~10배 단위 즉시 환산)")
        c_sb1, c_sb2 = st.columns([1.05, 2.15])
        with c_sb1:
            chosen_sobun = st.selectbox("📌 소분/소스/반찬 레시피 선택 (23종)", df_sobun["소분명"].tolist())
            st.markdown("##### 🔢 배합 배수 선택 (1배~10배 단위)")
            batch_mult = st.radio(
                "작업할 배합 단위를 선택하세요 (1배~10배합)",
                options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                horizontal=True,
                format_func=lambda x: f"{x}배합"
            )
            render_photo_uploader(f"소분_{chosen_sobun}", title_label=f"[{chosen_sobun}] 소분 기준 사진")

        with c_sb2:
            sb_row = df_sobun[df_sobun["소분명"] == chosen_sobun].iloc[0]
            st.markdown(f"""
            <div class="sj-card-gold">
                <div class="sj-nowrap-header">
                    <div class="sj-menu-title-wrap">
                        <span class="sj-tag">{sb_row['소분번호']} ({sb_row['품목코드']})</span>
                        <span class="sj-menu-name" style="font-size:20px;">{chosen_sobun} — {batch_mult}배합 기준</span>
                    </div>
                    <span class="sj-status-badge" style="background:#1A1817; color:#CB994F;">1g당 원가 {sb_row['1g당실원가(원)']:,.2f}원</span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:12px; flex-wrap:wrap; gap:10px;">
                    <div style="font-size:14px; color:#5C4938;">
                        총 투입 중량: <b>{int(round(sb_row['총투입중량(g)']*batch_mult)):,}g</b> ➔ 조리 후 완성 중량: <b>{int(round(sb_row['최종완성중량(g)']*batch_mult)):,}g</b> (실사용 비율 {sb_row['실사용비율(%)']:.1f}%)
                    </div>
                    <div style="font-size:20px; font-weight:800; color:#8C1D18; white-space:nowrap;">
                        {batch_mult}배합 총원가: {int(round(sb_row['1회배합총원가(원)']*batch_mult)):,}원
                    </div>
                </div>
                <div style="font-size:12.5px; color:#6E655F; margin-top:6px;">📌 참고사항: {sb_row['메모'] if sb_row['메모'] else '전자저울로 정확히 계량하여 배합해 주세요.'}</div>
            </div>
            """, unsafe_allow_html=True)

            for it in sobun_items_dict[chosen_sobun]:
                st.markdown(f"""
                <div class="sj-card" style="padding:12px 18px; margin-bottom:8px;">
                    <div class="sj-nowrap-header">
                        <div class="sj-menu-title-wrap">
                            <span class="sj-tag">{it['품목코드']}</span>
                            <span class="sj-menu-name" style="font-size:15px;">{it['재료명']}</span>
                        </div>
                        <div style="white-space:nowrap; flex-shrink:0; font-size:14px;">
                            <b style="color:#1A1817;">투입량: {it['투입량(g)']*batch_mult:,.0f}g</b>
                            <span style="margin-left:12px; color:#8C1D18; font-weight:700;">원가: {int(round(it['투입원가(원)']*batch_mult)):,}원 ({it['원가비중(%)']:.1f}%)</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ==============================================================================
# 카테고리 2: 🥩 메뉴별 원가 & 식자재 단가표
# ==============================================================================
elif nav == "🥩 2. 메뉴별 원가 & 식자재 단가표":
    st.markdown("#### 🥩 전 메뉴 20종 원가 진단 카드 (한 줄 정렬) & 식자재 단가 검색")
    sub_t1, sub_t2 = st.tabs(["📊 20종 메뉴 원가율 & 마진 한눈에 보기", "📦 식자재 구매 단가 및 주문 규격표 (121종)"])

    with sub_t1:
        confirmed_df = df_menu[df_menu["판매가확정여부"] == "확정"]
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown("""<div class="sj-kpi"><div class="sj-kpi-label">전체 등록 메뉴 수</div><div class="sj-kpi-val">20종</div><div class="sj-kpi-sub">확정 판매가 15종 / 예상가 5종</div></div>""", unsafe_allow_html=True)
        with k2:
            st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">확정 15종 평균 원가율</div><div class="sj-kpi-val" style="color:#2E6F40;">{confirmed_df['원가율(%)'].mean():.1f}%</div><div class="sj-kpi-sub">권장 목표치 30.0% 이하 달성</div></div>""", unsafe_allow_html=True)
        with k3:
            st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">20종 평균 1인분 원가</div><div class="sj-kpi-val">{int(round(df_menu['1인분총원가'].mean())):,}원</div><div class="sj-kpi-sub">최소 799원 ~ 최대 10,698원</div></div>""", unsafe_allow_html=True)
        with k4:
            over30_cnt = int((df_menu["원가율(%)"] > 30.0).sum())
            st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">원가율 30% 초과 집중관리 메뉴</div><div class="sj-kpi-val" style="color:#B8332A;">{over30_cnt}종</div><div class="sj-kpi-sub">정량 계량 집중 점검 대상</div></div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
        grid_cols = st.columns(2)
        for idx, row in df_menu.iterrows():
            with grid_cols[idx % 2]:
                r_pct = row["원가율(%)"]
                if r_pct <= 25:
                    bg_col, txt_col, status_text = "#EBF7EE", "#2E6F40", "🟢 우수 (25% 이하)"
                elif r_pct <= 30:
                    bg_col, txt_col, status_text = "#FEF6E7", "#B9770E", "🟡 적정 (25~30%)"
                else:
                    bg_col, txt_col, status_text = "#FDEDEC", "#B8332A", "🔴 관리필요 (30% 초과)"

                cats = menu_cat_breakdown[row["메뉴명"]]
                top_cats = sorted([(k, v) for k, v in cats.items() if v > 0], key=lambda x: x[1], reverse=True)
                cat_badges = " ".join([f"<span class='sj-tag'>{k}: {int(round(v)):,}원</span>" for k, v in top_cats[:3]])

                st.markdown(f"""
                <div class="sj-card" style="padding:16px 20px;">
                    <div class="sj-nowrap-header">
                        <div class="sj-menu-title-wrap">
                            <span class="sj-tag">{row['메뉴번호']} · {row['카테고리']}</span>
                            <span class="sj-menu-name" title="{row['메뉴명']}">{row['메뉴명']}</span>
                        </div>
                        <span class="sj-status-badge" style="background:{bg_col}; color:{txt_col}; border:1px solid {txt_col};">{status_text}</span>
                    </div>
                    <div class="sj-nowrap-metrics">
                        <span>판매가: <b>{int(row['적용판매가']):,}원</b> ({row['판매가확정여부']})</span>
                        <span>1인분 원가: <b style="color:#8C1D18;">{int(round(row['1인분총원가'])):,}원 ({r_pct:.1f}%)</b></span>
                        <span>그릇당 남는 돈: <b style="color:#2E6F40;">{int(round(row['1그릇당마진'])):,}원</b></span>
                    </div>
                    <div class="sj-prog-bg"><div class="sj-prog-fill" style="width:{min(r_pct*2.5, 100):.1f}%;"></div></div>
                    <div style="margin-top:8px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{cat_badges}</div>
                </div>
                """, unsafe_allow_html=True)

    with sub_t2:
        f_col1, f_col2 = st.columns([1.2, 2])
        with f_col1:
            sel_ing_cat = st.selectbox("식자재 분류 선택", ["전체"] + df_raw["분류"].unique().tolist())
        with f_col2:
            q_str = st.text_input("🔍 식자재 이름 또는 납품처 검색", placeholder="예: 가브리살, 곤이, 사골, 지우푸드...")

        f_df = df_raw.copy()
        if sel_ing_cat != "전체":
            f_df = f_df[f_df["분류"] == sel_ing_cat]
        if q_str:
            f_df = f_df[f_df["식재료명"].str.contains(q_str, na=False) | f_df["비고"].str.contains(q_str, na=False)]

        st.markdown(f"총 **{len(f_df)}종**의 식자재가 검색되었습니다. (모든 금액 천 단위 콤마 적용)")
        ing_cols = st.columns(3)
        for i, (_, r_ing) in enumerate(f_df.iterrows()):
            with ing_cols[i % 3]:
                st.markdown(f"""
                <div class="sj-card" style="padding:14px 16px; margin-bottom:10px;">
                    <div class="sj-nowrap-header">
                        <span class="sj-tag">{r_ing['품목코드']} · {r_ing['분류']}</span>
                        <b style="color:#8C1D18; font-size:13.5px; white-space:nowrap;">1g(개)당 {r_ing['1g당실원가']:,.2f}원</b>
                    </div>
                    <div class="sj-menu-name" style="font-size:15px; margin-top:6px;">{r_ing['식재료명']}</div>
                    <div style="font-size:13px; color:#5C4938; margin-top:4px; white-space:nowrap;">
                        주문 포장 단위: <b>{int(r_ing['구매총중량']):,}g(개)</b> | 구매 단가: <b>{int(r_ing['구매가격']):,}원</b>
                    </div>
                    <div style="font-size:11.5px; color:#6E655F; margin-top:4px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                        납품·규격 안내: {r_ing['비고'] if pd.notna(r_ing['비고']) else '-'}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ==============================================================================
# 카테고리 3: 🔍 실매출 · 원가 · 고정비 통합 진단
# ==============================================================================
elif nav == "🔍 3. 실매출 · 원가 · 고정비 통합 진단":
    st.markdown("""
    <div class="sj-card-gold">
        <h3 style="margin-top:0; color:#1A1817;">🔍 가맹점 [포스기 실제 매출 vs 실제 식자재 지출 · 고정비] 통합 손익 진단</h3>
        <p style="margin-bottom:0; color:#5C4938; font-weight:600;">
        이번 달 매장에서 실제로 판매한 <b>음식 20종 + 주류/음료 수량</b>과 <b>실제 식자재 구매액(본사물류 + 개인 마트/시장 구매) 및 9대 매장 고정비</b>를 한 화면에서 입력하면, <b>어느 재료에서 원가가 새어 나갔는지</b>와 <b>이번 달 최종 순수익</b>을 천 단위 콤마(,)로 보기 쉽게 진단합니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 1️⃣ 당월 가맹점 실제 판매량 입력 (스크롤 없이 20종 전체 한눈에 보기)")
    st.caption("표 안의 [실판매가(원)] 또는 [당월 판매량(그릇)] 숫자를 더블클릭하여 수정하시면 우측 금액이 천 단위 콤마(,)로 즉시 자동 계산됩니다.")

    default_sales_qty = [380, 140, 260, 220, 45, 0, 190, 0, 0, 0, 160, 110, 85, 130, 65, 90, 120, 95, 150, 110]
    full_pos_df = pd.DataFrame({
        "번호": df_menu["메뉴번호"],
        "메뉴명": df_menu["메뉴명"],
        "실판매가(원)": df_menu["적용판매가"].astype(int),
        "표준원가(원)": df_menu["1인분총원가"].round(0).astype(int),
        "월판매수량": default_sales_qty
    })

    pos_left_col, pos_right_col = st.columns(2)
    with pos_left_col:
        st.markdown("##### 🍲 식사 · 점심 메뉴 (#1 ~ #10)")
        edited_pos_1 = st.data_editor(
            full_pos_df.iloc[:10].reset_index(drop=True),
            column_config={
                "번호": st.column_config.TextColumn("번호", disabled=True, width="small"),
                "메뉴명": st.column_config.TextColumn("메뉴명", disabled=True),
                "실판매가(원)": st.column_config.NumberColumn("실판매가(원)", min_value=0, step=500, format="localized"),
                "표준원가(원)": st.column_config.NumberColumn("1인분 원가(원)", disabled=True, format="localized"),
                "월판매수량": st.column_config.NumberColumn("당월 판매량(그릇)", min_value=0, step=10, format="localized")
            },
            hide_index=True,
            use_container_width=True,
            key="pos_editor_left"
        )
    with pos_right_col:
        st.markdown("##### 🥩 메인 보쌈 · 요리 · 사이드 (#11 ~ #20)")
        edited_pos_2 = st.data_editor(
            full_pos_df.iloc[10:].reset_index(drop=True),
            column_config={
                "번호": st.column_config.TextColumn("번호", disabled=True, width="small"),
                "메뉴명": st.column_config.TextColumn("메뉴명", disabled=True),
                "실판매가(원)": st.column_config.NumberColumn("실판매가(원)", min_value=0, step=500, format="localized"),
                "표준원가(원)": st.column_config.NumberColumn("1인분 원가(원)", disabled=True, format="localized"),
                "월판매수량": st.column_config.NumberColumn("당월 판매량(그릇)", min_value=0, step=10, format="localized")
            },
            hide_index=True,
            use_container_width=True,
            key="pos_editor_right"
        )

    edited_pos = pd.concat([edited_pos_1, edited_pos_2], ignore_index=True)

    st.markdown("##### 🍶 주류 및 음료 당월 판매량 입력")
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
            "판매단가(원)": st.column_config.NumberColumn("판매가(원)", step=500, format="localized"),
            "표준원가(원)": st.column_config.NumberColumn("병/캔당 매입가(원)", step=50, format="localized"),
            "월판매수량": st.column_config.NumberColumn("당월 판매량(병/캔)", step=10, format="localized")
        },
        hide_index=True,
        use_container_width=True,
        key="bev_editor_full"
    )

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
        "포장용기/소모품 및 기본반찬": 0.0
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
        theo_cat_totals["포장용기/소모품 및 기본반찬"] += c_map.get("포장/소모품", 0.0) * qty

    theo_cat_totals["포장용기/소모품 및 기본반찬"] += food_rev * 0.022
    total_theo_cost = sum(theo_cat_totals.values())

    st.markdown("---")
    col_step2, col_step3 = st.columns([1.15, 1])

    with col_step2:
        st.markdown("#### 2️⃣ 당월 실제 식자재 매입·사용 금액 입력 (물류 + 개인 마트 구매)")
        st.caption("본사/물류 명세서 합계와 마트·시장에서 직접 구매한 금액을 입력해 주세요. (천 단위 콤마 자동 적용)")

        default_logistics = [
            int(theo_cat_totals["육류 (가브리살/스지 등)"] * 1.12),
            int(theo_cat_totals["해산물 (알/곤이/꼬막/오징어)"] * 1.10),
            int(theo_cat_totals["채소/농산 (배추/미나리/야채)"] * 0.85),
            int(theo_cat_totals["소스/공산품 (육수/분말/양념)"] * 1.03),
            int(theo_cat_totals["면/사리류 (칼국수/파스타/당면)"] * 1.02),
            int(theo_cat_totals["주류/음료 (소주/맥주/음료)"] * 1.03),
            int(theo_cat_totals["포장용기/소모품 및 기본반찬"] * 0.90)
        ]
        default_personal = [150000, 120000, 680000, 90000, 30000, 40000, 240000]

        spend_input_df = pd.DataFrame({
            "품목군": list(theo_cat_totals.keys()),
            "표준원가(원)": [int(round(v)) for v in theo_cat_totals.values()],
            "물류/주류업체 매입(원)": default_logistics,
            "개인구매/사입(원)": default_personal
        })

        edited_spend = st.data_editor(
            spend_input_df,
            column_config={
                "품목군": st.column_config.TextColumn("품목군 분류", disabled=True),
                "표준원가(원)": st.column_config.NumberColumn("판매량 기준 표준원가(원)", disabled=True, format="localized"),
                "물류/주류업체 매입(원)": st.column_config.NumberColumn("물류/주류업체 매입액(원)", min_value=0, step=50000, format="localized"),
                "개인구매/사입(원)": st.column_config.NumberColumn("개인 마트/시장 구매액(원)", min_value=0, step=10000, format="localized")
            },
            hide_index=True,
            use_container_width=True,
            key="spend_editor_comma"
        )
        inv_adj = st.number_input("📦 월말 남은 재고 보정액 (월초 재고 - 월말 재고, 없으면 0원)", value=0, step=50000)

    with col_step3:
        st.markdown("#### 3️⃣ 매장 월 고정비 9개 항목 입력 (엑셀 문서 표준 기준)")
        st.caption("원가계산서 문서에 정의된 9대 고정비 항목입니다. 금액 수정 시 최종 순수익에 즉시 반영됩니다.")

        fixed_rows = [
            {"항목번호": "고정비 1", "고정비 항목명": "임대료 및 관리비", "세부 내용": "월세, 상가 관리비 포함", "월지출액(원)": st.session_state["고정비 1. 임대료 및 관리비 (월세·상가관리비 포함)"]},
            {"항목번호": "고정비 2", "고정비 항목명": "인건비 (직원/알바)", "세부 내용": "주방 및 홀 인건비 총액", "월지출액(원)": st.session_state["고정비 2. 인건비 (주방·홀 직원 및 알바 총액)"]},
            {"항목번호": "고정비 3", "고정비 항목명": "수도 / 광열비 (가스·전기)", "세부 내용": "매장 가스비, 전기세, 수도세", "월지출액(원)": st.session_state["고정비 3. 수도 / 광열비 (매장 가스·전기·수도세)"]},
            {"항목번호": "고정비 4", "고정비 항목명": "기타 고정비 (세무/통신/방역)", "세부 내용": "기장료, 인터넷, 포스기, 정수기 등", "월지출액(원)": st.session_state["고정비 4. 기타 고정비 (세무기장·통신·포스기·방역)"]},
            {"항목번호": "고정비 5", "고정비 항목명": "예비비 / 기타 소모품", "세부 내용": "주방 세제, 화장지, 일회용품 등", "월지출액(원)": st.session_state["고정비 5. 예비비 / 기타 소모품 (세제·화장지·일회용품)"]},
            {"항목번호": "고정비 6", "고정비 항목명": "렌탈비용", "세부 내용": "제빙기, 정수기, 키오스크 등", "월지출액(원)": st.session_state["고정비 6. 렌탈비용 (제빙기·정수기·키오스크 등)"]},
            {"항목번호": "고정비 7", "고정비 항목명": "대출 이자 및 원리금", "세부 내용": "창업대출 원리금 및 이자", "월지출액(원)": st.session_state["고정비 7. 대출 이자 및 원리금 (창업대출 등)"]},
            {"항목번호": "고정비 8", "고정비 항목명": "보험료", "세부 내용": "화재보험, 배상책임보험 등", "월지출액(원)": st.session_state["고정비 8. 보험료 (화재보험·배상책임보험 등)"]},
            {"항목번호": "고정비 9", "고정비 항목명": "부대비용 (4대보험/퇴직연금)", "세부 내용": "4대보험 사업주 부담분, 퇴직연금 등", "월지출액(원)": st.session_state["고정비 9. 부대비용 (4대보험·퇴직연금 등)"]},
        ]
        fixed_df = pd.DataFrame(fixed_rows)
        edited_fixed = st.data_editor(
            fixed_df,
            column_config={
                "항목번호": st.column_config.TextColumn("구분", disabled=True, width="small"),
                "고정비 항목명": st.column_config.TextColumn("고정비 항목", disabled=True),
                "세부 내용": st.column_config.TextColumn("포함 내역", disabled=True),
                "월지출액(원)": st.column_config.NumberColumn("월 지출 금액(원)", min_value=0, step=50000, format="localized")
            },
            hide_index=True,
            use_container_width=True,
            key="fixed_cost_editor_cat3"
        )
        comm_rate_cat3 = st.slider("💳 평균 카드결제 / 배달앱 수수료율 (%)", min_value=0.0, max_value=20.0, value=3.5, step=0.5)

    for idx_f, fk in enumerate(DEFAULT_FIXED_COSTS.keys()):
        st.session_state[fk] = int(edited_fixed.loc[idx_f, "월지출액(원)"])

    total_fixed_cat3 = float(edited_fixed["월지출액(원)"].sum())
    comm_amount_cat3 = total_actual_rev * (comm_rate_cat3 / 100.0)

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

    final_net_profit = total_actual_rev - total_actual_cost - comm_amount_cat3 - total_fixed_cat3
    final_net_margin_pct = (final_net_profit / total_actual_rev * 100.0) if total_actual_rev > 0 else 0.0

    st.session_state["sim_actual_rev"] = total_actual_rev
    st.session_state["sim_actual_cost"] = total_actual_cost
    st.session_state["sim_theo_cost"] = total_theo_cost
    st.session_state["sim_comm_rate"] = comm_rate_cat3

    st.markdown("---")
    st.markdown("#### 📊 당월 실매출 · 실원가 · 9대 고정비 반영 최종 손익 요약표 (천 단위 콤마 적용)")

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">① 당월 실제 총매출</div><div class="sj-kpi-val">{int(round(total_actual_rev)):,}원</div><div class="sj-kpi-sub">음식 {int(round(food_rev)):,}원 / 주류 {int(round(bev_rev)):,}원</div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">② 레시피 기준 표준원가</div><div class="sj-kpi-val">{int(round(total_theo_cost)):,}원</div><div class="sj-kpi-sub" style="color:#2E6F40;">표준 원가율: {theo_rate_pct:.1f}%</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">③ 실제 사용한 총원가</div><div class="sj-kpi-val" style="color:#8C1D18;">{int(round(total_actual_cost)):,}원</div><div class="sj-kpi-sub" style="color:#8C1D18;">실제 원가율: {actual_rate_pct:.1f}% (초과 {int(round(total_variance)):+,}원)</div></div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">④ 9대 고정비 + 수수료 합계</div><div class="sj-kpi-val">{int(round(total_fixed_cat3 + comm_amount_cat3)):,}원</div><div class="sj-kpi-sub">고정비 {int(round(total_fixed_cat3)):,}원 + 수수료 {int(round(comm_amount_cat3)):,}원</div></div>""", unsafe_allow_html=True)
    with m5:
        np_color = "#2E6F40" if final_net_profit > 0 else "#B8332A"
        st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">⑤ 사장님 월 최종 순수익</div><div class="sj-kpi-val" style="color:{np_color};">{int(round(final_net_profit)):,}원</div><div class="sj-kpi-sub" style="color:{np_color};">순수익률: {final_net_margin_pct:.1f}% (세전)</div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    sorted_var = edited_spend.sort_values("원가차액(실제-표준)", ascending=False)
    v_cols = st.columns(2)
    for idx, (_, r_v) in enumerate(sorted_var.iterrows()):
        with v_cols[idx % 2]:
            diff_v = r_v["원가차액(실제-표준)"]
            pct_v = r_v["초과율(%)"]
            card_cls = "sj-card-alert" if diff_v > 150000 else ("sj-card" if diff_v > 0 else "sj-card-good")
            badge_str = f"🚨 +{int(round(diff_v)):,}원 초과지출 (+{pct_v:.1f}%)" if diff_v > 0 else f"✅ {int(round(diff_v)):,}원 절감 ({pct_v:.1f}%)"
            st.markdown(f"""
            <div class="{card_cls}" style="padding:14px 18px; margin-bottom:10px;">
                <div class="sj-nowrap-header">
                    <span class="sj-menu-name" style="font-size:15.5px;">{r_v['품목군']}</span>
                    <span class="sj-status-badge" style="color:{'#B8332A' if diff_v > 0 else '#2E6F40'}; background:#FFFFFF;">{badge_str}</span>
                </div>
                <div style="font-size:13px; color:#5C4938; margin-top:6px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                    표준원가: <b>{int(round(r_v['표준원가(원)'])):,}원</b> vs 실제지출: <b>{int(round(r_v['실제사용원가(원)'])):,}원</b>
                    (물류 {int(round(r_v['물류/주류업체 매입(원)'])):,}원 + 개인구매 {int(round(r_v['개인구매/사입(원)'])):,}원)
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 손정보쌈 슈퍼바이저 종합 결론 리포트
    st.markdown("#### 4️⃣ 손정보쌈 슈퍼바이저 종합 결론 및 현장 개선 처방전")
    worst_row = sorted_var.iloc[0]
    second_row = sorted_var.iloc[1]
    bev_share = (bev_rev / total_actual_rev * 100.0) if total_actual_rev > 0 else 0.0
    personal_share = (total_personal / total_actual_cost * 100.0) if total_actual_cost > 0 else 0.0

    conclusions = []
    meat_diff = float(edited_spend.loc[edited_spend["품목군"].str.contains("육류"), "원가차액(실제-표준)"].values[0])
    if meat_diff > 100000:
        conclusions.append(
            f"<li><b>[육류 파트 지출 초과 (+{int(round(meat_diff)):,}원)]</b>: 가브리살과 스지 실제 사용량이 판매량 기준 표준치보다 많습니다. "
            f"① <b>가브리보쌈 삶기 기준(중불 40분 삶기 + 20분 뜸들이기)</b>을 지켜 고기가 줄어드는 손실을 막고, "
            f"② 점심 보쌈정식(일반 <b>120g</b> / 특 <b>170g</b>) 및 저녁 보쌈(소 <b>300g</b> / 중 <b>400g</b>)을 썰 때 반드시 전자저울로 달아서 <b>정량보다 많이 나가는 일</b>이 없도록 점검해 주세요.</li>"
        )
    sea_diff = float(edited_spend.loc[edited_spend["품목군"].str.contains("해산물"), "원가차액(실제-표준)"].values[0])
    if sea_diff > 80000:
        conclusions.append(
            f"<li><b>[해산물 파트 지출 초과 (+{int(round(sea_diff)):,}원)]</b>: 알·곤이 및 꼬막 원가가 표준보다 높게 발생했습니다. "
            f"① 칼국수·전골 조리 시 <b>1인분 정량(알 50g / 곤이 120g)</b> 및 저녁 알곤이볶음(알 180g / 곤이 360g) 소분 정량을 지키고, "
            f"② 알곤이 찌기(중불 50분) 후 식혀서 보관하기 및 냉동 꼬막 소분 기준(냉동 100g ➔ 해동 후 <b>80g</b>)을 다시 확인해 주세요.</li>"
        )
    veg_diff = float(edited_spend.loc[edited_spend["품목군"].str.contains("채소"), "원가차액(실제-표준)"].values[0])
    if veg_diff > 80000 or personal_share > 8.0:
        conclusions.append(
            f"<li><b>[채소/농산 및 마트·시장 개인 구매 과다 (채소 {int(round(veg_diff)):+,}원 / 개인구매 비중 {personal_share:.1f}%)]</b>: "
            f"마트나 시장에서 개인 카드로 구매한 금액이 월 <b>{int(round(total_personal)):,}원</b>입니다. "
            f"① 배추 절이기 작업 시 <b>배추 3통을 절인 소금물을 버리지 않고 알배추 2박스 절이는 데 재사용</b>하여 소금·배추 손실을 줄이고, "
            f"② 미나리는 <b>줄기(냉국수 50g)와 잎(무침 40g)을 나누어 사용</b>하며, 점심 기본반찬 4종은 예상 점심 매출에 맞춰 조리량을 조절해 버리는 반찬을 줄여주세요.</li>"
        )
    if bev_share < 10.0:
        conclusions.append(
            f"<li><b>[주류/음료 및 별미 메뉴 추가 주문 유도 (현재 주류 비중 {bev_share:.1f}%)]</b>: "
            f"저녁 시간대 보쌈·알곤이볶음·맵불스지 주문 고객에게 주류 및 <b>마무리 알곤이 치즈 파스타(원가율 20.0%)</b> 추가 주문을 안내하시면 매장 전체 순수익률을 빠르게 높일 수 있습니다.</li>"
        )

    if not conclusions:
        conclusions.append("<li><b>[전 품목군 원가 관리 우수]</b>: 모든 식자재가 판매량 기준 표준 원가 범위 안에서 알뜰하게 관리되고 있습니다. 현재의 전자저울 계량과 소분 습관을 그대로 유지해 주세요.</li>")

    conc_html = "".join(conclusions)
    st.markdown(f"""
    <div class="sj-card-gold">
        <h4 style="margin-top:0; color:#8C1D18;">📋 [{selected_branch}] 손정보쌈 슈퍼바이저 종합 결론 리포트</h4>
        <p style="font-size:15px; font-weight:700; color:#1A1817; line-height:1.6;">
            당월 총매출 <b>{int(round(total_actual_rev)):,}원</b> 대비 레시피 기준 표준 식자재 원가는 <b>{int(round(total_theo_cost)):,}원({theo_rate_pct:.1f}%)</b>이며,
            실제 사용한 식자재 원가는 <b>{int(round(total_actual_cost)):,}원({actual_rate_pct:.1f}%)</b>으로 총 <b style="color:#B8332A;">{int(round(total_variance)):+,}원({rate_gap_pctp:+.1f}%p)</b>의 차이가 발생했습니다.<br>
            여기에 매장 9대 고정비 합계(<b>{int(round(total_fixed_cat3)):,}원</b>)와 결제·배달 수수료(<b>{int(round(comm_amount_cat3)):,}원</b>)를 모두 차감한
            <b>이번 달 사장님의 최종 순수익(세전)은 <span style="color:#2E6F40;">{int(round(final_net_profit)):,}원 (순수익률 {final_net_margin_pct:.1f}%)</span></b>입니다.
            현재 원가 차이가 가장 큰 항목은 <b>1순위 [{worst_row['품목군']} ({int(round(worst_row['원가차액(실제-표준)'])):+,}원)]</b>, <b>2순위 [{second_row['품목군']} ({int(round(second_row['원가차액(실제-표준)'])):+,}원)]</b>입니다.
        </p>
        <ul style="line-height:1.75; font-size:14px; color:#1A1817; margin-bottom:0;">
            {conc_html}
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 카테고리 4: 💰 매장 월간 순수익 상세 시뮬레이터 (9대 고정비 반영)
# ==============================================================================
elif nav == "💰 4. 매장 월간 순수익 상세 시뮬레이터":
    st.markdown("#### 💰 가맹점 월간 최종 순수익 계산표 (엑셀 문서 9대 고정비 항목 전체 반영)")
    st.caption("모든 금액은 천 단위 콤마(,)로 표시되며, 9개 고정비 세부 항목을 매장 상황에 맞게 조정하여 목표 순수익을 시뮬레이션할 수 있습니다.")

    default_rev = int(round(st.session_state.get("sim_actual_rev", 45000000)))
    default_act_cost = int(round(st.session_state.get("sim_actual_cost", 13200000)))
    default_theo_cost = int(round(st.session_state.get("sim_theo_cost", 11500000)))
    default_comm = float(st.session_state.get("sim_comm_rate", 3.5))

    c_p1, c_p2 = st.columns([1, 1.25])
    with c_p1:
        st.markdown("##### 1️⃣ 월 총매출 · 식자재 원가 · 수수료 설정")
        m_rev = st.number_input("당월 총매출액 (음식 + 주류/음료 합산, 원)", value=default_rev, step=500000)
        st.markdown(f"👉 입력된 당월 총매출액: **`{int(m_rev):,}원`**")

        cost_mode = st.radio(
            "적용할 식자재 원가 기준 선택",
            ["실제 사용 원가 기준 (물류+개인구매 반영)", "표준 레시피 원가 기준 (정량 준수 시 시뮬레이션)"],
            horizontal=True
        )
        m_cost = st.number_input(
            "당월 총 식자재·주류 원가 합계 (원)",
            value=default_act_cost if "실제" in cost_mode else default_theo_cost,
            step=100000
        )
        st.markdown(f"👉 입력된 총 식자재·주류 원가: **`{int(m_cost):,}원`** (매출 대비 **{(m_cost/m_rev*100 if m_rev>0 else 0):.1f}%**)")

        comm_rate = st.slider("평균 결제/배달 수수료율 (%)", min_value=0.0, max_value=25.0, value=default_comm, step=0.5)
        m_comm = m_rev * (comm_rate / 100.0)
        st.markdown(f"👉 월 결제·배달 수수료 금액: **`{int(round(m_comm)):,}원`**")

    with c_p2:
        st.markdown("##### 2️⃣ 매장 월 고정비 9개 항목 상세 입력 (천 단위 콤마 실시간 확인)")
        f_col_a, f_col_b = st.columns(2)
        fixed_keys = list(DEFAULT_FIXED_COSTS.keys())
        updated_fixed_sum = 0

        for idx_k, fk in enumerate(fixed_keys):
            target_col = f_col_a if idx_k < 5 else f_col_b
            with target_col:
                val = st.number_input(
                    fk,
                    min_value=0,
                    value=int(st.session_state[fk]),
                    step=50000,
                    key=f"sim_f_{idx_k}"
                )
                st.session_state[fk] = val
                updated_fixed_sum += val
                st.caption(f"적용 금액: **{int(val):,}원**")

    total_fixed = updated_fixed_sum
    gross_profit = m_rev - m_cost - m_comm
    net_profit = gross_profit - total_fixed
    net_margin_pct = (net_profit / m_rev * 100.0) if m_rev > 0 else 0.0
    cost_pct = (m_cost / m_rev * 100.0) if m_rev > 0 else 0.0
    fixed_pct = (total_fixed / m_rev * 100.0) if m_rev > 0 else 0.0
    potential_saving = max(0, default_act_cost - default_theo_cost)

    st.markdown("---")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">당월 총매출액</div><div class="sj-kpi-val">{int(m_rev):,}원</div><div class="sj-kpi-sub">매출 기준 100.0%</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">식자재·주류 원가 + 수수료</div><div class="sj-kpi-val" style="color:#8C1D18;">{int(round(m_cost + m_comm)):,}원</div><div class="sj-kpi-sub">원가 {cost_pct:.1f}% + 수수료 {comm_rate:.1f}%</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">9대 월 고정비 총합계</div><div class="sj-kpi-val">{int(total_fixed):,}원</div><div class="sj-kpi-sub">매출 대비 비중: {fixed_pct:.1f}%</div></div>""", unsafe_allow_html=True)
    with k4:
        np_col = "#2E6F40" if net_profit > 0 else "#B8332A"
        st.markdown(f"""<div class="sj-kpi"><div class="sj-kpi-label">💰 사장님 월 최종 순수익 (세전)</div><div class="sj-kpi-val" style="color:{np_col};">{int(round(net_profit)):,}원</div><div class="sj-kpi-sub" style="color:{np_col};">최종 순수익률: {net_margin_pct:.1f}%</div></div>""", unsafe_allow_html=True)

    fixed_badges_html = " ".join([
        f"<span class='sj-tag' style='margin-bottom:6px;'>{fk.split('(')[0].strip()}: <b>{int(st.session_state[fk]):,}원</b></span>"
        for fk in fixed_keys
    ])
    st.markdown(f"""
    <div class="sj-card" style="margin-top:14px;">
        <div style="font-weight:800; font-size:15px; margin-bottom:8px; color:#1A1817;">🧾 9대 고정비 항목별 지출 내역 요약 (합계: {int(total_fixed):,}원)</div>
        <div style="line-height:2.0;">{fixed_badges_html}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sj-card-gold" style="margin-top:12px;">
        <h4 style="margin-top:0; color:#1A1817;">💡 손정보쌈 슈퍼바이저 수익 개선 팁</h4>
        <p style="margin-bottom:0; font-size:15px; color:#5C4938; line-height:1.6;">
        현재 정량 계량과 소분 매뉴얼 준수를 통해 표준원가 대비 초과 지출된 식자재 비용(<b>+{int(round(potential_saving)):,}원</b>)만 줄여도,
        매출을 늘리지 않고도 사장님의 월 최종 순수익은 <b>{int(round(net_profit)):,}원 ➔ {int(round(net_profit + potential_saving)):,}원</b>으로 즉시 올라갑니다.
        </p>
    </div>
    """, unsafe_allow_html=True)
