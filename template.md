# Threat Model Report: {tm.name}

## 1. Identified Threats

{findings:repeat:
### {{item.description}}
* **Severity:** {{item.severity}}
* **Mitigation Strategy:** {{item.mitigations}}

---
}

## 2. Data Flows
{dataflows:repeat:
* **Flow:** {{item.source.name}} -> {{item.sink.name}} ({{item.description}})
}