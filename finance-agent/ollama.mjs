/** Optional local rationale for an existing signal. Ollama cannot alter the policy result. */
export async function explain(signal, verdict, model = 'phi4-mini') {
  const base = process.env.OLLAMA_URL || 'http://127.0.0.1:11434';
  const response = await fetch(new URL('/api/generate', base), {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model, stream: false,
      prompt: `Explain this paper trading decision in two sentences. Do not invent prices or recommend a real trade.\nSignal: ${JSON.stringify(signal)}\nPolicy result: ${JSON.stringify(verdict)}` }) });
  if (!response.ok) throw Error(`Ollama returned ${response.status}`);
  return String((await response.json()).response || '').slice(0, 1000);
}
