# Adapters and Data Normalization

Adapters translate between external representations and application contracts. Driving adapters supply clean application input; driven adapters translate infrastructure results into application data.

## Return Application Data

- Define the result shape and relevant types in the port contract, using the application's vocabulary.
- Normalize external field names, types, units, missing values, and response envelopes inside the adapter as needed to satisfy that contract.
- Return data the application can use without knowing the database schema, API payload, SDK response, or client library.
- Keep infrastructure-specific decoding and conversion out of application services. If a service needs to repair an adapter's result before using it, revisit the port contract and adapter.
- Hashes are valid return values when their keys and values follow the application contract. Use objects when they make that contract clearer; a wrapper alone does not establish a boundary.

Application decisions and calculations remain application concerns. An adapter may implement a report calculation in SQL when fulfilling the port, but the meaning of the metric belongs to the application contract.

## Driving Adapters Supply Clean Input

The controller is a driving adapter. It owns translating HTTP input into values the application can use directly.

- Put parameter extraction, parsing, normalization, and input-format validation in a public controller method named for the operation, such as `booking_params`. Do not override Rails' `params` method.
- `booking_params` either returns clean application values or raises an input exception. Do not return an error sentinel or a mixture of valid and invalid values.
- The service requests input through the listener's public `booking_params` method. The driving adapter translates parsing failures into a port-defined error; the service catches it and invokes the failure callback, which the controller renders as an HTTP response.
- Application services obtain typed, normalized values through that contract; they do not parse date strings, split comma-separated HTTP fields, or depend on Rails parameter objects.
- Keep business rules in the application. Valid input representation does not establish that a requested operation is allowed.

```ruby
module ForBooking
  class BookingError < StandardError; end

  # Returns true or false for a Date.
  def available?(starts_on); end

  # Returns a booking with an id; failures raise BookingError.
  def create(starts_on:); end
end

module ForBookingListener
  # Returns { starts_on: Date }; invalid input raises ForBooking::BookingError.
  def booking_params; end

  def booking_created(booking); end
  def booking_failed(message); end
end

class BookingsController < ApplicationController
  def create
    CreateBooking.new(booking_port, self).call
  end

  def booking_created(booking)
    render json: { id: booking.id }, status: :created
  end

  def booking_failed(message)
    render json: { error: message }, status: :unprocessable_entity
  end

  def booking_params
    { starts_on: Date.iso8601(params.require(:starts_on)) }
  rescue ActionController::ParameterMissing, Date::Error
    raise ForBooking::BookingError, "Invalid date"
  end

  private

  def booking_port
    PortFactory.for_booking
  end
end

class CreateBooking < Struct.new(:for_booking, :listener)
  def call
    starts_on = listener.booking_params.fetch(:starts_on)
    # starts_on is already a Date; availability is an application rule.
    if for_booking.available?(starts_on)
      listener.booking_created(for_booking.create(starts_on: starts_on))
    else
      listener.booking_failed("Date unavailable")
    end
  rescue ForBooking::BookingError => error
    listener.booking_failed(error.message)
  end
end
```

The service asks its listener for clean parameters. The controller parses HTTP input and translates parsing errors into `ForBooking::BookingError`. The service handles that error through `booking_failed`, just as it handles other port failures.
