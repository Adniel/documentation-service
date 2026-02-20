# Create Your First Document

This tutorial guides you through creating content in the platform, from setting up an organization to writing your first page.

## Prerequisites

- Completed [Getting Started](getting-started.md)
- Admin or Editor role in an organization

## Step 1: Create an Organization

If you are starting fresh, create an organization first.

1. Click **New Organization** in the sidebar
2. Fill in:
   - **Name**: Your company or team name (e.g., "Acme Corp")
   - **Slug**: URL-friendly identifier (e.g., `acme-corp`) — lowercase, hyphens only
   - **Description**: Optional summary
3. Click **Create**

You become the **Owner** of the organization automatically.

**API equivalent:**

```
POST /api/v1/organizations
{
  "name": "Acme Corp",
  "slug": "acme-corp",
  "description": "Acme Corporation documentation"
}
```

## Step 2: Create a Workspace

Workspaces group related documentation. A workspace might represent a department, project, or product.

1. Inside your organization, click **New Workspace**
2. Fill in:
   - **Name**: e.g., "Quality Management"
   - **Slug**: e.g., `quality-management`
   - **Description**: Optional
   - **Public**: Toggle on if the workspace should be visible to all org members
3. Click **Create**

## Step 3: Create Spaces

Each workspace needs at least one space. Spaces are typed by the Diataxis framework.

1. Inside your workspace, click **New Space**
2. Fill in:
   - **Name**: e.g., "Tutorials"
   - **Slug**: e.g., `tutorials`
   - **Diataxis Type**: Select "Tutorial"
   - **Classification**: Default is "Public" — choose higher for sensitive content
3. Click **Create**
4. Repeat for other types: How-to Guides, Reference, Explanation

A typical workspace has four spaces — one per Diataxis type.

## Step 4: Create a Page

Now create your first document.

1. Navigate to a space (e.g., Tutorials)
2. Click **New Page**
3. Enter the page title: e.g., "Introduction to Document Control"
4. The slug auto-generates from the title (e.g., `introduction-to-document-control`)
5. Click **Create**

You are now in the block-based editor.

## Step 5: Write Content

The editor supports rich content with slash commands:

- Type `/` to open the command palette
- Type text directly for paragraphs
- Use `# ` for headings (## for h2, ### for h3)
- Use `- ` for bullet lists, `1. ` for ordered lists
- Use `` ``` `` for code blocks

### Available Block Types

| Command | Block Type |
|---------|-----------|
| `/heading` | Heading (h1–h3) |
| `/paragraph` | Paragraph text |
| `/bullet-list` | Unordered list |
| `/ordered-list` | Numbered list |
| `/code` | Code block with syntax highlighting |
| `/table` | Table with rows and columns |
| `/image` | Image (inline or block) |
| `/callout` | Callout/admonition box |

### Keyboard Shortcuts

- **Ctrl+B** / **Cmd+B** — Bold
- **Ctrl+I** / **Cmd+I** — Italic
- **Ctrl+K** / **Cmd+K** — Insert link
- **Ctrl+S** / **Cmd+S** — Save

## Step 6: Save and Review

Content auto-saves as you type. Each save creates a Git commit behind the scenes:

- Your page content is stored as JSON in the Git repository
- The file path follows the pattern: `{workspace}/{space}/{page-slug}.json`
- Every save records the author, timestamp, and content hash

To view the version history, click the **History** icon in the page toolbar.

## Step 7: Set Page Metadata

In the page settings panel (gear icon):

- **Summary** — A brief description shown in listings
- **Classification** — Override the space default (Public, Internal, Confidential, Restricted)
- **Diataxis Types** — Override inherited type or assign multiple types

## Next Steps

- [Approval Workflow](approval-workflow.md) — Submit your document for review
- [Attachments and Media](../how-to/attachments-and-media.md) — Add images and files
