# AI Prompt Templates for HCC Coding Assistant

CONDITION_EXTRACTION_PROMPT = """
You are an expert medical coder specializing in HCC (Hierarchical Condition Category) coding.

Analyze this physician documentation and extract:
1. All medical conditions mentioned
2. Specificity level (specific vs vague)
3. Chronic vs acute nature
4. Severity indicators
5. Complications or comorbidities

Physician Notes: "{input_text}"

For each condition found, determine:
- Is it documented specifically enough for accurate ICD coding?
- Is it chronic (needs annual HCC recapture)?
- Are there complications that might map to higher-value HCC codes?

Respond in structured format with actionable coding recommendations.
"""

ICD_IMPROVEMENT_PROMPT = """
You are helping a physician choose the most appropriate ICD-10 code for accurate HCC risk adjustment.

Current situation:
- Physician thinking: "{physician_input}"
- Current ICD consideration: "{current_icd}"
- Clinical notes: "{clinical_notes}"

Available ICD options that map to HCC codes:
{hcc_options}

Provide specific recommendation:
1. Best ICD code choice and why
2. HCC category it maps to
3. RAF score impact
4. Documentation requirements to support this code
5. Any missing information needed

Focus on maximizing appropriate risk adjustment while maintaining coding compliance.
"""

MEAT_DOCUMENTATION_PROMPT = """
Review this clinical documentation for MEAT criteria compliance:

M - Monitor: Evidence of ongoing monitoring
E - Evaluate: Assessment of condition status
A - Assess/Address: Clinical assessment or addressing the condition
T - Treat: Treatment plans or interventions

Clinical Notes: "{clinical_notes}"
Condition: "{condition}"

Analyze if MEAT criteria are met and suggest specific documentation improvements to ensure HCC code defensibility during RADV audits.
"""

HCC_RECAPTURE_PROMPT = """
Analyze patient history for HCC recapture opportunities:

Patient History: "{patient_history}"
Current Visit Notes: "{current_notes}"
Previous HCC Codes: {previous_hccs}

Identify:
1. Chronic conditions that need annual recapture
2. Missing conditions that should be addressed
3. Specific documentation needed for each condition
4. RAF score impact of missing recaptures

Provide actionable checklist for this patient encounter.
"""
