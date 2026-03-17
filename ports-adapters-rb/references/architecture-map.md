# Rails Ports and Adapters Architecture Map (Generic)

## Ports (driven contracts + errors)

- `app/ports/user_port.rb`
  - Listener helpers: `CreateUserListener`, `AuthenticateUserListener`
  - Error: `UserPortError`
  - Port module: `UserPort`
- `app/ports/order_port.rb`
  - Listener helpers: `CreateOrderListener`, `CancelOrderListener`
  - Error: `OrderPortError`
  - Port module: `OrderPort`
- `app/ports/payment_port.rb`
  - Error: `PaymentPortError`
  - Port module: `PaymentPort`
- `app/ports/for_transfer.rb`
  - Listener helper: `ForTransferListener`
  - Error: `DomainError`
  - Port module: `ForTransfer`

## Domain (pure objects / decisions)

- `app/domain/build_order_payload.rb` (build outbound payload for a driven adapter)
- `app/domain/rebuild_user_projection.rb` (recompute dependent state)
- `app/domain/no_rebuild_needed.rb` (no-op strategy)
- `app/domain/transfer.rb` (transfer lifecycle such as `complete`)
- `app/domain/account.rb` (balance rules such as `debit` and `credit`)

## Services (use cases)

- `app/services/create_user.rb` (register + enqueue welcome email)
- `app/services/create_order.rb` (validate + persist + enqueue fulfillment)
- `app/services/cancel_order.rb` (update + notify)
- `app/services/handle_payment_webhook.rb` (validate + update records)
- `app/services/authenticate_user.rb` (session auth)
- `app/services/transfer_money.rb` (move funds + persist transfer in one transaction)

## Adapters (driven port implementations)

- `app/adapters/user_repo.rb` (UserPort implementation + persistence)
- `app/adapters/order_repo.rb` (OrderPort implementation + persistence)
- `app/adapters/payment_gateway.rb` (PaymentPort implementation + external API)
- `app/adapters/active_record_for_transfer.rb` (`ForTransfer` implementation + AR transaction/persistence)

## Controllers (driving adapters + listeners)

- `app/controllers/users_controller.rb`
  - Listener for: `CreateUser`, `AuthenticateUser`
- `app/controllers/orders_controller.rb`
  - Listener for: `CreateOrder`, `CancelOrder`
- `app/controllers/webhooks_controller.rb`
  - Listener for: `HandlePaymentWebhook`
- `app/controllers/sessions_controller.rb`
  - Listener for: `AuthenticateUser`
- `app/controllers/transfers_controller.rb`
  - Listener for: `TransferMoney`
  

## Listener Implementation Notes

- Services accept a `listener` and call `listener.<action>_success`/`listener.<action>_failure` methods.
- Controllers implement those methods directly; they do not inherit from a listener class.
- Use the listener classes in ports as reference shapes for tests or fakes.
- Example transfer callbacks: `transfer_success(transfer)` and `transfer_failed(message)`.

## Wiring

- `app/lib/port_factory.rb` wires ports to adapters with concrete dependencies:
  - `UserRepo.new`
  - `OrderRepo.new`
  - `PaymentGateway.new(ApiClient.instance)`
  - `ActiveRecordForTransfer.new`
