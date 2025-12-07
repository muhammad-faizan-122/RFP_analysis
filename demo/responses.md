## Testing & results of Each Endpoint
### `**ingest**` Endpoint
**With filter metadata**:
Input:
No input is required

output:
```
{
  "message": "Ingestion completed successfully.",
  "total_chunks": 132
}
```

### `**query**` Endpoint

**EXAMPLE-1: Input query With filter metadata**:
Input 
```
{
  "user_query": "what will be the evaluation procedures?",
  "metadata": {
    "file_name": "RFP3.pdf",
    "company": "Edgemont Union Free School District",
    "project": "Controlled Testing & Inspections for District Wide Additions & Alterations"
  }
}
```

output response
```
{
  "user_query": "what will be the evaluation procedures?",
  "answer": "The evaluation procedures will be based on the following criteria for reviewing written proposals:\n1. General experience in the field.\n2. References.\n3. Qualifications and experience which most closely match the needs of the District.\n4. Satisfaction with proposal requirements.\n5. The competitiveness of applicant’s fee structure.",
  "reasoning": "Document-1\nRelevance: Yes\nReasoning: The document is titled \"EVALUATION PROCEDURES\" and details the criteria and process for evaluating applicants, directly addressing the user's query about evaluation procedures.",
  "extracted_requirements": [
    {
      "id": null,
      "metadata": {
        "company": "Edgemont Union Free School District",
        "file_name": "RFP3.pdf",
        "project": "CONTROLLED TESTING & INSPECTIONS FOR DISTRICT WIDE ADDITIONS & ALTERATIONS"
      },
      "page_content": "H.​ EVALUATION PROCEDURES\nThese proposals are being solicited through a fair and open process. Applicants who are willing to\nprovide the services described as requested above, shall be evaluated based on experience and\nqualifications as set forth in the criteria described below. For the selection of the finalist, the written\nproposals will be reviewed based on the following:\n1.​ General experience in the field.\n2.​ References.\n3.​ Qualifications and experience which most closely match the needs of the District.\n4.​ Satisfaction with proposal requirements.\n5.​ The competitiveness of applicant’s fee structure.",
      "type": "Document"
    }
  ]
}
```
**EXAMPLE-2: Without filter metadata**:

Input:
```
{
  "user_query": "what will be the evaluation procedures?",
  "metadata": {
    "file_name": "",
    "company": "",
    "project": ""
  }
}
```
Output:

