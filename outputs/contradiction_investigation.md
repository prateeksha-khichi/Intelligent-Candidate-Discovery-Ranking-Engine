# Contradiction Logic Investigation

## Exact Logic Used Previously:
```python
def get_category(text):
    text = text.lower()
    if 'qa' in text or 'quality assurance' in text or 'tester' in text or 'manual testing' in text: return 'qa'
    if 'sales' in text or 'quota' in text or 'arr' in text or 'account executive' in text: return 'sales'
    if 'support' in text or 'customer service' in text or 'help desk' in text: return 'support'
    if 'frontend' in text or 'backend' in text or 'software engineer' in text or 'developer' in text or 'fullstack' in text: return 'swe'
    return 'unknown'
```

## 15 Random Flagged Examples:

### Example 1 (CAND_0069023)
- **Job Title:** `full stack developer`
- **Title Categorized As:** `swe`
- **Job Description:** test automation and qa engineering for a fintech product. built and maintained the end-to-end test suite using selenium and pytest, plus the load-testing setup using locust. worked closely with developers on testability patterns and with product on acceptance criteria. recent work has been on shifting test responsibility into the dev team — moving from qa-as-gate to qa-as-coach. career has been entirely in qa/test engineering.
- **Desc Categorized As:** `qa`
- **Why Flagged:** Title category 'swe' != Description category 'qa' within the same job entry.

### Example 2 (CAND_0012103)
- **Job Title:** `qa engineer`
- **Title Categorized As:** `qa`
- **Job Description:** frontend engineering at a media company. react, typescript, and the typical surrounding tooling (webpack, jest, cypress). built the company's design system from scratch and led the migration from a legacy angularjs app. strong on the frontend craft — accessibility, performance, animations — but limited backend exposure.
- **Desc Categorized As:** `swe`
- **Why Flagged:** Title category 'qa' != Description category 'swe' within the same job entry.

### Example 3 (CAND_0002568)
- **Job Title:** `sales executive`
- **Title Categorized As:** `sales`
- **Job Description:** customer support team lead at a saas product. managed a team of 8 support agents handling tier-1 and tier-2 tickets; owned the escalation process to engineering and the customer-feedback loop to product. built out the support knowledge base and the agent training program. strong on the people-management side and the process side; lighter on technical depth beyond product expertise.
- **Desc Categorized As:** `support`
- **Why Flagged:** Title category 'sales' != Description category 'support' within the same job entry.

### Example 4 (CAND_0079842)
- **Job Title:** `software engineer`
- **Title Categorized As:** `swe`
- **Job Description:** test automation and qa engineering for a fintech product. built and maintained the end-to-end test suite using selenium and pytest, plus the load-testing setup using locust. worked closely with developers on testability patterns and with product on acceptance criteria. recent work has been on shifting test responsibility into the dev team — moving from qa-as-gate to qa-as-coach. career has been entirely in qa/test engineering.
- **Desc Categorized As:** `qa`
- **Why Flagged:** Title category 'swe' != Description category 'qa' within the same job entry.

### Example 5 (CAND_0029455)
- **Job Title:** `software engineer`
- **Title Categorized As:** `swe`
- **Job Description:** test automation and qa engineering for a fintech product. built and maintained the end-to-end test suite using selenium and pytest, plus the load-testing setup using locust. worked closely with developers on testability patterns and with product on acceptance criteria. recent work has been on shifting test responsibility into the dev team — moving from qa-as-gate to qa-as-coach. career has been entirely in qa/test engineering.
- **Desc Categorized As:** `qa`
- **Why Flagged:** Title category 'swe' != Description category 'qa' within the same job entry.

### Example 6 (CAND_0026459)
- **Job Title:** `customer support`
- **Title Categorized As:** `support`
- **Job Description:** marketing leadership role at a b2b saas company. owned the demand-generation function — content marketing, paid acquisition, seo, email nurture. built and managed a team of 5 across content, performance marketing, and marketing operations. worked closely with sales on lead-quality definitions and the sdr-handoff process. recent focus has been on account-based marketing for our enterprise segment.
- **Desc Categorized As:** `sales`
- **Why Flagged:** Title category 'support' != Description category 'sales' within the same job entry.

### Example 7 (CAND_0024105)
- **Job Title:** `sales executive`
- **Title Categorized As:** `sales`
- **Job Description:** customer support team lead at a saas product. managed a team of 8 support agents handling tier-1 and tier-2 tickets; owned the escalation process to engineering and the customer-feedback loop to product. built out the support knowledge base and the agent training program. strong on the people-management side and the process side; lighter on technical depth beyond product expertise.
- **Desc Categorized As:** `support`
- **Why Flagged:** Title category 'sales' != Description category 'support' within the same job entry.

