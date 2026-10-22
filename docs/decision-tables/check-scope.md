# Decision table — check_scope (draft)

Guards run in order; the first "no" decides the response.

| Rule | Token | App access | Level | Route | Target | Expected | Tested at |
|---|---|---|---|---|---|---|---|
| R1 | no Authorization header | — | — | GET | own | 401 | mentoria API |
| R1b | header without `Bearer ` | — | — | GET | own | 401 | mentoria API |
| R2 | expired | — | — | GET | own | 401 | auth-service API |
| R3 | invalid signature | — | — | GET | own | 401 | auth-service API |
| R4 | valid | no | — | GET | own | 403 | mentoria API |
| R5 | valid | yes | Editar | GET | own | 200 | mentoria API |
| R6 | valid | yes | Editar | GET | other mentor's | 404 | mentoria API |
| R7 | valid | yes | Gerenciar | GET | other mentor's | 200 | mentoria API |
| R8 | valid | yes | gerenciar (wrong case) | GET | other mentor's | 404 | mentoria API |
| R9 | valid | yes | Editar | GET | nonexistent | 404 | mentoria API |
| R10 | valid | yes | Visualizar | GET | own | 200 | mentoria API |
| R11 | valid | yes | Visualizar | GET | other mentor's | 404 | mentoria API |
| R12 | valid | yes | Visualizar | POST | own | 403 | mentoria API |
| R13 | valid | yes | Editar | GET | other mentor's, shared with me | TBD | mentoria API |
| R14 | auth-service down | — | — | GET | own | 503 | mentoria API |

> **R13 — open question.** The code suggests sharing works per document, not per mentee, so "mentee shared with me" may not be a real state. The expected result stays TBD until the sharing model is confirmed in the code.
