# AL - Agentic Lender

Year 3 Group Project 2026

## Team & Subsystem Ownership

| Member | Primary Subsystem | Responsibilities |
|---|---|---|
| Kian Le Roux | AL-Web (React portal) | Broker & underwriter UI, system design, flow mapping |
| Rebecca Lordan | AL-Mobile (Android, Kotlin) | Borrower app, functional specs, screen design |
| Eldict Koonan John | AL-Core & Ledger (Firebase + Blockchain) | Database, smart contracts, custom feature, project report |
| Dimitar Bodurov | AL-AI Engine (Python) | ML valuation model, multi-agent AI committee, UI wireframes |

## Shared Responsibilities

- Documentation - each member documents their own subsystem
- Testing - unit testing per subsystem + group integration testing
- Sprint planning - all members attend stand-ups and retrospectives
- Presentation - all members present their subsystem in the final demo

## Subsystems

- **AL-Mobile** (Android, Kotlin) - Borrower app for applying, tracking, and messaging
- **AL-Web** (React, Tailwind CSS) - Broker & underwriter web portal
- **AL-Core & Ledger** (Firebase + Solidity) - Database, auth, blockchain settlement
- **AL-AI Engine** (Python) - ML property valuation & multi-agent underwriting

## Custom Feature

**Green Mortgage Smart Incentive** - The Solidity smart contract checks the property's BER rating at loan minting. If the home is energy-efficient (BER A or B), it automatically applies a 0.25% APR discount to the digital loan note.

## Project Management & Documentation

- **Trello:** https://trello.com/b/A6dYXHja (Week 3 tracking)
- **Jira:** Migration planned for Sprint 1
- **Confluence:** Project reports, meeting notes, and design docs
- **GitHub:** Code repository + documentation storage

## Infrastructure & Dev Environment

| Purpose | Tool |
|---|---|
| Communication | Trello / Jira / Microsoft Teams |
| Documentation | Confluence, Google Docs, Word, GitHub |
| Code management | Git (via GitHub) |
| Mobile development | Android Studio, Kotlin |
| Web development | VS Code, React, Tailwind CSS |
| Backend / AI | VS Code, Python (Flask/FastAPI), CrewAI / AutoGen / LangGraph |
| Blockchain | Hardhat, Solidity, Ethers.js / Web3.py |
| Database / Auth | Firebase (Firestore + Auth) |
| Testing | Manual QA + Jest (web), JUnit (mobile) |
| Deployment | Firebase Hosting, Polygon Amoy / Arbitrum Sepolia testnet |

## Week 3 Deliverables (Due 4 Oct)

| Deliverable | Status |
|---|---|
| Product Backlog | Completed |
| Mock-up / Prototype | Completed (mobile + desktop wireframes) |
| Infrastructure outline | Completed (GitHub, Trello, dev environment plan) |
