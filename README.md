# 📈 섹터별 턴어라운드 대시보드

KOSPI, KOSDAQ, 미국 시장의 섹터별/종목별 턴어라운드를 시각화하는 Streamlit 대시보드입니다.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ 주요 기능

### 📊 섹터 분석
- **턴어라운드 스코어 랭킹**: 섹터별 종합 점수 시각화
- **가격 추이 차트**: 상위 섹터들의 3개월 가격 흐름
- **기술적 지표 차트**: 저점 대비 상승률, MA 크로스, RSI
- **턴어라운드 매트릭스**: 버블 차트로 섹터 포지션 확인

### 🔍 종목 분석
- 섹터 내 개별 종목 상세 분석
- 종목별 턴어라운드 지표 테이블
- 하이라이트로 턴어라운드 종목 식별

### 📈 상세 차트
- 다중 섹터 비교 차트
- 레이더 차트로 종합 비교

## 🛠️ 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/Delpiero21/stock_investment.git
cd stock_investment
```

### 2. 가상환경 생성 (권장)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 실행
```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

## 📖 지표 설명

| 지표 | 설명 | 해석 |
|------|------|------|
| **턴어라운드 스코어** | 종합 점수 (0-100) | 70↑ 강함, 50-70 보통, 50↓ 약함 |
| **저점 대비 상승률** | 3개월 저점 대비 현재가 | 15%↑ 반등 신호 |
| **MA20-MA60** | 20일선 vs 60일선 | 양수 = 골든크로스 |
| **RSI** | 상대강도지수 (14일) | 50↑ 상승 모멘텀 |
| **거래량** | 평균 대비 비율 | 150%↑ 관심 증가 |

## 🔧 데이터 소스

### 샘플 데이터 (기본)
- 시뮬레이션된 데이터로 빠른 테스트 가능

### 실제 데이터 (선택)
사이드바에서 "실제 데이터 사용" 체크박스 활성화

지원 API:
- **한국 시장**: [FinanceDataReader](https://github.com/financedata-org/financedatareader)
- **미국 시장**: [yfinance](https://github.com/ranaroussi/yfinance)

## 📁 프로젝트 구조

```
stock_investment/
├── app.py                 # 메인 Streamlit 앱
├── requirements.txt       # 패키지 의존성
├── README.md             # 프로젝트 설명
└── .streamlit/           # Streamlit 설정 (선택)
    └── config.toml
```

## 🚀 배포

### Streamlit Cloud (무료)
1. GitHub 저장소 연결
2. [share.streamlit.io](https://share.streamlit.io) 에서 배포
3. Main file: `app.py` 지정

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

## 📝 향후 계획

- [ ] 실시간 데이터 자동 업데이트
- [ ] 알림 기능 (텔레그램, 슬랙)
- [ ] 백테스팅 기능
- [ ] 포트폴리오 추적
- [ ] AI 기반 턴어라운드 예측

## 🤝 기여

Pull Request 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

## 📧 문의

이슈 탭에서 질문이나 버그 리포트를 남겨주세요.

---

⭐ 유용하셨다면 Star를 눌러주세요!
