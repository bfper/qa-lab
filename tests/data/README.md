# Data oracles — week 6

Verify the system did what it said it did, not just that the screen showed
the right message.

Two queries that matter:
- a recorded payment reconciles with the mentorando's balance
- no orphan rows between mentor and mentorando

Turn the ad-hoc query into a pytest that fails when the assertion does not
hold. Same runner as week 1, so the marginal cost is close to zero.
