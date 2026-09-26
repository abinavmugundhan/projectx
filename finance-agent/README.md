# Finance Agent — paper trading only

Node 20+ deterministic risk engine with allowlisted symbols, cash, position and trade limits. LLM generated ideas can be passed as JSON signals, but the model cannot bypass the policy. Default command performs **no API submission**.

```bash
cd finance-agent
node agent.mjs
node --test agent.test.mjs
```

Inputs are `signal.json` with `symbol`, `action`, `price`, `quantity` and `portfolio.json` with `equity`, `cash`, `positions`. Run `node agent.mjs signal.json portfolio.json` to evaluate custom inputs. Every decision is appended to `finance-audit.jsonl` (ignored by git). To submit an explicitly requested order **only to Alpaca's paper endpoint**, set `ALPACA_PAPER_KEY` and `ALPACA_PAPER_SECRET` and add `--submit-paper`. Test prices and holdings are caller supplied and must be refreshed from a trusted source before submission. This implementation does not connect to Ollama/MCP or calculate P&L; no autonomous live brokerage access is present.
