# Worked Example: Transfer Money

`ForTransfer` represents the application capability of transferring money. Its adapter handles account lookup, balance updates, and transfer persistence within one transaction.

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
  # Returns integer source_id, dest_id, and amount_cents; invalid input raises DomainError.
  def transfer_params; end

  def transfer_success(transfer); end
  def transfer_failed(message); end
end

# app/services/transfer_money.rb
# If the app uses app/application instead of app/services, keep the same shape.
class TransferMoney < Struct.new(:for_transfer, :listener)
  def call
    input = listener.transfer_params
    source_id = input.fetch(:source_id)
    dest_id = input.fetch(:dest_id)
    amount_cents = input.fetch(:amount_cents)

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
  def create
    repo = ForTransferRepo.new

    TransferMoney.new(repo, self).call
  end

  def transfer_params
    {
      source_id: Integer(params.require(:source_account_id), 10),
      dest_id: Integer(params.require(:dest_account_id), 10),
      amount_cents: Integer(params.require(:amount_cents), 10)
    }
  rescue ActionController::ParameterMissing, ArgumentError, TypeError
    raise DomainError, "Account IDs and amount_cents must be integers"
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

- `ForTransfer` defines one logical application capability; its adapter provides the required transaction guarantee.
- `TransferMoney` orchestrates the use case and reports both success and failure through the listener.
- `ForTransferRepo` is the driven adapter; it wraps Active Record and translates infrastructure failures into `DomainError`.
- `TransfersController` is the driving adapter; `transfer_params` converts HTTP input to integers or raises a domain error, and the outcome callbacks produce HTTP responses. This example accepts the amount in integer cents; business rules such as requiring a positive amount belong to the application.
- The listener module is a reference shape only. The controller does not inherit behavior from it; it just implements the expected methods.
