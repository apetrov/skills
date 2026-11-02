# Defining Ports by Application Capability

A port is a logical piece of the application, such as `ForHandlingTransaction`, `ForUserAuthentication`, or `ForOrdering`. It describes the operations the application needs for that capability. The application depends on this contract; the adapter owns how those operations are fulfilled.

## Choosing a Boundary

- Start with the application's capabilities and group the operations needed for each one.
- Name ports after their application purpose, using names such as `ForHandlingTransaction` and `ForUserAuthentication`.
- Keep operations together when they form one coherent application capability. A port may expose both saving a record and enqueueing a notification.
- Split a port when it represents separate application capabilities. Tables, technologies, aggregate counts, and method counts do not determine the boundary.

## Implementation Belongs to Adapters

An adapter may use a database, queue, external service, or a combination of them to fulfill a port. The application should not need to know which technologies are involved or how the adapter coordinates them.

Specify observable behavior and failure outcomes in the port contract. When atomicity matters to the application, express that guarantee without exposing the infrastructure mechanism used to provide it.

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