```
{
  "user_query": "what will be the evaluation procedures?",
  "answer": "The evaluation procedures will involve reviewing written proposals based on the following criteria:\n\n*   **General experience in the field.**\n*   **References.**\n*   **Qualifications and experience which most closely match the needs of the District.**\n*   **Satisfaction with proposal requirements.**\n*   **The competitiveness of applicant’s fee structure.**\n*   **Experience and Qualifications of the Proposer:**\n    *   Demonstrating strong capabilities, experience, and reputation in similar undertakings.\n    *   Providing authoritative documentation of financial soundness and stability.\n    *   At least ten (10) years’ experience in providing construction management services on projects involving school district renovations, alterations, and/or additions.\n    *   At least ten (10) projects in school district expansions, renovations, and upgrades.\n*   **Ability to Implement District Projects Promptly:** Demonstrating an ability to carry out tasks and responsibilities in a prompt and efficient manner.\n\nProposals will also be reviewed for completeness prior to actual evaluation, and any deemed non-responsive to requests for information may be eliminated from further consideration.",
  "reasoning": "Document-1\nRelevance: Yes\nReasoning: The document explicitly outlines \"EVALUATION PROCEDURES\" and lists specific criteria (experience, qualifications, references, proposal satisfaction, fee structure) used for evaluation.\n\nDocument-2\nRelevance: Yes\nReasoning: The document details \"Proposal Evaluation Criteria\" and describes the specific criteria (experience, qualifications, ability to implement projects promptly) on which proposals will be evaluated.\n\nDocument-3\nRelevance: No\nReasoning: This document focuses on \"PROPOSAL FORMAT AND CONTENTS\" and the pre-screening process for completeness, not the actual procedures or criteria for evaluating the content of the proposals themselves.",
  "extracted_requirements": [
    {
      "id": null,
      "metadata": {
        "company": "Edgemont Union Free School District",
        "file_name": "RFP3.pdf",
        "project": "CONTROLLED TESTING & INSPECTIONS FOR DISTRICT WIDE ADDITIONS & ALTERATIONS"
      },
      "page_content": "H.​ EVALUATION PROCEDURES\nThese proposals are being solicited through a fair and open process. Applicants who are willing to\nprovide the services described as requested above, shall be evaluated based on experience and\nqualifications as set forth in the criteria described below. For the selection of the finalist, the written\nproposals will be reviewed based on the following:\n1.​ General experience in the field.\n2.​ References.\n3.​ Qualifications and experience which most closely match the needs of the District.\n4.​ Satisfaction with proposal requirements.\n5.​ The competitiveness of applicant’s fee structure.",
      "type": "Document"
    },
    {
      "id": null,
      "metadata": {
        "file_name": "RFP2.pdf",
        "company": "EAST ISLIP UNION FREE SCHOOL DISTRICT",
        "project": "CONSTRUCTION MANAGEMENT SERVICES"
      },
      "page_content": "C. Proposal Evaluation Criteria\nProposals will be evaluated on the basis of the following criteria:\n1. Experience and Qualifications of the Proposer: Consideration will be given to\nproposers demonstrating strong capabilities, experience and reputation in\nundertakings similar to those described in this RFP, and providing authoritative\ndocumentation of their financial soundness and stability. Similar experience will\nbe understood to include, but not be limited to:\na. At least ten (10) years’ experience in the provision of construction\nmanagement services on projects involving school district renovations,\nalterations and/or additions;\nb. At least ten (10) projects in school district expansions, renovations and\nupgrades.\n2. Ability to Implement District Projects Promptly: Preference will be given to\nproposals demonstrating an ability to carry out the tasks and responsibilities\noutlined in the proposal in a prompt and efficient manner. The capability of the",
      "type": "Document"
    },
    {
      "id": null,
      "metadata": {
        "project": "CONSTRUCTION MANAGEMENT SERVICES",
        "file_name": "RFP2.pdf",
        "company": "EAST ISLIP UNION FREE SCHOOL DISTRICT"
      },
      "page_content": "VI. PROPOSAL FORMAT AND CONTENTS\nProposals must be submitted in the format outlined in this section. Each of the described parts\nand sections must be completed in full (except those sections described as optional). Each\nproposal will be reviewed to determine if it is complete prior to actual evaluation. The School\nDistrict reserves the right to eliminate from further consideration any proposal deemed to be nonresponsive to the requests for information contained herein. Each of the parts and sections\ndescribed below should begin on a separate page, and each page should state the name of the\nproposer in the upper right hand corner.",
      "type": "Document"
    }
  ]
}
```
**EXAMPLE-3: General Query or other than RFP**:
Input: 
```
{
  "user_query": "Hi, how are you doing today",
  "metadata": {
    "file_name": "",
    "company": "",
    "project": ""
  }
}

```
Output:
```

{
  "user_query": "Hi, how are you doing today",
  "answer": "Hi there! I'm doing great, thanks for asking! As an AI, I don't have feelings, but I'm ready to help. How can I assist you today?",
  "reasoning": "",
  "extracted_requirements": []
}
```

### `**eval_rfp**` Endpoint
Example-1 **With filter metadata**:
Input 

```
{
  "user_query": "what will be the evaluation procedures?",
  "answer": "The evaluation procedures will be based on the following criteria for reviewing written proposals:\n1. General experience in the field.\n2. References.\n3. Qualifications and experience which most closely match the needs of the District.\n4. Satisfaction with proposal requirements.\n5. The competitiveness of applicant’s fee structure.",
  "reasoning": "Document-1\nRelevance: Yes\nReasoning: The document is titled \"EVALUATION PROCEDURES\" and details the criteria and process for evaluating applicants, directly addressing the user's query about evaluation procedures.",
  "extracted_requirements": [
    {
      "id": null,
      "metadata": {
        "company": "Edgemont Union Free School District",
        "file_name": "RFP3.pdf",
        "project": "CONTROLLED TESTING & INSPECTIONS FOR DISTRICT WIDE ADDITIONS & ALTERATIONS"
      },
      "page_content": "H.​ EVALUATION PROCEDURES\nThese proposals are being solicited through a fair and open process. Applicants who are willing to\nprovide the services described as requested above, shall be evaluated based on experience and\nqualifications as set forth in the criteria described below. For the selection of the finalist, the written\nproposals will be reviewed based on the following:\n1.​ General experience in the field.\n2.​ References.\n3.​ Qualifications and experience which most closely match the needs of the District.\n4.​ Satisfaction with proposal requirements.\n5.​ The competitiveness of applicant’s fee structure.",
      "type": "Document"
    }
  ]
}
```

output:
```
{
  "evaluation": {
    "answer_relevancy_score": 96.67,
    "reasoning_quality_score": 90,
    "retrieved_relevancy_score": 100
  }
}
```

