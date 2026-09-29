Here is a detailed comparison table and analysis contrasting the concepts introduced in **Dexter Horthy's video** ("Everything We Got Wrong About Research-Plan-Implement") with those in the **Agent-mastery** repository.

---

### Comparative Overview: Video vs. Repository

| Dimension | Video: Dexter Horthy (RPI to CRISPY) | GitHub Repo: `Agent-mastery` |
| :--- | :--- | :--- |
| **Primary Focus & Domain** | General software engineering workflows and coding agent methodologies for enterprise software development. | Domain-specific, specification-driven framework for deterministic SAS-to-Python migrations. |
| **Core Workflow Framework** | **CRISPY** (Questions, Research, Design, Structure, Plan, Work, Implement, PR) replacing **RPI** (Research, Plan, Implement). | **5-Act Lifecycle**: Align, Reuse/Reconstruct, Build/Prove, Adapt/Operate, Improve. |
| **Prompt & Skill Architecture** | Moving away from 85+ instruction mega-prompts; using smaller, focused prompts (<40 instructions) controlled by deterministic code flow. | **20 verb-based skills** with thin prompts that route work to a single authorized skill per prompt. |
| **Context Window Strategy** | Avoiding the "Dumb Zone" by keeping context windows under 40–60%; hiding task tickets during research to prevent biased/opinionated output. | Isolating contexts per stage and keeping durable state in committed artifacts rather than overloading a single prompt. |
| **Human Alignment & Governance** | Aligning on short, 200-line **Design Discussions** and **Structure Outlines** (like C header files) instead of reading 1,000-line plan files. | Mandatory **human approval gates** and explicit artifact contracts before advancing between stages. |
| **Planning Approach** | **Vertical Planning**: Breaking changes into small, end-to-end testable slices rather than horizontal layer-by-layer planning (DB → Service → UI). | Stage-specific artifacts and gates ensure each act produces a concrete, reviewable deliverable before the next step. |
| **Code Review & Quality** | **"Read the Code, No Slop"**: Developers must review and own generated production code rather than delegating review to agents. | **Local Parity & Tie-Out**: Deterministic validation against approved fixtures, contracts, and evidence rather than subjective review alone. |
| **Recovery & Error Handling** | Resteering agents early during the 200-line design phase before 2,000 lines of bad code are generated. | **Bounded Recovery Loop**: Triggered on `FAIL` or `BLOCKED` via ingest → diagnose → repair → review → retry. |
| **Learning & Cross-Task Memory** | Preserving intent across static markdown assets instead of relying on lossy autocompaction. | **Governed Learning Memory**: Cross-migration advisory layer turning accepted evidence into audit-safe observations and patterns. |

---

### Key Conceptual Insights

#### 1. Workflow Evolution (CRISPY vs. 5-Act Migration Lifecycle)
* **Video (CRISPY)**: Dexter Horthy explains that simple **RPI (Research-Plan-Implement)** breaks down because agents can skip intermediate alignment steps when overloaded with instructions. CRISPY breaks planning into distinct, lightweight phases — **Questions → Research → Design Discussion → Structure Outline → Plan** — to force human-agent alignment early.
* **Repo (5-Act Lifecycle)**: Keshav Nath's framework uses a structured lifecycle (**Align → Reconstruct → Build/Prove → Adapt → Improve**) designed specifically for deterministic SAS-to-Python migrations. Each phase produces explicit JSON/YAML artifacts before progression to the next stage.

#### 2. Instruction Budgets & Control Flow Architecture
* **Video**: Highlights that frontier LLMs struggle when exceeding an instruction budget of ~150–200 instructions. The solution is to use code/deterministic control flow instead of asking the prompt to manage everything.
* **Repo**: Implements this exact principle by keeping commands modular. Prompts act purely as routers (`.github/prompts/`), while individual skills (`.github/skills/`) execute focused tasks and update durable state.

#### 3. Human Leverage & Quality Control ("No Slop" vs. Contract-Driven Parity)
* **Video**: Emphasizes that "slop" happens when developers do not read the generated code or rely on reading massive plan files. Real leverage comes from reading a 200-line **Design Discussion** upfront and steering early.
* **Repo**: Enforces quality through deterministic tie-out contracts (`config/tieout.yaml`). Instead of subjective code review alone, the system validates exact numerical parity against SAS oracle evidence.

#### 4. Memory and Patterns
* **Video**: Recommends saving context into static markdown documents (Design, Outline, Plan) rather than relying on automatic context compaction.
* **Repo**: Introduces a **Governed Learning Memory** layer. When recurring migration patterns or failures occur, the framework generates audit-safe observations and candidate patterns, which must pass independent review and human promotion before becoming reusable guidance.

---
