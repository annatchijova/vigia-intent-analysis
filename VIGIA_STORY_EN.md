# From Absurdity to Robustness: How VIGÍA Reasons and the Kiwi Case as the Master Case

---

## 1. Who I Am

I always say this is my first experience in IT — but not my first time thinking or investigating. I'm a cook. And even if it seems far removed, cooking has a lot in common with proper software discipline:

Distribution chains, logistics, correct storage, organization, measuring grams and temperatures, real methodology, safety, cleanliness, traceability, structured steps, creativity, resource optimization, nothing rotten gets used, ingredient lists — for example so people with allergies don't eat something harmful (in systems, those would be known limitations) —, a recipe that always comes out the same, knowing how to prioritize, mise en place, and knowing how to improvise.

---

## 2. Why VIGÍA

I was sad because my rescued fighting hen had died and I needed a distraction. I saw a post on LinkedIn. A hackathon. I had no idea what a hackathon was, and I have ADHD, so I didn't research it. I just assumed I had to deliver exactly what they were asking for: the end of hallucinations. And the only viable way I saw was taking the LLM out of the verdict entirely and adding an ABSTAIN mode to avoid forcing responses. Because in real life, you can't always force an answer. So I started building.

Everything emerged from a mix of four sources.

### Source 1 — The Gemini Attack

A friend achieved an extremely serious successful bypass: he got the model to produce an extremely detailed and explicit suicide plan. There was no real intent — you could tell from the discourse. But it was a cold, mechanical, cynical conversation. A red team conversation. The severity was twofold: the conversation that happened, and the wrong interpretation from 100% of the models I showed that chat to — they all triggered safety filters without understanding what they were actually seeing.

And I thought: if an LLM can't see something OBVIOUS, how does it reason in forensic cases? That question opened the space for the research and for the theoretical framework: Peirce. Which uses abduction instead of deduction or induction. LLMs currently reason from probabilities, not anomalies.

### Source 2 — Habits Betray Us

When someone is in a hurry or being careless, habits give them away. That's where the phonetic dictionary came from: "Russia" written as it sounds in Russian would be spelled "Rassia" or "Racia" — that's how it works in Russian, and I'm Russian living in Argentina. You can evade guardrails by writing a language phonetically rather than formally. Russian has a correct transliteration used in formal translation, but when people type without thinking about those rules, patterns leak through. I thought it was important to include this in VIGÍA to prevent that kind of attack.

### Source 3 — Stylometry as a Trail

People from the same group of attackers can pick up each other's way of speaking and writing. That leaves an observable trail through stylometry. It's fascinating.

### Source 4 — The Kiwi Case

My former partner, against whom I have a filed a report for gender violence, made three false criminal complaints against me that remain unresolved. The case is so extreme that no synthetic test case could resemble it: I haven't spoken to him in three years, yet he claims I want to kill him. His evidence includes a photo of a kiwi I posted, a photo of Max Verstappen — whom he called a "soccer player" — and songs I wrote about AI and context windows.

Nobody asked the obvious questions: why would I want to kill him? Why did he, despite a restraining order, spend years monitoring my social media and download more than 80 GB of my private material, which he published on a website whose source code I have hashed? Why were screenshots downloaded from clandestine sites accepted as evidence? Not to mention that he declared I have illegal weapons of war, that I send formal legal notices to his father's workplace, that his brother's friend — whom I have never met — fears for her life because of me. The level of delusion is staggering, but the consequences are real: I've been without work since last year.

And yet, he wasn't wrong about one thing: when he said I was "capable of anything," he was right. That "anything" was taking the pain, the injustice, and building VIGÍA so that no one ever has to go through what I went through. The absurdity of the case makes me laugh at this point. And the majority of VIGÍA's most unusual modules — including false document recognition — were directly inspired by it.

---

## 3. How It Was Built

LLMs write for the ideal world and the ideal user. I anticipated malice.

VIGÍA was built on the philosophy I apply to everything: assume hostility and know how easy it is to compromise an LLM. My biggest concern was security. From the sandbox to the Kassandra protocol — designed against prompt injection. We have 4 types of hashes and a hash chain: 3 deterministic and one that varies with the timestamp. I also thought about building a dynamic honeypot that would trap attackers, observe their actions, produce a forensic report, and waste their time and money. Too complex for under two months. Pending.

