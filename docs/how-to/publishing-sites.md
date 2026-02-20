# How to Publish Documentation Sites

This guide shows you how to create a published documentation site, apply themes, and configure custom domains.

## Overview

The Publishing module generates public-facing documentation sites from your platform content. Sites can be public or restricted, themed, and optionally hosted on custom domains.

## Create a Published Site

1. Navigate to **Organization Settings** → **Publishing**
2. Click **New Site**
3. Fill in:
   - **Site Title**: Display name for the site
   - **Slug**: URL path segment (e.g., `docs` → accessible at `/s/docs`)
   - **Workspace**: Which workspace to publish from
   - **Visibility**: Public (no auth required) or Restricted (visitor login)
4. Click **Create**

**API:**

```
POST /api/v1/publishing/sites
{
  "site_title": "Acme Documentation",
  "slug": "acme-docs",
  "workspace_id": "workspace-uuid",
  "visibility": "public"
}
```

## Select Content to Publish

By default, all effective pages in the workspace are included. You can customize this:

- **Include/Exclude spaces** — Select which spaces appear in the site
- **Classification filter** — Only publish pages at or below a classification level
- **Page-level overrides** — Show or hide individual pages

## Apply a Theme

Themes control the visual appearance of the published site.

1. Go to the site settings → **Theme**
2. Choose or create a theme:
   - **Primary color**: Main brand color
   - **Sidebar position**: Left or Right
   - **Content width**: Narrow, Standard, or Wide
   - **Logo**: Upload a logo image
   - **Custom CSS**: Optional CSS overrides

**API:**

```
POST /api/v1/publishing/themes
{
  "name": "Acme Brand",
  "primary_color": "#0066cc",
  "sidebar_position": "left",
  "content_width": "standard",
  "custom_css": ""
}
```

Then apply the theme to the site:

```
PATCH /api/v1/publishing/sites/{site_id}
{
  "theme_id": "theme-uuid"
}
```

## Publish the Site

Once configured:

1. Click **Publish** in the site toolbar
2. Optionally add a publish message
3. The site becomes accessible at the configured URL

The publish action:
- Generates the site from current effective content
- Creates a Git commit marking the publish point
- Updates the site status to "Published"

## Custom Domains

To host the site on your own domain:

1. Go to site settings → **Custom Domain**
2. Enter your domain (e.g., `docs.acme.com`)
3. Configure DNS:
   - Add a CNAME record pointing to your platform instance
   - Or an A record pointing to the platform's IP
4. The platform will detect and serve the site for that domain

**API:**

```
PATCH /api/v1/publishing/sites/{site_id}
{
  "custom_domain": "docs.acme.com"
}
```

## Manage Visitor Access (Restricted Sites)

For restricted sites, manage who can access:

1. Go to site settings → **Visitors**
2. Add visitors by email address
3. Assign visitor roles (controls which content they see)
4. Visitors receive an email with login instructions

Restricted content handling:
- **Hidden mode** — Restricted pages are invisible to visitors without access
- **Placeholder mode** — Restricted pages show a "Content Restricted" message

Configure this in site settings → **Discovery Settings**.

See [Security Model](../explanation/security-model.md) for details on the visitor access model.

## Site Lifecycle

| Status | Description |
|--------|------------|
| **Draft** | Site created but not yet published |
| **Published** | Live and accessible at the site URL |
| **Maintenance** | Temporarily unavailable (shows maintenance page) |
| **Archived** | Permanently taken offline |

## Unpublish a Site

To take a site offline:

1. Click **Unpublish** in the site toolbar
2. Confirm the action
3. The site returns to Draft status and is no longer accessible
