# GitHub Copilot Instructions

All agent rules, coding guidelines, safety guardrails, repository references, and skill pointers for this project are maintained centrally in:
👉 **[AGENTS.md](../AGENTS.md)**

### Critical Directives:
1. **Follow [AGENTS.md](../AGENTS.md) as the Single Source of Truth:** Read and strictly adhere to the guidelines in [AGENTS.md](../AGENTS.md).
2. **Treat ROM Information as Science:** Never guess, assume, or hallucinate. In binary ROM hacking, hallucinations, guesswork, and imprecise approximations are **catastrophically destructive**. If an address, opcode, flag, coordinate, or parameter is not 100% verified, **use raw hex or explicitly state that you do not know**.
3. **Never Invent Names:** Every symbol or constant must trace back to [in/core/main.evs](../in/core/main.evs) or raw disassembly.
4. **File Editing Safety:** Never edit project source files unless the user explicitly names the target file.
5. **Use On-Demand Skills:** Refer to `.agents/skills/<skill-name>/SKILL.md` for specific domain procedures (memory mapping, Asar patching, Mesen2 debugging, testing, emoji data classification).
