# payments/

Tiny stand-in for a payment service. Used by the **Compliance Co-Pilot** and
**Incident Time-Machine** demos. Not a real implementation.

The baseline code in `charge.py` is intentionally **compliant** with the
policies in `/policies` so that a deliberately bad PR against this file will
light up the agent.
