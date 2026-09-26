import { test } from 'node:test';
import { strict as assert } from 'node:assert';
import { decide } from './agent.mjs';
const policy = { allowedSymbols: ['AAPL'], maxPositionFraction: .1, maxTradeFraction: .05 };
const portfolio = { equity: 10000, cash: 5000, positions: { AAPL: 0 } };
test('approves a bounded paper order', () => assert.equal(decide({ symbol: 'AAPL', action: 'buy', price: 100, quantity: 2 }, portfolio, policy).approved, true));
test('rejects unaffordable and excessive orders', () => {
  assert.equal(decide({ symbol: 'AAPL', action: 'buy', price: 100, quantity: 60 }, portfolio, policy).approved, false);
  assert.equal(decide({ symbol: 'AAPL', action: 'sell', price: 100, quantity: 2 }, portfolio, policy).approved, false);
});
test('rejects malformed model output', () => assert.equal(decide({ symbol: 'AAPL', action: 'buy', price: 'NaN', quantity: 1 }, portfolio, policy).approved, false));
