---
name: ports-adapters-rb
description: "Navigate Rails hexagonal architecture (ports, domain, services, adapters, controllers) and the listener callback pattern. Use when tracing a use case end-to-end or adding a new one without breaking the architecture."
type: workflow
lifecycle: active
---

# Rails Ports and Adapters

## Overview

Trace or add use cases across hexagonal layers without leaking infrastructure or breaking the listener pattern.

## Architecture Map

For locating layers and wiring, read [references/architecture-map.md](references/architecture-map.md), the generic file map of ports, domain objects, services, adapters, controllers, and wiring.

## Listener Pattern

- Treat services as orchestrators that call listener callbacks for success/failure.
- Domain services must not raise exceptions; they report outcomes only through listener success/failure callbacks.
- Pass the controller (or a dedicated presenter) as the listener; implement the expected callback methods on the controller.
- The listener/controller must always turn both success and failure callbacks into a valid application response; do not rely on uncaught exceptions that become HTTP 500s.
- Use listener classes in ports as interface references only; controllers do not inherit from them.

## Error Boundaries

- Adapters may raise only domain-defined errors from the relevant port contract, for example `UserPortError`.
- Do not leak adapter-specific exceptions (AR errors, HTTP client errors, SDK errors) across the port boundary; translate them into domain exceptions first.
- Services handle adapter/domain failures by triggering the listener failure path instead of re-raising.

## Adapter Data Boundaries

Driving adapters provide clean application input; services obtain it through the listener's public operation-specific input method (for example, `booking_params`), which returns normalized values or raises a port-defined error handled by the service through its failure callback. Driven adapters return data in the shape and types defined by the application port. For designing or reviewing this boundary, read [references/adapter-design.md](references/adapter-design.md).

## Trace a Use Case

1. Identify the entry controller and the listener methods it implements.
2. Find the service in `app/services` that the controller calls.
3. Inspect the driven port contract in `app/ports` for required adapter methods and error types.
4. Confirm the driven adapter implementation in `app/adapters` and any collaborators in `app/domain`.
5. Check `app/lib/port_factory.rb` to see how the adapter is wired.

## Add a New Use Case

For choosing or changing port boundaries, read [references/port-design.md](references/port-design.md). For a complete transactional service, adapter, and controller example, read [references/transfer-example.md](references/transfer-example.md).

- Define or extend a driven port in `app/ports` (include error and any listener interfaces).
- Implement the driven adapter in `app/adapters` (wrap AR/HTTP/queues/etc. and translate infrastructure failures into domain port errors).
- Add a service in `app/services` that accepts `repo`/`listener`, never raises, and calls listener callbacks for both success and failure.
- Implement the listener callbacks in the controller or presenter so every path returns a valid response.
- Wire the adapter in `app/lib/port_factory.rb` if needed.
- Update tests to cover the service and adapter boundary.

## Driving Ports

- Treat driving ports (HTTP/CLI/controllers) as implicit interfaces; they are defined by the entrypoints you expose.
- Keep the explicit interfaces in driven ports; use services to translate from driving adapters into driven ports.
