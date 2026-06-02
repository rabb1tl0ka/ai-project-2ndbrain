Invited: Bruno Costa (bruno@loka.com), Sara Kim (sara@loka.com), David Chen (david.chen@acme.com), Maria Lopez (maria.lopez@acme.com)

---

## Summary

SOW2 kicked off with alignment on the customer service bot POC scope. Sara walked through the proposed RAG architecture: ACME's knowledge base as the retrieval corpus, GPT-4o as the generation model, with a thin evaluation layer to measure accuracy per inquiry category. David approved the approach.

Maria confirmed her team's availability for acceptance testing starting mid-February. She also mentioned that the operations team has been asking whether the bot could help with inventory-related customer inquiries ("where is my order", "when will X be back in stock") — Bruno noted this is adjacent to the scope and will need a separate discussion.

The architecture document is the first milestone due January 31.

---

## Decisions

### ALIGNED
- RAG architecture approved: ACME knowledge base + GPT-4o
- Acceptance testing starts Feb 17 with Maria's team
- Architecture doc due Jan 31 — Sara to lead, Bruno to review
- Weekly syncs continue Fridays 10am EST

### NEEDS FURTHER DISCUSSION
- Inventory-related inquiries: Maria's team wants to include "order status" and "back-in-stock" questions. Bruno flagged this may require integration with ACME's inventory system, which is out of scope. Needs scoping call.
- Knowledge base gaps: Sara identified 3 inquiry categories with thin documentation. Maria needs to assign someone to fill the gaps before Feb 1.

---

## Next steps

- [Sara] Draft architecture document by Jan 28 for Bruno review
- [Bruno] Schedule scoping call with Maria on inventory inquiry scope by Jan 25
- [Maria Lopez] Assign knowledge base owner to fill documentation gaps by Jan 27
- [David Chen] Confirm GPT-4o API access and cost approval by Jan 24
