# 팀 실험 결과

`python3 scripts/exp.py`가 만드는 폴더입니다. 손으로 고치지 마세요. 사용법은 [EXPERIMENTS.md](../EXPERIMENTS.md).

```
results/<라이브러리>/OWNER.txt                 담당자 (exp.py claim)
results/<라이브러리>/1h/<하네스>/rNN.json       1시간 회차 하나의 결과 (exp.py run)
results/<라이브러리>/24h/<하네스>.json         24시간 실험, 구간마다 측정값이 쌓임 (exp.py run --plan 24h)
results/<라이브러리>/REPORT.md                 라이브러리 보고서 (exp.py report)
results/SUMMARY.md                            전체 요약 (exp.py report --all, 정리 담당만)
```
