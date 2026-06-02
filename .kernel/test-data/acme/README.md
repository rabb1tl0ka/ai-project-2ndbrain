# ACME Test Data

Synthetic test data for validating the multi-SOW bootstrap architecture.

## Scenario

**Client**: ACME Corp — mid-size retail company
**Engagement**: AI transformation across two SOWs

| SOW | Name | Status | Period |
|-----|------|--------|--------|
| sow1 | AI Readiness Assessment | Completed | Nov–Dec 2025 |
| sow2 | Customer Service Bot POC | Active | Jan–Mar 2026 |

## People

| Name | Company | Role |
|------|---------|------|
| Bruno Costa | Loka | TPM |
| Sara Kim | Loka | ML Lead |
| David Chen | ACME | CTO |
| Maria Lopez | ACME | Head of Customer Experience |
| Janet Walsh | ACME | VP Operations |

## Intentional tensions (to validate bootstrap gap detection)

1. **Missing deliverable**: SOW1 commits to a competitive analysis — never discussed in any meeting
2. **Scope creep**: SOW2 meetings discuss inventory forecasting — explicitly out of scope in SOW2
3. **Missing stakeholder**: Janet Walsh is named in SOW1 but never appears in any meeting or Slack
4. **Timeline drift**: SOW2 deadline is March 31 but Feb meeting notes suggest they're behind

## How to set this up in Google Drive

1. Create two Drive folders:
   - `ACME SOW1 Meeting Notes` → upload the 2 files from `sow1/meetings/`
   - `ACME SOW2 Meeting Notes` → upload the 2 files from `sow2/meetings/`

2. Upload the SOW docs anywhere accessible in Drive:
   - `sow1/ACME SOW1 - AI Readiness Assessment.md`
   - `sow2/ACME SOW2 - Customer Service Bot POC.md`

3. Note the folder URLs and SOW doc URLs — you'll need them for `/onboard`.

## /onboard config for this test

```
PROJECT_NAME: ACME
CLIENT_NAME: ACME Corp
ENGAGEMENT_TYPE: AI Transformation
ENGAGEMENT_CONTEXT: Loka is helping ACME Corp assess their AI readiness and build a customer service chatbot POC.
OWNER_NAME: Bruno Costa
OWNER_HANDLE: @bruno
OWNER_ROLE: TPM
SOWs: sow1, sow2
```

SOW1 config:
```
DRIVE_FOLDER: <your sow1 meetings folder URL>
SOW_DOC_URL: <your sow1 doc URL>
SLACK_CHANNELS: #acme-sow1
```

SOW2 config:
```
DRIVE_FOLDER: <your sow2 meetings folder URL>
SOW_DOC_URL: <your sow2 doc URL>
SLACK_CHANNELS: #acme-sow2
```
