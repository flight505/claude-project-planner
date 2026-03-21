# Building Blocks - Specification Examples

## Backend Service Block

```yaml
building_block:
  name: "User Authentication Service"
  id: "BB-001"
  type: "backend"

  description: |
    Handles user authentication, authorization, and session management.
    Supports email/password login and OAuth2 social providers.

  responsibilities:
    - "User registration with email verification"
    - "Login/logout with session management"
    - "JWT token generation and validation"
    - "OAuth2 integration (Google, GitHub)"
    - "Password reset flow"
    - "Role-based access control"

  dependencies:
    internal:
      - block_id: "BB-010"
        type: "required"
        interface: "Database Service"
    external:
      - name: "PostgreSQL"
        version: ">=14.0"
        purpose: "User credentials and sessions"
      - name: "Redis"
        version: ">=6.0"
        purpose: "Session cache and rate limiting"

  interfaces:
    api_endpoints:
      - method: "POST"
        path: "/api/v1/auth/register"
        description: "Register new user with email/password"
        request_schema:
          email: "string (email format)"
          password: "string (min 8 chars)"
          name: "string"
        response_schema:
          user_id: "uuid"
          message: "string"
        auth_required: false

      - method: "POST"
        path: "/api/v1/auth/login"
        description: "Authenticate user and return tokens"
        request_schema:
          email: "string"
          password: "string"
        response_schema:
          access_token: "string (JWT)"
          refresh_token: "string"
          expires_in: "number (seconds)"
        auth_required: false

      - method: "POST"
        path: "/api/v1/auth/refresh"
        description: "Refresh access token"
        auth_required: true

      - method: "POST"
        path: "/api/v1/auth/logout"
        description: "Invalidate session"
        auth_required: true

      - method: "GET"
        path: "/api/v1/auth/me"
        description: "Get current user profile"
        auth_required: true

    events_published:
      - name: "user.registered"
        description: "Emitted when new user completes registration"
        payload_schema:
          user_id: "uuid"
          email: "string"
          registered_at: "timestamp"

      - name: "user.logged_in"
        description: "Emitted on successful login"
        payload_schema:
          user_id: "uuid"
          login_at: "timestamp"
          method: "password | oauth"

  complexity: "M"
  estimated_hours: 24
  story_points: 5

  test_criteria:
    - "User can register with valid email and password"
    - "Registration fails with invalid email format"
    - "Registration fails with weak password"
    - "User can login with correct credentials"
    - "Login fails with incorrect password (returns 401)"
    - "User receives valid JWT token on login"
    - "JWT token contains correct claims (user_id, roles)"
    - "Token refresh works with valid refresh token"
    - "Logout invalidates session"
    - "Protected endpoints reject invalid tokens"
    - "Rate limiting prevents brute force attacks"

  priority: "critical"
  sprint_assignment: "Sprint 1"
```

## Frontend Component Block

```yaml
building_block:
  name: "Dashboard UI"
  id: "BB-020"
  type: "frontend"

  description: |
    Main dashboard interface showing key metrics, recent activity,
    and navigation to other features.

  responsibilities:
    - "Display key performance metrics"
    - "Show recent user activity feed"
    - "Provide navigation to features"
    - "Handle responsive layout"
    - "Manage loading and error states"

  dependencies:
    internal:
      - block_id: "BB-001"
        type: "required"
        interface: "Auth Service (for user context)"
      - block_id: "BB-005"
        type: "required"
        interface: "Metrics API"
      - block_id: "BB-025"
        type: "required"
        interface: "Design System Components"
    external:
      - name: "React"
        version: ">=18.0"
        purpose: "UI framework"
      - name: "TanStack Query"
        version: ">=5.0"
        purpose: "Data fetching and caching"

  interfaces:
    api_consumed:
      - endpoint: "GET /api/v1/metrics/summary"
        purpose: "Load dashboard metrics"
      - endpoint: "GET /api/v1/activity/recent"
        purpose: "Load activity feed"

    components_exposed:
      - name: "DashboardPage"
        description: "Main dashboard route component"
      - name: "MetricsWidget"
        description: "Reusable metrics display widget"

  complexity: "M"
  estimated_hours: 20
  story_points: 5

  test_criteria:
    - "Dashboard loads and displays metrics"
    - "Activity feed shows recent items"
    - "Loading state shown while fetching"
    - "Error state shown on API failure"
    - "Responsive layout works on mobile"
    - "Navigation links work correctly"
    - "Auto-refresh updates data periodically"

  priority: "high"
  sprint_assignment: "Sprint 2"
```

## Infrastructure Block

```yaml
building_block:
  name: "CI/CD Pipeline"
  id: "BB-100"
  type: "infrastructure"

  description: |
    Continuous integration and deployment pipeline using GitHub Actions.
    Handles testing, building, and deploying to staging and production.

  responsibilities:
    - "Run tests on pull requests"
    - "Build Docker images"
    - "Push to container registry"
    - "Deploy to staging automatically"
    - "Deploy to production with approval"
    - "Run database migrations"

  dependencies:
    external:
      - name: "GitHub Actions"
        purpose: "CI/CD platform"
      - name: "Docker Hub / ECR"
        purpose: "Container registry"
      - name: "AWS ECS / Kubernetes"
        purpose: "Deployment target"

  interfaces:
    triggers:
      - event: "push to main"
        action: "Deploy to staging"
      - event: "release tag"
        action: "Deploy to production"
      - event: "pull request"
        action: "Run tests"

    outputs:
      - name: "Docker images"
        format: "project/service:version"
      - name: "Test reports"
        format: "JUnit XML"
      - name: "Coverage reports"
        format: "Cobertura XML"

  complexity: "M"
  estimated_hours: 16
  story_points: 3

  test_criteria:
    - "Pipeline triggers on push to main"
    - "Tests run and report results"
    - "Build creates valid Docker image"
    - "Image is pushed to registry"
    - "Staging deployment succeeds"
    - "Production requires manual approval"
    - "Rollback mechanism works"
    - "Secrets are not exposed in logs"

  priority: "critical"
  sprint_assignment: "Sprint 1"
```
