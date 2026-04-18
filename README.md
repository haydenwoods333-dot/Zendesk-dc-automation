Modular Macro Framwork - Zendesk Dynamic Content
---

## Known Arthitectural Limitation

This framework was purpose-built to work within a specific constraint: the two-way API access required to connect Zendesk and VBASoftware directly is gated, either behind Zendesk's AI agents add on, behing VBAPI, or another system as verified by our dev ops

As a result, the system relies on a daily automated export from VBA Software, imported into Zendesk as custom objects, rather than a live real-time connection. All data accessed by this framework is therefore up to 24 hours old. This is a known tradeoff, not an oversight.

> A direct integration path may become available pending evaluation of VBAPI access and Zendesk's Advanced AI add-on.
---

## Overview

This project automates how Zendesk ticket responses are generated for claims, eligibility, and member requests. Instead of agents manually writing responses, the system uses Liquid templates and Python automation to push pre-built, personalized content directly into Zendesk Dynamic Content items.

The framework is modular. Each piece has a single, well-defined job:

- A MAIN CONTROLLER manages routing and variables
- SUBCONTROLLERS handle specific contact reasons
- CONTENT BLOCKS generate the actual response text
- COMPUTATION BLOCKS handle all math and derived fields separately

This separation keeps templates clean, testable, and easy to maintain.

### Why this approach was chosen

The ideal solution would be a live, real-time connection between VBASoftware and Zendesk using VBAPI on the VBA side and Zendesk's native integration tools on the other. That path was unavailable at the time of build. This framework was designed as the best available solution under those constraints, using only capabilities accessible on the current plan.

---

## How It Works

There are two phases: automation and rendering.

### Phase 1: Python automation (`build.py`)

1. The build script loads a shared library and the relevant Liquid template.
2. It combines them and pushes the result to the correct Zendesk Dynamic Content item via the Zendesk API.
3. This replaces the previous content and makes the updated template live.

### Phase 2: Ticket rendering (Liquid template)

1. Varibles are assigned from ticket fields at the top of the main controller.
2. Execution state is determined: the system checks for HIPAA flags, missing member data, or encryption requirements before proceeding.
3. Audience is identified: internal agent view vs. external customer-facing response.
4. A subcontroller is selected based on the contact reason (e.g., claim status, eligibility).
5. Content blocks are rendered: financial breakdowns, claim snapshots, and explanation codes are assembled.
6. Computations are applied: derived fields like member responsibility and plan payable amounts are calculated.

> DATA REFRESH
 All data rendered by these templates originates from a daily automated export from VBASoftware, imported into Zendesk custom objects. Claim status, eligibility, and member information may be up to 24 hours behind the source system.

---

## Component Roles

1. Main controller: Entry point for every template. Assigns all shared variables and determines execution state before anything else runs. 
2. Logic Gates: Guard conditions that stop or redirect execution. This handles HIPAA compliance checks, encryption requirements, and missing member scenarios. 
3. Subcontroller: One per contact reason. Manages routing and variable assignment specific to that workflow (e.g., claim status, eligibility).
4. Content Blocks: Predefined Dynamic Content items that generate the actual ticket response text (external comment or internal note).
5. Computation Blocks: Handle all math and derived field logic. This includes member responsibility, plan payable, etc. Keeping calculations here prevents logic from bleeding into content blocks.
6. Debug Controller: Enabled in sandbox only. Prints all assigned variables, execution state, and subcontroller path to help diagnose template issues before going live.

---

## Rules & Conventions

- All variables are assigned at the main controller level. Local assignments inside content blocks are only used when strictly necessary.
- All loops must be closed. Open loops may break rendering.
- Normalize all values: dates, statuses, currencies, and text fields must be formatted consistently before use.
- All math belongs in computaion blocks, not in content blocks or controllers.
- Use arrays with `| split: ","` for flexible structures when looping through multiple values (e.g., explanation codes).
- Format dates at the varible assignment stage, not inside content blocks.
- For object files, maintain structure based on the source object: member object, claim object, claim batch object.

---

## Setup & Installation

1. Clone the repository

```bash
git clone <repository_url>
cd project_root
```

2. Install dependencies

```bash
pip install requests
```

3. Configure credentials

Edit `config_sandbox.py`:

```python
SUBDOMAIN = "your_subdomain"
EMAIL = "your_email@example.com"
API_TOKEN = "your_api_token"
```

4. Map templates to Dynamic Content items

Edit `dynamic_contents.py`:

```python
DCS = {
    "claim_status.liquid": "Claim Status DC",
    "eligibility.liquid": "Eligibility DC",
}
```

5. Run the build script

```bash
python build.py
```

---

## Debugging & Testing

Enable debug mode at the top of any template to print a full diagnostic output: variable values, execution state, and subcontroller path:

```liquid
{% assign debug_mode = "enabled" %}
```

Always test in the sandbox environment before deploying to production. Debug output is for internal use only and must never be visible to customers.

---

## Adding New Templates

1. Add the new Liquid template to the `Liquid/` folder.
2. Register it in `dynamic_contents.py` by mapping the filename to its Dynamic Content item name.
3. Prepend the shared library content to the new template.
4. Run `build.py` to deploy.

---

## Known Limitations & Future Path

## Active limitations

Data is not real time

Dependent on internal expertise 

---

## Under evaluation

Direct VBA integration via VBAPI

Zendesk Advanced AI add-on

---

## Why This Approach

1. Maintainability: Modular structure means changes to one component don't ripple through the entire template. Each piece can be updated and tested in isolation.
2. Compliance: Built-in execution gates enforce HIPAA checks and encryption requirements before any content is rendered or sent.
3. Consistency: Computation blocks ensure derived fields are always calculated the same way, eliminating manual errors across ticket types.
4. Efficiency: Automated deployment via `build.py` removes the need to manually update Dynamic Content items in the Zendesk UI one by one.
