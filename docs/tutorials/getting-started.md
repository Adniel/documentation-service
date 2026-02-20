# Getting Started

This tutorial walks you through your first login, navigating the interface, and understanding the core concepts of the Documentation Service Platform.

## Prerequisites

- A running instance of the Documentation Service (see [Configuration](../reference/configuration.md))
- An account created by your administrator

## Step 1: Log In

1. Navigate to your instance URL (default: `http://localhost:5173`)
2. Enter your email address and password
3. Click **Sign In**

The platform uses JWT-based authentication. Your session lasts 30 minutes by default (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`), with automatic refresh tokens valid for 7 days.

**API equivalent:**

```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "you@example.com",
  "password": "your-password"
}
```

## Step 2: Understand the Content Hierarchy

Content is organized in four levels:

```
Organization
  └── Workspace
        └── Space (Diataxis-typed)
              └── Page
```

- **Organization** — Your company or team. Contains workspaces and manages members.
- **Workspace** — A project or department grouping. Examples: "Quality Management", "Engineering".
- **Space** — A documentation area typed by the Diataxis framework: Tutorial, How-to, Reference, or Explanation.
- **Page** — An individual document with rich content, version history, and lifecycle status.

## Step 3: Navigate the UI

After logging in, you will see:

1. **Sidebar** — Lists your organizations, workspaces, and spaces in a collapsible tree
2. **Content area** — Displays the selected page in the block-based editor
3. **Top bar** — Search, user menu, and notifications

### Switching Organizations

If you belong to multiple organizations, use the organization selector in the sidebar header to switch between them.

### Using Search

Press `/` or click the search bar to search across all pages you have access to. Results respect your classification clearance level — you will only see documents at or below your clearance.

## Step 4: Understand Diataxis Types

Every space has a Diataxis type that categorizes the documentation it contains:

| Type | Purpose | Example |
|------|---------|---------|
| **Tutorial** | Learning-oriented lessons | "Getting Started with QMS" |
| **How-to** | Task-oriented instructions | "How to Submit a Change Request" |
| **Reference** | Information-oriented descriptions | "API Endpoint Reference" |
| **Explanation** | Understanding-oriented discussion | "Why We Use Hash Chains for Audit" |

Pages inherit their type from the parent space by default, but can also be assigned multiple types explicitly.

## Step 5: Check Your Profile

1. Click your avatar in the top-right corner
2. Select **Profile**
3. Review your details: name, email, clearance level, and organization memberships

Your clearance level (0–3) determines which classified documents you can access:

| Level | Classification | Access |
|-------|---------------|--------|
| 0 | Public | Public documents only |
| 1 | Internal | Public + Internal |
| 2 | Confidential | Public + Internal + Confidential |
| 3 | Restricted | All documents |

## Next Steps

- [Create Your First Document](create-first-document.md) — Learn how to create pages
- [Approval Workflow](approval-workflow.md) — Learn the document lifecycle
