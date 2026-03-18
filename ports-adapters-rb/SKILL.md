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
- Domain services must not raise exceptions; they report outcomes only through listener success/failure callbacks.
- Pass the controller (or a dedicated presenter) as the listener; implement the expected callback methods on the controller.
- The listener/controller must always turn both success and failure callbacks into a valid application response; do not rely on uncaught exceptions that become HTTP 500s.
- Use listener classes in ports as interface references only; controllers do not inherit from them.

## Error Boundaries

- Adapters may raise only domain-defined errors from the relevant port contract, for example `UserPortError`.
- Do not leak adapter-specific exceptions (AR errors, HTTP client errors, SDK errors) across the port boundary; translate them into domain exceptions first.
- Services handle adapter/domain failures by triggering the listener failure path instead of re-raising.

## Worked Example: Transfer Money

Use one coarse driven port when the use case spans multiple records inside one transaction. A money transfer is a good example because account lookup, balance updates, and transfer persistence all belong to the same consistency boundary.

```ruby
class DomainError < StandardError; end

module ForTransfer
  def find_account(id); end
  def build_transfer(source, dest, amount_cents); end
  def update_account_balance(account); end
  def save_transfer(transfer); end
  def transaction(&block); end
end

module ForTransferListener
  def transfer_success(transfer); end
  def transfer_failed(message); end
end

# app/services/transfer_money.rb
# If the app uses app/application instead of app/services, keep the same shape.
class TransferMoney
  attr_reader :for_transfer, :listener

  def initialize(for_transfer, listener)
    @for_transfer = for_transfer
    @listener = listener
  end

  def call(source_id, dest_id, amount_cents)
    transfer = for_transfer.transaction do
      source = for_transfer.find_account(source_id)
      dest = for_transfer.find_account(dest_id)
      transfer = for_transfer.build_transfer(source, dest, amount_cents)

      source.debit(amount_cents)
      dest.credit(amount_cents)

      for_transfer.update_account_balance(source)
      for_transfer.update_account_balance(dest)

      transfer.complete
      for_transfer.save_transfer(transfer)
      transfer
    end

    listener.transfer_success(transfer)
  rescue DomainError => e
    listener.transfer_failed(e.message)
  end
end

class Transfer < ActiveRecord::Base
end

class Account < ActiveRecord::Base
end

# app/adapters/for_transfer_repo.rb
# Driven
class ForTransferRepo
  include ForTransfer

  def transaction(&block)
    Account.transaction(&block)
  end

  def find_account(id)
    Account.find(id)
  rescue ActiveRecord::RecordNotFound
    raise DomainError, "Unable to find account"
  end

  def update_account_balance(account)
    account.save!
  rescue ActiveRecord::ActiveRecordError
    raise DomainError, "Unable to update account"
  end

  def build_transfer(source, dest, amount_cents)
    Transfer.new(source: source, dest: dest, amount: amount_cents, status: "pending")
  end

  def save_transfer(transfer)
    transfer.save!
  rescue ActiveRecord::ActiveRecordError
    raise DomainError, "Unable to save transfer"
  end
end

# app/controllers/transfers_controller.rb
# Driving
class TransfersController < ApplicationController
  include ForTransferListener

  def create
    repo = ForTransferRepo.new

    TransferMoney.new(repo, self).call(
      params.require(:source_account_id),
      params.require(:dest_account_id),
      params.require(:amount).to_i * 100
    )
  end

  def transfer_success(transfer)
    render json: { transfer_id: transfer.id, status: transfer.status }, status: :created
  end

  def transfer_failed(message)
    render json: { error: message }, status: :unprocessable_entity
  end
end
```

Why this example fits the architecture:

- `ForTransfer` is a single driven port because its methods are used together in one transaction.
- `TransferMoney` orchestrates the use case and reports both success and failure through the listener.
- `ActiveRecordForTransfer` is the driven adapter; it wraps Active Record and translates infrastructure failures into `DomainError`.
- `TransfersController` is the driving adapter; it gathers HTTP input and implements the listener callbacks that become HTTP responses.
- The listener module is a reference shape only. The controller does not inherit behavior from it; it just implements the expected methods.

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
- Money transfer: `app/services/transfer_money.rb` -> `app/controllers/transfers_controller.rb`

## Trace a Use Case

1. Identify the entry controller and the listener methods it implements.
2. Find the service in `app/services` that the controller calls.
3. Inspect the driven port contract in `app/ports` for required adapter methods and error types.
4. Confirm the driven adapter implementation in `app/adapters` and any collaborators in `app/domain`.
5. Check `app/lib/port_factory.rb` to see how the adapter is wired.

## Add a New Use Case

- Define or extend a driven port in `app/ports` (include error and any listener interfaces).
- Implement the driven adapter in `app/adapters` (wrap AR/HTTP/queues/etc. and translate infrastructure failures into domain port errors).
- Add a service in `app/services` that accepts `repo`/`listener`, never raises, and calls listener callbacks for both success and failure.
- Implement the listener callbacks in the controller or presenter so every path returns a valid response.
- Wire the adapter in `app/lib/port_factory.rb` if needed.
- Update tests to cover the service and adapter boundary.

## Driving Ports

- Treat driving ports (HTTP/CLI/controllers) as implicit interfaces; they are defined by the entrypoints you expose.
- Keep the explicit interfaces in driven ports; use services to translate from driving adapters into driven ports.

## Resources

- `references/architecture-map.md` for the current file map and listener wiring.
