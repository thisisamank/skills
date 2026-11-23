---
name: ai-model-switch
description: Compare AI models on the real product flow, then switch provider safely. Use when the user wants to change AI provider or model, compare models, or know what AI costs.
disable-model-invocation: true
---

# AI model switch

## Evaluate
1. Run the real product flow end to end with each candidate model on real inputs.
2. Measure each model: cost per run, latency, and output quality. Show outputs side by side.
3. Compare with the current provider's real usage and cost.
4. Give one recommendation. Drop a model that is too slow for the job.
5. Take prices from the vendor's page today, not from memory.

## Switch
1. Save the new key with `noenv secret set`, then push it with `noenv wrangler KEY` (see `noenv-secrets-to-workers`).
2. Delete the old secret from production. Keep it in local noenv.
3. Make the related changes: privacy policy (sub-processor list), public pricing docs, the cost table in code.
4. Log an AI-call event with tokens and cost on every call.
5. Cut the number of calls where you can.
6. If the AI cost changes the cost per user, run `pricing-saas` again.

## Defaults
- The latest fast Gemini model, unless the test shows a better fit.
- Ask before you change a production pipeline that the user said to leave alone.
