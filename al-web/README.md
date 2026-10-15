# AL-Web (Agentic Lender portal)

Static prototype. No build step. Open `index.html` in a browser.

```
al-web/
  index.html        Pipeline: KPIs + origination queue
  dossier.html      Collateral, borrower profile, multi-agent audit console
  stress-test.html  Macro stress simulator (range sliders)
  settlement.html   Decision hash, mint preview, exports
  assets/css/styles.css
  assets/js/role.js     Role switcher, remembered across pages
  assets/js/stress.js   Stress simulator calculations
```
Sample data only. Role view and stress model are mocked. Role switcher needs no server; it uses localStorage.
