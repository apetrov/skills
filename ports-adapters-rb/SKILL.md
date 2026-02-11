---
name: ports-adapters-rb
description: Rails web app architecture guide. Use when working in app/ports, app/domain, app/services, app/adapters, or app/controllers, especially to trace or implement listener callbacks between services and controllers in a ports-and-adapters design.
---

# Rails Ports and Adapters

## Overview

Navigate hexagonal layers (ports, domain, services, adapters, controllers) and the listener callback pattern. Use this skill to trace a workflow end-to-end or add a new use case without breaking the architecture.

## Architecture Map

Open `references/architecture-map.md` for the generic file map of ports, domain objects, services, adapters, controllers, and wiring.

## Listener Pattern

- Treat services as orchestrators that call listener callbacks for success/failure.
- Pass the controller (or a dedicated presenter) as the listener; implement the expected callback methods on the controller.
- Use listener classes in ports as interface references only; controllers do not inherit from them.

## Defining Ports (Cluster by Responsibility)

Avoid extremes like "one port per table" or "one port per use case" because they create many tiny ports and force services to depend on 4–8 ports each. Instead, cluster by responsibility so you end up with a small set of coarse driven ports that reflect how the domain actually talks to the outside world.

How to cluster correctly:

- Group operations that belong to the same consistency boundary (aggregate root + close collaborators).
- Group operations that change together in transactions.
- Group operations that are replaced together when swapping technology (DB, queue, external service).
- Group operations that share the same "conversation style" with an external actor.

Heuristics to find natural clusters:

- Start from use cases and collect all outgoing calls they make.
- Merge ports whose methods are always used together or in the same transaction.
- Split only when methods have clearly different lifecycles, failure modes, or replacement triggers (e.g., payment vs notification).
- Align with DDD aggregates: one repository port per major aggregate root (or small cluster of related aggregates).
- Aim for 5–15 methods per port; beyond that, split by sub-responsibility (read vs write, query vs command).

Example:

```ruby
# Bad (fragmented)
CreateOrder = Struct.new(:order_port, :item_port, :user_port, :order_notification_port, :listener)

# Good (clustered)
CreateOrder = Struct.new(:for_ordering, :listener)
```

Concrete examples to follow:

- User signup: `app/services/create_user.rb` -> `app/controllers/users_controller.rb`
- Order placement: `app/services/create_order.rb` -> `app/controllers/orders_controller.rb`
- Payment webhook: `app/services/handle_payment_webhook.rb` -> `app/controllers/webhooks_controller.rb`
- Session auth: `app/services/authenticate_user.rb` -> `app/controllers/sessions_controller.rb`

## Trace a Use Case

1. Identify the entry controller and the listener methods it implements.
2. Find the service in `app/services` that the controller calls.
3. Inspect the driven port contract in `app/ports` for required adapter methods and error types.
4. Confirm the driven adapter implementation in `app/adapters` and any collaborators in `app/domain`.
5. Check `app/lib/port_factory.rb` to see how the adapter is wired.

## Add a New Use Case

- Define or extend a driven port in `app/ports` (include error and any listener interfaces).
- Implement the driven adapter in `app/adapters` (wrap AR/HTTP/queues/etc.).
- Add a service in `app/services` that accepts `repo`/`listener` and calls listener callbacks.
- Implement the listener callbacks in the controller or presenter.
- Wire the adapter in `app/lib/port_factory.rb` if needed.
- Update tests to cover the service and adapter boundary.

## Driving Ports

- Treat driving ports (HTTP/CLI/controllers) as implicit interfaces; they are defined by the entrypoints you expose.
- Keep the explicit interfaces in driven ports; use services to translate from driving adapters into driven ports.

## Resources

- `references/architecture-map.md` for the current file map and listener wiring.
