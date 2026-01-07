---

# Power Apps Canvas App Agentic AI Generation Code Reviewer

An automated "Critic" and "Linter" framework designed to ensure AI-generated Power Apps YAML and Power Fx code is actually usable, syntactically correct, and ready for import.

## 🚀 The Problem
Large Language Models (LLMs) often struggle with the specific nuances of Power Apps source code (YAML). Common issues include:
*   **Missing Formula Prefixes:** Forgetting the `=` sign for properties containing Power Fx formulas.
*   **Property Hallucinations:** Using properties that don't exist for specific controls (e.g., `OnClick` instead of `OnSelect`).
*   **Syntax Errors:** Incorrectly nested YAML or improperly escaped strings in Power Fx.
*   **Naming Issues:** Using spaces or invalid characters in control names.

## 🛠 The Solution
This project implements an **Agentic Reviewer Loop**. Instead of relying on a single AI generation, we use a multi-agent approach where a "Reviewer Agent" validates the output against a set of hard rules and "Agentic Docs" before the code ever reaches the developer.

### Recommended Stack
*   **Orchestration:** [Gravity](https://usegravity.ai/) (Recommended) – Use Gravity to build the multi-agent workflow where one agent generates and another (using this repo) reviews and corrects.
*   **Logic:** Python (for YAML parsing and regex validation).
*   **Documentation:** Markdown-based "Agent Docs" to provide the LLM with the latest Power Apps schemas.

---

## 📂 Project Structure

```text
├── aidocs/                # Knowledge base for the Agents
│   ├── rules.md           # The "Global Laws" (Formula syntax, naming conventions)
│   ├── control_catalog.md # Valid properties for Buttons, Galleries, etc.
│   └── common_fixes.md    # Solutions to frequent AI hallucinations
├── scripts/               # Validation scripts
│   └── reviewer.py        # Python script to check YAML integrity and = signs
├── workspace/             # Output folder for validated .pa.yaml files
└── instructions.md        # The System Prompt for the Gravity Agent
```

---

## 🤖 Usage with Gravity

To get the most out of this project, we recommend using **Gravity** for agentic generation. 

1.  **Create a Gravity Workflow:** Setup a sequence with at least two nodes.
2.  **The Generator Node:** Task an LLM to generate the Power Apps YAML.
3.  **The Reviewer Node:** Provide this agent with the files in `/aidocs`. Tell the agent to run the `reviewer.py` script (or simulate its logic) to check the Generator's output.
4.  **The Correction Loop:** If the Reviewer finds errors (like a missing `=` in a `Filter()` function), Gravity should route the output back to the Generator for a fix.

---

## 📏 Core Reviewer Rules (The "Validator" Logic)

The Reviewer agent is trained to enforce these non-negotiable rules:

1.  **The Formula Rule:** Every property containing a Power Fx function (e.g., `Navigate`, `Filter`, `Lookup`) **must** start with an `=` sign.
    *   ❌ `Text: "User: " & User().FullName`
    *   ✅ `Text: ="User: " & User().FullName`
2.  **No Spaces:** All Control names must be alphanumeric with no spaces (e.g., `btn_Submit_Main`).
3.  **YAML Indentation:** Strict adherence to the Power Apps source code indentation schema.
4.  **Enum Correctness:** Ensure Enums like `Color.Blue` or `DisplayMode.Edit` are used rather than plain strings.

---

## 🛠 Setup & Contribution

1.  **Clone the repo:**
    ```bash
    git clone https://github.com/your-username/powerapps-agentic-reviewer.git
    ```
2.  **Add your "Hard Rules":** 
    Update `aidocs/rules.md` whenever you find a new "hallucination" the AI repeats.
3.  **Run the local validator:**
    ```bash
    python scripts/reviewer.py workspace/my_app_view.yaml
    ```

---

## 📄 License
MIT

---
*Created to bridge the gap between AI imagination and Power Apps reality.*