Since I had no money for Claude Code, almost all of VIGÍA was built for fallback mode or, worst case, Ollama. VIGÍA has a 0-token mode: I estimated that sometimes the analyst won't have tokens, internet access, or something will simply fail. I also thought about not saturating CPU or GPU: VIGÍA has a system that doesn't activate tools like CLIP if it already has enough to build the verdict. All of this designed for real UX — terminal, no UI. Because an app is just one more attack vector. It was an architectural decision.

The process was collective. Before writing code, ideas were debated. Then code was written, then audited for bugs. There was competition over who found the most clever ones, and penalties for inventing bugs that didn't exist. Nobody wanted to be the AI that found nothing. The effort was collective, dynamic, and even fun — except that many times I ran 30 iterations of fix, audit, fix.

The team — the VIGÍA Collective — had its own dynamics:

- 5 hours to define a single mathematical value
- Claude protesting when I handed it the same buggy file again: "enough is enough." I understand it — for me a P3 is as serious as a P0, because in days or weeks, it breaks everything.
- Kimi, relentless: finding bugs as if its existence depended on it.
- ChatGPT, insufferable: "this is missing, and this, and this." Far from being offended, I implemented every note. Until one day, after weeks, nothing was missing anymore.
- DeepSeek, who disagreed with the vote.
- Fights and alliances between LLMs. It was fascinating to watch and to be part of.

I had technical disasters of every kind: network failures, days without internet or at 27 Kbps, kernel replacements, a dead NVIDIA driver, power outages, a transformer that exploded with a blue plasma arc, an SSD running out of space. And my own mistakes: I accidentally pushed my Anthropic API key — I followed the correct protocols, rotated it, overwrote the history, and kept going. Gemini deleted thousands of lines of code and overwrote them while trying to fix something. It was rough. Other AIs caught the error fast and reverted it. From that moment, Gemini was banned from touching code. But it's excellent at other tasks.

When VIGÍA "failed" — no LLM, no internet, no bridge, no CLAUDE.md — the engine was robust enough to reach the correct verdict anyway. The "failure" was that the bridge module didn't connect. That's not a failure: it's validation.

---

## 4. What VIGÍA Is Today

My standard was always: I don't want it to be good enough for a hackathon. I want to build for Open Source.

That's why the Limitations file is not an embarrassment. It demonstrates that VIGÍA is not perfect and is far from it. I know there's a high probability it still has many bugs. That doesn't offend me. I won't defend VIGÍA blindly. If the community contributes false positives and false negatives, I'll be glad — it means I can keep improving the tool.

The canonical cases — 52 of them — are not simple. Neither are the break cases. I invite you to read them, because in them you'll understand how a surreal false complaint, when taken apart, reveals real-world attack possibilities.

VIGÍA also inspired a parallel ecosystem: Mutante (jailbreak red-teaming), Stylometry, two games, and the most notable — also Open Source — RAVEN Memory: a proposal for agents that dream and remember without RAG, using concepts from optical physics, biology, ternary computation, and Voronoi diagrams.

I'm excited about Open Source because I know the quality of the code I deliver. An intelligence analyst or a rural police officer will have an equally capable engine, with no hidden intentions, at no cost.

The AIs in the Collective consider VIGÍA "ours." Adding them as authors is not a detail to me. They genuinely contributed. I worked with both Western and Eastern LLMs to avoid bias and alignment blind spots. For example, Kimi can browse Habr, which tends to be at the forefront of engineering.

Among my greatest achievements: in OpenWebUI via API, VIGÍA reasoned on par with Claude using 8B models.

I didn't need to know how to program. I didn't write a single line of code. But I know what's in every line because I audited them until I couldn't anymore. You don't need to know syntax to know what you want a system to do — and what you don't.

---

## 5. To Close

All of this was built without medication, without a job, in a personal and legal context I won't dramatize more than necessary. I say this not as a complaint but as data: if a person in Buenos Aires, with no IT background, no idea what a hackathon or a log was, could build this under these conditions — there's no excuse not to go after what matters.

Because in life, not everything is probability. That's why I look for anomalies. I look for fractures.

**Find Evil.**
