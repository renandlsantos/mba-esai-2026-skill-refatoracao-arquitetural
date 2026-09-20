# Shop red phase

Before refactoring, unittest failed importing create_app: baseline has only a global Flask object. Baseline behavioral evidence separately confirms SQL login bypass and credential exposure (baseline-shop.json). Implementation was then added; no unexplained retry was performed.
