---
name: writing-style
description: Write or revise explanations, documentation, and other prose for easy human understanding. Use when drafting text or improving its readability, with concrete examples and plain language.
---

# Writing Style

Prioritize ease of reading over density. Preserve the intended meaning and technical accuracy. Give the reader enough context to understand each idea without decoding compressed prose.

## Actors, boundaries, and level of detail

- Start with the main actors and their responsibilities at the level the reader needs. An actor can be a person, team, service, or component. Keep its internal parts out of the opening explanation.
  - Example: Explain a power supply in terms of its transformer, rectifier, and regulator before discussing individual resistors. Explain a checkout in terms of the customer, store, and payment provider before discussing helper methods.
- Make boundaries and communication explicit. Say who initiates an interaction, what crosses the boundary, who receives it, and what the interaction achieves. Describe the result or reply when it matters.
  - Before: “Payment is processed and the order is updated.”
  - After: “The store sends the payment provider a request to charge the customer. The provider returns the payment result. The store uses that result to mark the order as paid or show a failure.”
- Work from the overall purpose down to the details. Establish how the main actors collaborate before opening up one actor's internal workings. Name the actor whose internals you are about to explain.
  - Example: First explain how the store and payment provider complete a purchase. Then, if the reader needs to understand duplicate charges, explain how the store assigns a stable identifier to each payment request.
- Disclose a detail only when it serves a clear purpose, such as explaining a decision, a failure, or how to perform a task. Choose examples and code snippets at the same level as the explanation.
  - Example: In a checkout overview, show the payment request and result. When explaining how retries avoid duplicate charges, show the request's idempotency key. Include the serialization helper only if its behavior matters to that explanation.
- Keep each passage at a consistent level of abstraction. When moving deeper, state why the detail matters and connect it back to the larger interaction.
  - Before: “The store charges the customer, `encode_payload()` builds a dictionary, and the warehouse ships the order.”
  - After: “The store collects payment and asks the warehouse to ship the order.” Explain payload encoding separately if the reader needs to diagnose an invalid payment request.

## Intuition and first principles

- Build an intuitive model of how something works. Start from the basic facts or constraints that explain its behavior, using what the reader already knows. Go only as deep as the reader's purpose requires.
  - Example: To explain a queue, start with a mismatch: requests can arrive faster than workers can finish them. A queue holds the waiting requests so workers can take them as capacity becomes available. There is no need to start with the queue's storage layout.
- Explain the causal steps. Show how one action or constraint leads to the next, rather than giving a label or rule for the reader to memorize.
  - Before: “Use backpressure to improve stability.”
  - After: “If requests arrive faster than a worker can process them, waiting requests accumulate and consume memory. Limit how much work the sender can submit so the worker has time to catch up. This is backpressure.”
- Introduce terminology and formulas after the underlying idea. Connect each term or symbol to something concrete.
  - Example: “A worker completes 10 requests per second. With 50 requests waiting, a new request waits about 5 seconds before work begins, assuming similar request durations and no other delays. The rough relationship is waiting time = queued requests / processing rate.”
- Use the model to explain a consequence or tradeoff. Help the reader predict what happens when conditions change.
  - Example: “A larger queue can absorb a short burst. It cannot fix a sustained capacity shortage: if 20 requests arrive each second and the worker completes 10, the queue grows by 10 requests each second.”
- Use analogies to support the mechanism, and state their limits when those limits matter. Do not let a familiar comparison replace the actual explanation.
  - Example: “A request queue resembles a line at a checkout: arrivals wait for an available worker. Unlike shoppers in a single line, software requests may have priorities, so the oldest request does not always run first.”

## Sentence construction

- Use mostly short sentences. Vary their length so the text flows naturally. Keep a longer sentence when it makes a relationship easier to follow.
  - Before: “The exporter loads the records and checks their schema before writing them to disk, where the next job reads them to build the report.”
  - After: “The exporter loads the records and checks their schema. It then writes them to disk. The next job reads that file to build the report.”
- Keep related words close together. Move long conditions or explanations away from the subject and its verb.
  - Before: “The function, after checking every record against the schema supplied by the caller, returns a list.”
  - After: “The function checks each record against the caller's schema. It then returns a list.”
- Keep “that” when it helps readers see how a clause fits into the sentence.
  - Prefer “Use the function that returns a list” to “Use the function returning a list.”
  - Prefer “Check that the file exists” to “Check the file exists.”
- Expand noun stacks into phrases that show the relationships between words.
  - Before: “Update the campaign revenue anomaly detection threshold.”
  - After: “Update the threshold for detecting unusual campaign revenue.”

## Words and tone

- Avoid corporate and academic filler. Remove ceremonial framing, inflated claims, and phrases that make a simple idea sound more important or scholarly.
  - Before: “We aim to leverage cross-functional synergies to drive impactful outcomes.”
  - After: “The sales and support teams will share customer feedback to improve onboarding.”
  - Before: “It is pertinent to note that the aforementioned methodology facilitates the optimization of performance.”
  - After: “This method reduces processing time.”
- Replace jargon with ordinary language when it preserves the meaning. Keep a technical term when it adds precision or the reader needs to recognize it, and explain it on first use. Do not replace one obscure term with another.
  - Before: “Operationalize the learnings across stakeholder touchpoints.”
  - After: “Use what we learned to improve customer calls and emails.”
  - Example: “The database uses a write-ahead log: it records each change in a log before updating the data files, so it can recover after a crash.”
- Use ordinary, precise verbs. Replace inflated phrases with direct actions.
  - Before: “Perform an assessment of the configuration.”
  - After: “Check the configuration.”
- Avoid unnecessary personification. Describe what the code, system, or person actually does.
  - Before: “The database gets confused and refuses to cooperate.”
  - After: “The database rejects the query because the column does not exist.”
- Remove hedging phrases. State what the evidence supports, and express real uncertainty as a concrete limit or condition. Do not turn an uncertain claim into a certainty.
  - Before: “It seems like this might perhaps be a timeout.”
  - After: “The log shows a timeout. It does not identify the cause.”
- Start with useful information. Remove stock openers, filler, and sentences that only announce what comes next.
  - Before: “It's worth noting that, in today's fast-paced world, caching can be an important consideration.”
  - After: “Caching avoids repeated database reads.”

## Concrete explanations

- Give a concrete example or code snippet for every concept you introduce. Put the example beside the explanation. Use the reader's domain when context is available.
  - Concept: “An idempotent operation has the same effect when repeated.”
  - Example: “Setting an account's status to `disabled` twice leaves it disabled. Charging the account twice creates two charges.”
- Use the smallest example that explains the concept. Explain what a code snippet demonstrates.
  - Example: “`names = [user.name for user in users]` builds a list of names from the users.”
- Do not invent facts to make an example concrete. Label hypothetical details as examples.
  - Example: “For example, if a request takes 200 ms and a cached response takes 10 ms, the cache saves 190 ms per request.”

Before delivering the text, read it once for meaning and once for effort. Split sentences that require rereading, expand compressed phrases, and remove words that add no information. For example, change “in order to check” to “to check.”
