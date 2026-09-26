/** Paper-only decision agent: model advice is untrusted, risk rules make final decision. */
import fs from 'node:fs';
import crypto from 'node:crypto';

export function decide(signal, portfolio, policy) {
  const symbol = String(signal.symbol || '').toUpperCase();
  const action = String(signal.action || '').toLowerCase();
  const price = Number(signal.price);
  const equity = Number(portfolio.equity);
  const cash = Number(portfolio.cash);
  const quantity = Number(signal.quantity);
  const held = Number(portfolio.positions?.[symbol] || 0);
  if (!/^[A-Z]{1,5}$/.test(symbol) || !['buy', 'sell', 'hold'].includes(action) ||
      !Number.isFinite(price) || price <= 0 || !Number.isFinite(quantity) ||
      !Number.isInteger(quantity) || quantity < 0 || !Number.isFinite(equity) || equity <= 0 ||
      !Number.isFinite(cash) || cash < 0) return { approved: false, reason: 'Invalid input' };
  if (action === 'hold') return { approved: false, reason: 'Hold signal' };
  if (!policy.allowedSymbols.includes(symbol)) return { approved: false, reason: 'Symbol not allowlisted' };
  if (quantity === 0) return { approved: false, reason: 'Quantity must be positive' };
  if (action === 'sell' && quantity > held) return { approved: false, reason: 'Insufficient position' };
  if (action === 'buy' && quantity * price > cash) return { approved: false, reason: 'Insufficient cash' };
  if (action === 'buy' && (held + quantity) * price > equity * policy.maxPositionFraction)
    return { approved: false, reason: 'Position limit exceeded' };
  if (action === 'buy' && quantity * price > equity * policy.maxTradeFraction)
    return { approved: false, reason: 'Trade limit exceeded' };
  return { approved: true, order: { symbol, side: action, qty: quantity, type: 'market', time_in_force: 'day' } };
}

export function audit(entry, path) {
  fs.appendFileSync(path, JSON.stringify({ ...entry, id: crypto.randomUUID(), at: new Date().toISOString() }) + '\n', { mode: 0o600 });
}

export async function paperOrder(order, key, secret) {
  if (!key || !secret) throw new Error('Alpaca paper credentials required');
  const response = await fetch('https://paper-api.alpaca.markets/v2/orders', {
    method: 'POST', headers: { 'APCA-API-KEY-ID': key, 'APCA-API-SECRET-KEY': secret,
      'Content-Type': 'application/json' }, body: JSON.stringify(order) });
  const result = await response.json();
  if (!response.ok) throw new Error(`Paper API ${response.status}: ${JSON.stringify(result)}`);
  return result;
}

if (process.argv[1] && import.meta.url === new URL(`file://${process.argv[1]}`).href) {
  const policy = JSON.parse(fs.readFileSync(new URL('./policy.json', import.meta.url)));
  const signal = JSON.parse(fs.readFileSync(process.argv[2] || new URL('./sample-signal.json', import.meta.url)));
  const portfolio = JSON.parse(fs.readFileSync(process.argv[3] || new URL('./sample-portfolio.json', import.meta.url)));
  const verdict = decide(signal, portfolio, policy);
  const livePaper = process.argv.includes('--submit-paper');
  let result = null;
  if (livePaper && verdict.approved) result = await paperOrder(verdict.order, process.env.ALPACA_PAPER_KEY, process.env.ALPACA_PAPER_SECRET);
  let explanation = null;
  if (process.argv.includes('--explain')) {
    const { explain } = await import('./ollama.mjs');
    explanation = await explain(signal, verdict);
  }
  audit({ signal, verdict, submitted: Boolean(result), paperOrderId: result?.id || null, explanation }, 'finance-audit.jsonl');
  console.log(JSON.stringify({ ...verdict, submitted: Boolean(result), paperOrderId: result?.id || null, explanation }, null, 2));
}