### Example 8 (CAND_0015195)
- **Job Title:** `customer support`
- **Title Categorized As:** `support`
- **Job Description:** marketing leadership role at a b2b saas company. owned the demand-generation function — content marketing, paid acquisition, seo, email nurture. built and managed a team of 5 across content, performance marketing, and marketing operations. worked closely with sales on lead-quality definitions and the sdr-handoff process. recent focus has been on account-based marketing for our enterprise segment.
- **Desc Categorized As:** `sales`
- **Why Flagged:** Title category 'support' != Description category 'sales' within the same job entry.

### Example 9 (CAND_0079372)
- **Job Title:** `full stack developer`
- **Title Categorized As:** `swe`
- **Job Description:** test automation and qa engineering for a fintech product. built and maintained the end-to-end test suite using selenium and pytest, plus the load-testing setup using locust. worked closely with developers on testability patterns and with product on acceptance criteria. recent work has been on shifting test responsibility into the dev team — moving from qa-as-gate to qa-as-coach. career has been entirely in qa/test engineering.
- **Desc Categorized As:** `qa`
- **Why Flagged:** Title category 'swe' != Description category 'qa' within the same job entry.

### Example 10 (CAND_0011137)
- **Job Title:** `qa engineer`
- **Title Categorized As:** `qa`
- **Job Description:** frontend engineering at a media company. react, typescript, and the typical surrounding tooling (webpack, jest, cypress). built the company's design system from scratch and led the migration from a legacy angularjs app. strong on the frontend craft — accessibility, performance, animations — but limited backend exposure.
- **Desc Categorized As:** `swe`
- **Why Flagged:** Title category 'qa' != Description category 'swe' within the same job entry.

### Example 11 (CAND_0072963)
- **Job Title:** `sales executive`
- **Title Categorized As:** `sales`
- **Job Description:** customer support team lead at a saas product. managed a team of 8 support agents handling tier-1 and tier-2 tickets; owned the escalation process to engineering and the customer-feedback loop to product. built out the support knowledge base and the agent training program. strong on the people-management side and the process side; lighter on technical depth beyond product expertise.
- **Desc Categorized As:** `support`
- **Why Flagged:** Title category 'sales' != Description category 'support' within the same job entry.

### Example 12 (CAND_0079777)
- **Job Title:** `qa engineer`
- **Title Categorized As:** `qa`
- **Job Description:** android mobile development using java and (more recently) kotlin at a consumer-app company. built and maintained multiple production features including the main shopping flow, push notification system, and the offline-first sync layer. comfortable with the android framework, jetpack components, and the typical patterns (mvvm, hilt, coroutines). my career has been entirely on mobile so far; interested in expanding into broader backend or platform engineering.
- **Desc Categorized As:** `swe`
- **Why Flagged:** Title category 'qa' != Description category 'swe' within the same job entry.

### Example 13 (CAND_0096354)
- **Job Title:** `sales executive`
- **Title Categorized As:** `sales`
- **Job Description:** customer support team lead at a saas product. managed a team of 8 support agents handling tier-1 and tier-2 tickets; owned the escalation process to engineering and the customer-feedback loop to product. built out the support knowledge base and the agent training program. strong on the people-management side and the process side; lighter on technical depth beyond product expertise.
- **Desc Categorized As:** `support`
- **Why Flagged:** Title category 'sales' != Description category 'support' within the same job entry.

### Example 14 (CAND_0058631)
- **Job Title:** `backend engineer`
- **Title Categorized As:** `swe`
- **Job Description:** built and maintained data pipelines on apache airflow processing ~500gb of daily transactional data across 12 source systems. worked extensively with spark (pyspark) for batch processing and dbt for the transformation/modeling layer in our snowflake warehouse. owned the on-call rotation for data quality issues — wrote most of the data quality checks that detect schema drift and unusual volume changes. the pipeline supports the analytics team and a few internal ml models.
- **Desc Categorized As:** `support`
- **Why Flagged:** Title category 'swe' != Description category 'support' within the same job entry.

### Example 15 (CAND_0009624)
- **Job Title:** `software engineer`
- **Title Categorized As:** `swe`
- **Job Description:** implemented streaming data pipelines on kafka and spark streaming for a real-time user-activity processing platform. designed the schema-registry integration, the watermark/state management approach, and the deduplication logic for late-arriving events. worked closely with the data science team to make sure feature pipelines aligned with what their models needed. most of my career has been data engineering, with some adjacent ml exposure.
- **Desc Categorized As:** `sales`
- **Why Flagged:** Title category 'swe' != Description category 'sales' within the same job entry.

