
[README.md](https://github.com/user-attachments/files/25538553/README.md)
========================================================
MODULAR MACRO FRAMEWORK – ZENDESK DYNAMIC CONTENT
========================================================
Execution Order:
1. Master Controller
2. Logic Gates / Execution State
3. Subcontrollers (per Contact Reason)
4. Content Blocks (Dynamic Content)
5. Computations / Derived Fields

========================================================
Component Roles:

- Controllers & Subcontrollers: 
  Handle routing, execution states, and variable assignments for the template.

- Content Blocks:
  Predefined text templates (Dynamic Content items) that generate the actual ticket output.

- Computations:
  Perform all calculations, derived fields, and data processing logic.

========================================================
Rules & Best Practices:

- Assign all variables at the top level (Main Controller)
  → Only assign variables inside content blocks if required locally.

- Use closed loops only

- Normalize all values
  → Dates, statuses, currencies, and text fields.

- All mathematical operations belong in Computation blocks
  → Keeps template logic clean.

- Utilize Debug Controller for sandbox testing
  → Prints variable values and execution path.

- Use arrays and {% raw %}| split: ","{% endraw %} for flexible structures
  → Example: looping through multiple explanation codes.

- Format dates under Variables assignment
  → Example: {% raw %}{% assign claim_received_date = claim.received_date | date: "%m/%d/%y" %}{% endraw %}

- For object files, maintain structure based on source object
  → Example: member object, claim object, claim batch object.

========================================================
Project Overview:

This project automates Zendesk Dynamic Content (DC) management and creates dynamic ticket responses for claims, eligibility, and member requests.

- Python script (`build.py`) loads Liquid templates, prepends shared library content, and pushes updates to Zendesk DC items.
- Liquid templates implement:
  - Variable assignment (from ticket fields)
  - Execution state and gating (HIPAA, encryption, missing member)
  - Subcontrollers based on contact_reason (claim_status, eligibility)
  - Dynamic content blocks (financial breakdown, claim snapshot, explanation codes)
  - Computations for derived fields (member responsibility, plan payable, etc.)
  - Debug mode for testing

========================================================
Execution Flow:

1. Python Automation:
   - Load library + template
   - Push/update DC via Zendesk API

2. Ticket Rendering (Liquid Template):
   - Assign variables from ticket fields
   - Determine execution_state (hipaa_denied, member_not_found, encryption, normal)
   - Select audience (internal vs external)
   - Route to subcontroller based on contact_reason
   - Render content blocks (financial breakdown, snapshots, etc.)
   - Apply computations for derived values
   - Optional debug output

========================================================
Installation & Setup:

1. Clone repository:
```bash
git clone <repository_url>
cd project_root
````

2. Install dependencies:

```bash
pip install requests
```

3. Configure credentials (`config_sandbox.py`):

```python
SUBDOMAIN = "your_subdomain"
EMAIL = "your_email@example.com"
API_TOKEN = "your_api_token"
```

4. Map templates to Dynamic Content items (`dynamic_contents.py`):

```python
DCS = {
    "claim_status.liquid": "Claim Status DC",
    "eligibility.liquid": "Eligibility DC",
}
```

5. Run build script:

```bash
python build.py
```

========================================================
Debugging & Testing:

* Enable debug mode in templates:

```liquid
{% assign debug_mode = "enabled" %}
```

* Outputs all assigned variables, execution state, and subcontroller paths.
* Recommended to test in **sandbox environment** before production.

========================================================
Benefits:

* Modular and maintainable template structure
* Automated DC deployment reduces manual effort
* Dynamic content generation for personalized ticket responses
* Built-in execution gates ensure HIPAA compliance and data security
* Computation blocks standardize derived fields and calculations

========================================================
Contributing:

* Add new Liquid templates in the `Liquid/` folder
* Update `dynamic_contents.py` mapping
* Prepend library content to new templates
* Run `build.py` to deploy

========================================================
License:

Copyright (c) 2026 Hayden Woods

All rights reserved.

This software and associated files are the exclusive property of Hayden Woods.  
Unauthorized copying, modification, distribution, or use is prohibited.
