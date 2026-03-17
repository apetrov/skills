# Rails Patterns

## Action Shape

Keep the controller action short:

```ruby
def show
  ShowUser.new(repo: User, listener: self).call(params[:user_id])
end

def show_success(page)
  @page = page
  render :show
end

def show_failed(message)
  render json: { error: message }, status: :unprocessable_entity
end
```

- Let the action delegate immediately.
- Let callback methods translate outcomes into HTTP responses.
- If the app already uses listener callbacks or ports/adapters, follow that existing pattern.

## Use Case Shape

```ruby
ShowUser = Struct.new(:repo, :listener) do
  def call(user_id)
    user = repo.find_by(id: user_id)
    raise StandardError, "Unknown user" unless user
    raise StandardError, "User is inactive" unless user.active?

    listener.show_success(ShowUserPage.new(user))
  rescue StandardError => e
    listener.show_failed(e.message)
  end
end
```

- Put branching and validation here, not in the controller.
- Return a page object for HTML or a domain object/DTO for JSON.
- Keep the public message small, usually `call` or a verb like `show`.

## One Page Object

Bad shape:

```ruby
@user = user
@document = document
@summary = summary
@content = content
```

Preferred shape:

```ruby
@page = build_page_for(user, document)
```

Choose the page object by role or state:

```ruby
def build_page_for(user, document)
  if user.admin?
    AdminDocumentPage.new(user:, document:)
  else
    UserDocumentPage.new(user:, document:)
  end
end

class AdminDocumentPage
  def initialize(user:, document:)
    @user = user
    @document = document
  end

  def summary
    Summary.new(@document)
  end

  def header_partial
    "header_admin"
  end
end

class UserDocumentPage
  def initialize(user:, document:)
    @user = user
    @document = document
  end

  def summary
    Summary.new(@document)
  end

  def header_partial
    "header_user"
  end
end
```

- Do not hide role branching inside `header_partial`.
- Pick the variant object earlier, then let the template ask a uniform interface.

## Template Shape

Prefer:

```erb
<%= render @page.header_partial, page: @page %>
```

Over:

```erb
<% if current_user.admin? %>
  ...
<% else %>
  ...
<% end %>
```

- Let the page object or a role object choose the partial.
- Prefer `AdminPage` / `UserPage` style objects over one object with role conditionals.
- Keep the partials dumb; they should render already-chosen data.
- Use helpers sparingly. If a helper is making domain or role decisions, it probably wants to be an object.