Input:
```
{
  "user_query": "what will be the evaluation procedures?",
  "answer": "The evaluation procedures will involve reviewing written proposals based on the following criteria:\n\n*   **General experience in the field.**\n*   **References.**\n*   **Qualifications and experience which most closely match the needs of the District.**\n*   **Satisfaction with proposal requirements.**\n*   **The competitiveness of applicant’s fee structure.**\n*   **Experience and Qualifications of the Proposer:**\n    *   Demonstrating strong capabilities, experience, and reputation in similar undertakings.\n    *   Providing authoritative documentation of financial soundness and stability.\n    *   At least ten (10) years’ experience in providing construction management services on projects involving school district renovations, alterations, and/or additions.\n    *   At least ten (10) projects in school district expansions, renovations, and upgrades.\n*   **Ability to Implement District Projects Promptly:** Demonstrating an ability to carry out tasks and responsibilities in a prompt and efficient manner.\n\nProposals will also be reviewed for completeness prior to actual evaluation, and any deemed non-responsive to requests for information may be eliminated from further consideration.",
  "reasoning": "Document-1\nRelevance: Yes\nReasoning: The document explicitly outlines \"EVALUATION PROCEDURES\" and lists specific criteria (experience, qualifications, references, proposal satisfaction, fee structure) used for evaluation.\n\nDocument-2\nRelevance: Yes\nReasoning: The document details \"Proposal Evaluation Criteria\" and describes the specific criteria (experience, qualifications, ability to implement projects promptly) on which proposals will be evaluated.\n\nDocument-3\nRelevance: No\nReasoning: This document focuses on \"PROPOSAL FORMAT AND CONTENTS\" and the pre-screening process for completeness, not the actual procedures or criteria for evaluating the content of the proposals themselves.",
  "extracted_requirements": [
    {
      "id": null,
      "metadata": {
        "company": "Edgemont Union Free School District",
        "file_name": "RFP3.pdf",
        "project": "CONTROLLED TESTING & INSPECTIONS FOR DISTRICT WIDE ADDITIONS & ALTERATIONS"
      },
      "page_content": "H.​ EVALUATION PROCEDURES\nThese proposals are being solicited through a fair and open process. Applicants who are willing to\nprovide the services described as requested above, shall be evaluated based on experience and\nqualifications as set forth in the criteria described below. For the selection of the finalist, the written\nproposals will be reviewed based on the following:\n1.​ General experience in the field.\n2.​ References.\n3.​ Qualifications and experience which most closely match the needs of the District.\n4.​ Satisfaction with proposal requirements.\n5.​ The competitiveness of applicant’s fee structure.",
      "type": "Document"
    },
    {
      "id": null,
      "metadata": {
        "file_name": "RFP2.pdf",
        "company": "EAST ISLIP UNION FREE SCHOOL DISTRICT",
        "project": "CONSTRUCTION MANAGEMENT SERVICES"
      },
      "page_content": "C. Proposal Evaluation Criteria\nProposals will be evaluated on the basis of the following criteria:\n1. Experience and Qualifications of the Proposer: Consideration will be given to\nproposers demonstrating strong capabilities, experience and reputation in\nundertakings similar to those described in this RFP, and providing authoritative\ndocumentation of their financial soundness and stability. Similar experience will\nbe understood to include, but not be limited to:\na. At least ten (10) years’ experience in the provision of construction\nmanagement services on projects involving school district renovations,\nalterations and/or additions;\nb. At least ten (10) projects in school district expansions, renovations and\nupgrades.\n2. Ability to Implement District Projects Promptly: Preference will be given to\nproposals demonstrating an ability to carry out the tasks and responsibilities\noutlined in the proposal in a prompt and efficient manner. The capability of the",
      "type": "Document"
    },
    {
      "id": null,
      "metadata": {
        "project": "CONSTRUCTION MANAGEMENT SERVICES",
        "file_name": "RFP2.pdf",
        "company": "EAST ISLIP UNION FREE SCHOOL DISTRICT"
      },
      "page_content": "VI. PROPOSAL FORMAT AND CONTENTS\nProposals must be submitted in the format outlined in this section. Each of the described parts\nand sections must be completed in full (except those sections described as optional). Each\nproposal will be reviewed to determine if it is complete prior to actual evaluation. The School\nDistrict reserves the right to eliminate from further consideration any proposal deemed to be nonresponsive to the requests for information contained herein. Each of the parts and sections\ndescribed below should begin on a separate page, and each page should state the name of the\nproposer in the upper right hand corner.",
      "type": "Document"
    }
  ]
}
```
Output:
```

{
  "evaluation": {
    "answer_relevancy_score": 100,
    "reasoning_quality_score": 96.67,
    "retrieved_relevancy_score": 66.66666666666666
  }

}```