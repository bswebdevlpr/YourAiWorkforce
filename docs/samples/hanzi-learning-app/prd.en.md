<!--
  ⚠️ HUMAN TRANSLATION — NOT system output.
  This is a faithful English translation of ./prd.md, which is the raw, unedited
  output of the product_discovery agent (generated in Korean by qwen3:8b).
  Provided for readability only. The authoritative sample is the Korean original (prd.md).
  Content is preserved verbatim, including the model-hallucinated date below.
-->

> **⚠️ Human translation.** The authoritative artifact is [`prd.md`](prd.md) — the raw, unedited
> Korean output of the `product_discovery` agent. This file is a faithful hand-translation for
> readability, not a system output.

## Project Name
Mobile app for learning Hanja like a game

## Date
2023-10-15

## Author
Product Discovery

## 1. Problem Definition
- **Action**: Learning (building the ability to memorize and read Hanja)
- **Domain Object**: Hanja (Chinese characters)
- **Platform**: Mobile app
- **Core problems**: boredom of repetitive study, missing review timing, complexity of radical/stroke-order rules

## 2. Target Users
### Persona 1: Kim Min-su (17, high-school senior)
- Background: 3rd-year high-schooler, preparing for Hanja Proficiency Test level 8
- Tech level: medium digital literacy
- Goal: pass Hanja Proficiency Test level 1 and use it for college admissions
- Pain points: boredom of repetitive study, missing review timing
- Usage scenario: reviews 10 cards for 15 minutes after class, motivated by daily streaks

### Persona 2: Park Ji-hyun (28, accountant)
- Background: needs to process Chinese-language documents, faces a Hanja communication barrier
- Tech level: high proficiency with mobile apps
- Goal: improve Hanja reading ability and cultural understanding
- Pain points: monotonous format of existing textbooks, lack of time
- Usage scenario: spaced-repetition review for 10 minutes during the commute, level-up competition

### Persona 3: Lee Jun-ho (35, Japanese learner)
- Background: preparing for JLPT N4, needs foundational Hanja study
- Tech level: expert
- Goal: strengthen handwriting recognition and meaning/reading matching for Hanja
- Pain points: study delays caused by complex radical/stroke-order rules
- Usage scenario: studies 15 cards during morning coffee, motivated by gamification

## 3. Feature Priorities
### P0 (MVP essential)
1. SRS spaced-repetition system: auto-adjusted to Hanja Proficiency Test levels 8–1 (targets: Kim Min-su, Park Ji-hyun, Lee Jun-ho)
2. Handwriting recognition quiz: evaluates Hanja writing skill and gives feedback (target: Lee Jun-ho)
3. Daily streak system: rewards for 7 consecutive days of study (targets: Kim Min-su, Park Ji-hyun)
4. Gamified card collection: styling elements added on level-up (targets: Park Ji-hyun, Lee Jun-ho)
5. Radical/stroke-order rule learning: classification and practice by character components (target: Lee Jun-ho)

### P1 (Critical)
6. Hanja Proficiency Test goal setting: step-by-step study plan for levels 8–1 (target: Kim Min-su)
7. Meaning/reading matching quiz: reading-aloud drills with real-time feedback (targets: Park Ji-hyun, Lee Jun-ho)
8. Learning progress visualization: statistics on study time/accuracy (targets: Kim Min-su, Lee Jun-ho)

### P2 (Nice-to-have)
9. Study-buddy invite feature: adds competition/collaboration modes (target: Park Ji-hyun)
10. Cultural context learning: provides Hanja origin stories/cultural background (target: Park Ji-hyun)

### P3 (Future)
11. AI personalized learning recommendations: tailored content based on user patterns (target: Lee Jun-ho)
12. Multi-language support: adds Japanese/Chinese subtitles/quizzes (target: Lee Jun-ho)

## 4. Success Metrics
1. Daily study time: 20 min/day (targets: Kim Min-su, Park Ji-hyun, Lee Jun-ho) - measured by: daily streak records, threshold: sustained 14+ days
2. SRS review accuracy: 85%+ (targets: Kim Min-su, Lee Jun-ho) - measured by: handwriting recognition quiz results, threshold: adjust review interval below 75%
3. Level-up achievement rate: 5 level-ups within 30 days (targets: Park Ji-hyun, Lee Jun-ho) - measured by: gamification history, threshold: extra reward if achieved within 20 days
4. Hanja reading accuracy: 90%+ (targets: Park Ji-hyun, Lee Jun-ho) - measured by: meaning/reading matching quiz, threshold: add radical/stroke-order study below 80%
5. Learning-progress sharing: 50%+ user participation (target: all personas) - measured by: study-buddy invite feature, threshold: redesign incentives below 30%

## 5. Scope Boundaries
### In Scope
- Learning based on Hanja Proficiency Test levels
- SRS spaced-repetition review
- Handwriting recognition and meaning/reading matching quizzes
- Daily streak system
- Gamified card collection/level-up
- Radical/stroke-order rule learning

### Out of Scope
- Social media integration
- External API integration (e.g., education platforms)
- Advanced AI personalized recommendations

## 6. Phase Milestones (estimated)
- **Phase 0 complete**: PRD + architecture + domain-knowledge docs
- **Phase 1 complete**: database + basic API + build setup
- **Phase 2 complete**: all P0 features working
- **Phase 3 complete**: P1 features + algorithm implementation
- **Phase 4 complete**: SEO + performance optimization + i18n
- **Phase 5 complete**: passes domain-expert review
- **Phase 6 complete**: production deployment

## Appendix: Domain Keyword Extraction
- Technical domain: SRS, Hanja Proficiency Test, radicals/stroke order
- Academic domain: classical Chinese literature, education
- Sub-domains: Hanja reading, handwriting recognition, gamification
