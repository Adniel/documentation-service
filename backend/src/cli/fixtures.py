"""Seed data fixtures for the documentation-service platform."""

# ---------------------------------------------------------------------------
# MINIMAL FIXTURE
# ---------------------------------------------------------------------------

MINIMAL_FIXTURE = {
    "users": [
        {
            "email": "admin@acme-corp.example",
            "password": "admin123!",
            "full_name": "Admin User",
            "is_superuser": True,
            "clearance_level": 3,
        },
    ],
    "organization": {
        "name": "Acme Corp",
        "slug": "acme-corp",
        "description": "Acme Corporation documentation platform",
    },
    "workspaces": [
        {
            "name": "General",
            "slug": "general",
            "description": "General documentation",
            "spaces": [
                {"name": "Tutorials", "slug": "tutorials", "diataxis_type": "tutorial"},
                {"name": "How-to Guides", "slug": "how-to-guides", "diataxis_type": "how_to"},
                {"name": "Reference", "slug": "reference", "diataxis_type": "reference"},
                {"name": "Explanation", "slug": "explanation", "diataxis_type": "explanation"},
            ],
        },
    ],
    "pages": [],
}


# ---------------------------------------------------------------------------
# DEMO FIXTURE
# ---------------------------------------------------------------------------

DEMO_FIXTURE = {
    "users": [
        {
            "email": "admin@acme-corp.example",
            "password": "admin123!",
            "full_name": "Alice Chen",
            "is_superuser": True,
            "clearance_level": 3,
        },
        {
            "email": "editor@acme-corp.example",
            "password": "editor123!",
            "full_name": "Bob Martinez",
            "is_superuser": False,
            "clearance_level": 1,
        },
        {
            "email": "viewer@acme-corp.example",
            "password": "viewer123!",
            "full_name": "Carol Nguyen",
            "is_superuser": False,
            "clearance_level": 0,
        },
    ],
    "organization": {
        "name": "Acme Corp",
        "slug": "acme-corp",
        "description": "Acme Corporation documentation platform",
    },
    "workspaces": [
        {
            "name": "Quality Management",
            "slug": "quality-management",
            "description": "Quality management system documentation including SOPs, work instructions, and compliance records",
            "spaces": [
                {
                    "name": "Tutorials",
                    "slug": "tutorials",
                    "diataxis_type": "tutorial",
                    "description": "Step-by-step learning guides for the QMS",
                },
                {
                    "name": "How-to Guides",
                    "slug": "how-to-guides",
                    "diataxis_type": "how_to",
                    "description": "Task-oriented guides for common QMS procedures",
                },
                {
                    "name": "Reference",
                    "slug": "reference",
                    "diataxis_type": "reference",
                    "description": "Technical reference for document control and compliance",
                },
                {
                    "name": "Explanation",
                    "slug": "explanation",
                    "diataxis_type": "explanation",
                    "description": "Background and conceptual material for understanding the QMS",
                },
            ],
        },
        {
            "name": "Engineering",
            "slug": "engineering",
            "description": "Engineering team documentation, API references, architecture guides, and development workflows",
            "spaces": [
                {
                    "name": "Tutorials",
                    "slug": "tutorials",
                    "diataxis_type": "tutorial",
                    "description": "Hands-on engineering tutorials",
                },
                {
                    "name": "How-to Guides",
                    "slug": "how-to-guides",
                    "diataxis_type": "how_to",
                    "description": "Practical engineering guides and recipes",
                },
                {
                    "name": "Reference",
                    "slug": "reference",
                    "diataxis_type": "reference",
                    "description": "API reference, configuration, and technical specs",
                },
                {
                    "name": "Explanation",
                    "slug": "explanation",
                    "diataxis_type": "explanation",
                    "description": "Architecture decisions and design rationale",
                },
            ],
        },
        {
            "name": "Compliance",
            "slug": "compliance",
            "description": "Regulatory compliance documentation: SOPs, system validation, risk assessments, and role-based training",
            "spaces": [
                {
                    "name": "System Documentation",
                    "slug": "system-docs",
                    "diataxis_type": "reference",
                    "description": "System design, requirements, risk assessment, and validation documents",
                },
                {
                    "name": "SOPs",
                    "slug": "sops",
                    "diataxis_type": "how_to",
                    "description": "Standard Operating Procedures for platform use",
                },
                {
                    "name": "Training",
                    "slug": "training",
                    "diataxis_type": "tutorial",
                    "description": "Role-based training modules with assessments",
                },
            ],
        },
    ],
    "pages": [
        # =====================================================================
        # Quality Management > Tutorials
        # =====================================================================
        {
            "title": "Getting Started with Document Control",
            "slug": "getting-started-with-document-control",
            "workspace_slug": "quality-management",
            "space_slug": "tutorials",
            "classification": "public",
            "summary": "A step-by-step tutorial for new users learning how to create, review, and approve controlled documents in the QMS.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Getting Started with Document Control"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This tutorial walks you through creating your first controlled document in the Quality Management System. By the end, you will understand the complete document lifecycle from draft to effective status.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Prerequisites"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "An active account with Editor or higher permissions"}],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Access to the Quality Management workspace"}],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Familiarity with your organization's document naming conventions"}],
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Step 1: Create a New Document"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Navigate to your workspace and click the \"New Page\" button. Select the appropriate document type (SOP, Work Instruction, Form, or Policy). The system will automatically generate a document number based on your organization's numbering scheme.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Step 2: Write Your Content"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Use the block-based editor to compose your document. You can add headings, paragraphs, lists, tables, code blocks, and diagrams. Each change is automatically saved and versioned.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Step 3: Submit for Review"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "When your document is ready, click \"Submit for Review.\" The system will route it to the appropriate reviewers based on the approval matrix configured for your document type. Reviewers will receive a notification and can approve, request changes, or reject the document.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Step 4: Electronic Signature and Approval"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Once all reviewers have approved, the designated approver will apply an electronic signature. This signature is 21 CFR Part 11 compliant, capturing the signer's identity, a timestamp from a trusted NTP source, and the meaning of the signature (e.g., Authored, Reviewed, Approved).",
                            }
                        ],
                    },
                ],
            },
        },
        {
            "title": "Your First SOP: A Hands-On Walkthrough",
            "slug": "your-first-sop-walkthrough",
            "workspace_slug": "quality-management",
            "space_slug": "tutorials",
            "classification": "public",
            "summary": "An interactive tutorial guiding new technical writers through creating a Standard Operating Procedure from template selection to final approval.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Your First SOP: A Hands-On Walkthrough"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Standard Operating Procedures (SOPs) are the backbone of any quality management system. This tutorial will guide you through writing an effective SOP using our platform's built-in templates and collaboration features.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Choosing a Template"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Navigate to the Quality Management workspace and click \"New Page.\" From the template picker, select \"Standard Operating Procedure.\" This template includes pre-built sections for Purpose, Scope, Responsibilities, Procedure, and References.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Filling in the Sections"}],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {"type": "text", "marks": [{"type": "bold"}], "text": "Purpose"},
                                            {"type": "text", "text": " \u2014 State why this SOP exists and what process it governs. Keep it to one or two sentences."},
                                        ],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {"type": "text", "marks": [{"type": "bold"}], "text": "Scope"},
                                            {"type": "text", "text": " \u2014 Define which departments, roles, or products are covered by this procedure."},
                                        ],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {"type": "text", "marks": [{"type": "bold"}], "text": "Responsibilities"},
                                            {"type": "text", "text": " \u2014 List each role involved and their specific responsibilities."},
                                        ],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {"type": "text", "marks": [{"type": "bold"}], "text": "Procedure"},
                                            {"type": "text", "text": " \u2014 Write clear, numbered steps. Each step should begin with an action verb."},
                                        ],
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Collaborating with Reviewers"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Use the real-time collaboration features to work with subject-matter experts. You can @mention reviewers directly in the document. All changes are tracked with full version history, so you can always see who changed what and when.",
                            }
                        ],
                    },
                ],
            },
        },
        # =====================================================================
        # Quality Management > How-to Guides
        # =====================================================================
        {
            "title": "How to Configure Approval Workflows",
            "slug": "how-to-configure-approval-workflows",
            "workspace_slug": "quality-management",
            "space_slug": "how-to-guides",
            "classification": "internal",
            "summary": "Step-by-step instructions for setting up and customizing approval matrices for different document types.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "How to Configure Approval Workflows"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Approval workflows ensure that documents are reviewed and signed off by the right people before they become effective. This guide shows you how to set up approval matrices for each document type in your organization.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Access the Admin Dashboard"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Navigate to Settings > Document Control > Approval Matrices. You will need Admin or Owner permissions to modify these settings.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Define Approval Stages"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Each approval matrix consists of one or more stages. A typical workflow includes:",
                            }
                        ],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {"type": "text", "marks": [{"type": "bold"}], "text": "Author Review"},
                                            {"type": "text", "text": " \u2014 The author confirms the document is ready for formal review."},
                                        ],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {"type": "text", "marks": [{"type": "bold"}], "text": "Peer Review"},
                                            {"type": "text", "text": " \u2014 A subject-matter expert reviews the technical accuracy."},
                                        ],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {"type": "text", "marks": [{"type": "bold"}], "text": "Quality Approval"},
                                            {"type": "text", "text": " \u2014 The Quality Manager approves the document for compliance."},
                                        ],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {"type": "text", "marks": [{"type": "bold"}], "text": "Final Authorization"},
                                            {"type": "text", "text": " \u2014 The department head or designated authority provides final sign-off."},
                                        ],
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Assign Roles to Each Stage"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "For each stage, specify which roles or individual users are required to approve. You can set stages as sequential (each must complete before the next begins) or parallel (multiple approvals can happen simultaneously).",
                            }
                        ],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "json"},
                        "content": [
                            {
                                "type": "text",
                                "text": "{\n  \"document_type\": \"SOP\",\n  \"stages\": [\n    {\n      \"name\": \"Peer Review\",\n      \"required_role\": \"reviewer\",\n      \"min_approvals\": 1,\n      \"parallel\": false\n    },\n    {\n      \"name\": \"Quality Approval\",\n      \"required_role\": \"admin\",\n      \"min_approvals\": 1,\n      \"parallel\": false\n    }\n  ]\n}",
                            }
                        ],
                    },
                ],
            },
        },
        {
            "title": "How to Conduct a Periodic Document Review",
            "slug": "how-to-conduct-periodic-review",
            "workspace_slug": "quality-management",
            "space_slug": "how-to-guides",
            "classification": "public",
            "summary": "Instructions for performing scheduled periodic reviews of controlled documents as required by ISO 9001.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "How to Conduct a Periodic Document Review"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "ISO 9001 requires that controlled documents be reviewed at planned intervals to ensure they remain current and adequate. This guide covers the periodic review process from start to completion.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Check Your Review Queue"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Navigate to your dashboard and look for the \"Pending Reviews\" section. Documents approaching their review date are shown with a yellow indicator; overdue documents are shown in red.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Perform the Review"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Open the document and read through all sections"}],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Verify all referenced documents and external standards are still current"}],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Confirm that the procedure still reflects actual practice"}],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Check for any regulatory changes that affect the document's content"}],
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Record the Outcome"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Click \"Complete Review\" and select one of three outcomes: \"No Changes Required\" (the review date is reset), \"Minor Updates\" (you can edit inline and resubmit), or \"Major Revision Required\" (a new change request is created automatically).",
                            }
                        ],
                    },
                ],
            },
        },
        # =====================================================================
        # Quality Management > Reference
        # =====================================================================
        {
            "title": "Document Lifecycle States Reference",
            "slug": "document-lifecycle-states-reference",
            "workspace_slug": "quality-management",
            "space_slug": "reference",
            "classification": "public",
            "summary": "Complete reference for all document lifecycle states, valid transitions, and required permissions.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Document Lifecycle States Reference"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This reference describes each state in the document lifecycle, the transitions between them, and the permissions required to execute each transition.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "States"}],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "Draft"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "The initial state for all documents. Content is editable and only visible to the author and designated collaborators. Draft documents do not appear in published sites.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "In Review"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "The document has been submitted for formal review. Content is locked from editing (except for reviewer comments). All designated reviewers must complete their review before the document can proceed.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "Approved"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "All required approvals have been obtained and electronic signatures applied. The document is ready to become effective but has not yet replaced the current version.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "Effective"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "The document is the current active version. It is visible on published sites and can be referenced by other documents. Any previous version is automatically moved to Obsolete status.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "Obsolete"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "A previously effective document that has been superseded by a newer version. Retained for historical reference and audit trail purposes. Subject to retention policies.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Transition Permissions"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "Transition              Required Role      Signature Required\n---------------------------------------------------------------\nDraft -> In Review      Editor or higher   No\nIn Review -> Approved   Admin or higher    Yes (21 CFR Part 11)\nApproved -> Effective   Admin or higher    No (automatic option)\nEffective -> Obsolete   Admin or higher    No\nAny -> Draft            Editor or higher   No (creates new rev)",
                            }
                        ],
                    },
                ],
            },
        },
        # =====================================================================
        # Quality Management > Explanation
        # =====================================================================
        {
            "title": "Understanding the Diataxis Framework",
            "slug": "understanding-the-diataxis-framework",
            "workspace_slug": "quality-management",
            "space_slug": "explanation",
            "classification": "public",
            "summary": "An explanation of the Diataxis framework and how it structures documentation into four distinct types for maximum clarity.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Understanding the Diataxis Framework"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Diataxis is a systematic approach to organizing technical documentation. It recognizes that documentation serves different purposes at different times and proposes dividing content into four distinct types, each with its own characteristics and writing style.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "The Four Documentation Types"}],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "Tutorials (Learning-Oriented)"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Tutorials are lessons that take the reader through a series of steps to complete a project. They are designed for beginners who need to acquire basic competence. A good tutorial is like a cooking class: the goal is not the dish itself, but the skills the learner acquires.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "How-to Guides (Task-Oriented)"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "How-to guides are directions that take the reader through the steps required to solve a real-world problem. Unlike tutorials, they assume the reader already has basic competence and knows what they want to achieve. A how-to guide is like a recipe: it addresses a specific need and assumes you know how to use a kitchen.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "Reference (Information-Oriented)"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Reference documentation describes the machinery: APIs, configuration options, database schemas, command-line arguments. It is austere and to the point, structured around the code itself rather than around user tasks. Think of it as a dictionary or encyclopedia entry.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "Explanation (Understanding-Oriented)"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Explanation documentation discusses topics at a higher level, providing context and background. It answers the \"why\" questions: why things work the way they do, what the design decisions were, and how concepts relate to each other. This is the type of documentation you are reading right now.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Why This Matters for Quality Management"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "In a regulated environment, clear documentation is not just helpful; it is a compliance requirement. By separating your SOPs (how-to guides) from your training materials (tutorials) and your technical specifications (reference), each document can be written, reviewed, and maintained independently with the appropriate level of rigor.",
                            }
                        ],
                    },
                ],
            },
        },
        {
            "title": "Why Electronic Signatures Matter for Compliance",
            "slug": "why-electronic-signatures-matter",
            "workspace_slug": "quality-management",
            "space_slug": "explanation",
            "classification": "confidential",
            "summary": "An explanation of 21 CFR Part 11 electronic signature requirements and their importance for GxP document control.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Why Electronic Signatures Matter for Compliance"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "The FDA's 21 CFR Part 11 regulation establishes the criteria under which electronic signatures are considered equivalent to handwritten signatures. Understanding these requirements is essential for any organization operating in a GxP-regulated environment.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "The Legal Foundation"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "21 CFR Part 11 was published in 1997 and applies to any records required by FDA regulations. When an organization chooses to maintain records electronically and sign them electronically, Part 11 defines the technical and procedural controls that must be in place.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Key Requirements"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {"type": "text", "marks": [{"type": "bold"}], "text": "Unique to one individual"},
                                            {"type": "text", "text": " \u2014 Each signature must be attributable to exactly one person and not reused or reassigned."},
                                        ],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {"type": "text", "marks": [{"type": "bold"}], "text": "Identity verification"},
                                            {"type": "text", "text": " \u2014 The signer must re-authenticate at the time of signing, even if they have an active session."},
                                        ],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {"type": "text", "marks": [{"type": "bold"}], "text": "Meaning capture"},
                                            {"type": "text", "text": " \u2014 The signature must include the meaning (Authored, Reviewed, Approved, or Witnessed) along with the date and time."},
                                        ],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {"type": "text", "marks": [{"type": "bold"}], "text": "Non-repudiation"},
                                            {"type": "text", "text": " \u2014 The system must ensure that signed records cannot be altered without detection, typically through cryptographic hashing."},
                                        ],
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "How Our Platform Implements Part 11"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Our platform addresses each Part 11 requirement through a combination of technical controls. Re-authentication is enforced at signature time via a timed challenge token. Timestamps are obtained from a trusted NTP source rather than the client clock. A SHA-256 content hash is computed at signing time and stored alongside the signature, enabling integrity verification at any future point. The entire signing event is recorded in the immutable audit trail with cryptographic chaining.",
                            }
                        ],
                    },
                ],
            },
        },
        # =====================================================================
        # Engineering > Tutorials
        # =====================================================================
        {
            "title": "Setting Up Your Local Development Environment",
            "slug": "setting-up-local-dev-environment",
            "workspace_slug": "engineering",
            "space_slug": "tutorials",
            "classification": "internal",
            "summary": "A tutorial for new developers covering local environment setup, database configuration, and running the full stack.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Setting Up Your Local Development Environment"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This tutorial walks new developers through setting up the documentation-service platform locally. By the end, you will have the backend API, frontend application, database, and search engine running on your machine.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Prerequisites"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Python 3.12 or later"}],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Node.js 20 LTS or later"}],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Docker and Docker Compose"}],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Git"}],
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Step 1: Clone and Install"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "bash"},
                        "content": [
                            {
                                "type": "text",
                                "text": "git clone https://github.com/acme-corp/documentation-service.git\ncd documentation-service\nmake install",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Step 2: Start Infrastructure"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Start PostgreSQL, Meilisearch, and Redis using Docker Compose:",
                            }
                        ],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "bash"},
                        "content": [
                            {
                                "type": "text",
                                "text": "make docker-infra\nmake setup-env\nmake db-upgrade",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Step 3: Seed Sample Data"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "bash"},
                        "content": [
                            {
                                "type": "text",
                                "text": "make seed",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Step 4: Run the Stack"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "bash"},
                        "content": [
                            {
                                "type": "text",
                                "text": "make dev",
                            }
                        ],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "The backend API will be available at http://localhost:8000, the frontend at http://localhost:5173, and the API documentation at http://localhost:8000/api/v1/docs.",
                            }
                        ],
                    },
                ],
            },
        },
        # =====================================================================
        # Engineering > How-to Guides
        # =====================================================================
        {
            "title": "How to Add a New API Endpoint",
            "slug": "how-to-add-new-api-endpoint",
            "workspace_slug": "engineering",
            "space_slug": "how-to-guides",
            "classification": "internal",
            "summary": "A practical guide for adding new REST API endpoints following the project's established patterns.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "How to Add a New API Endpoint"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This guide covers the process of adding a new REST API endpoint to the backend, following the established project patterns for schemas, services, and routers.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "1. Define Pydantic Schemas"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Create your schemas using the three-tier pattern: Base (shared fields), Create (input), and Response (output).",
                            }
                        ],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "python"},
                        "content": [
                            {
                                "type": "text",
                                "text": "# src/modules/myfeature/schemas.py\nfrom pydantic import BaseModel, Field\n\n\nclass WidgetBase(BaseModel):\n    name: str = Field(..., min_length=1, max_length=255)\n    description: str | None = None\n\n\nclass WidgetCreate(WidgetBase):\n    pass\n\n\nclass WidgetResponse(WidgetBase):\n    id: str\n    created_at: datetime\n\n    class Config:\n        from_attributes = True",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "2. Implement the Service Layer"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "The service layer contains business logic and database operations. It receives an AsyncSession from the endpoint and returns model instances.",
                            }
                        ],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "python"},
                        "content": [
                            {
                                "type": "text",
                                "text": "# src/modules/myfeature/service.py\nasync def create_widget(\n    db: AsyncSession, widget_in: WidgetCreate\n) -> Widget:\n    widget = Widget(**widget_in.model_dump())\n    db.add(widget)\n    await db.commit()\n    await db.refresh(widget)\n    return widget",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "3. Create the Router"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Define your FastAPI router in the endpoints directory and register it in the central router file.",
                            }
                        ],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "python"},
                        "content": [
                            {
                                "type": "text",
                                "text": "# src/api/endpoints/widgets.py\nfrom fastapi import APIRouter\nfrom src.api.deps import DbSession, CurrentUser\n\nrouter = APIRouter()\n\n@router.post(\"/\", response_model=WidgetResponse)\nasync def create_widget(\n    widget_in: WidgetCreate,\n    db: DbSession,\n    user: CurrentUser,\n):\n    return await service.create_widget(db, widget_in)",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "4. Register in the Central Router"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "python"},
                        "content": [
                            {
                                "type": "text",
                                "text": "# src/api/router.py\nfrom src.api.endpoints import widgets\n\napi_router.include_router(\n    widgets.router,\n    prefix=\"/widgets\",\n    tags=[\"widgets\"],\n)",
                            }
                        ],
                    },
                ],
            },
        },
        # =====================================================================
        # Engineering > Reference
        # =====================================================================
        {
            "title": "API Authentication Reference",
            "slug": "api-authentication-reference",
            "workspace_slug": "engineering",
            "space_slug": "reference",
            "classification": "internal",
            "summary": "Technical reference for the API authentication system including JWT tokens, session management, and service accounts.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "API Authentication Reference"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This document describes the authentication mechanisms available in the documentation-service API.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "JWT Token Authentication"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "The API uses JWT (JSON Web Tokens) for authentication. Tokens are obtained by POSTing credentials to the login endpoint and must be included in the Authorization header of subsequent requests.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "Obtaining a Token"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "bash"},
                        "content": [
                            {
                                "type": "text",
                                "text": "curl -X POST http://localhost:8000/api/v1/auth/login \\\n  -H \"Content-Type: application/json\" \\\n  -d '{\"email\": \"user@example.com\", \"password\": \"secret\"}'",
                            }
                        ],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Response:",
                            }
                        ],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "json"},
                        "content": [
                            {
                                "type": "text",
                                "text": "{\n  \"access_token\": \"eyJhbGciOiJIUzI1...\",\n  \"refresh_token\": \"eyJhbGciOiJIUzI1...\",\n  \"token_type\": \"bearer\",\n  \"expires_in\": 1800\n}",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "Using the Token"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "bash"},
                        "content": [
                            {
                                "type": "text",
                                "text": "curl -H \"Authorization: Bearer eyJhbGciOiJIUzI1...\" \\\n  http://localhost:8000/api/v1/organizations",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Token Lifetimes"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {"type": "text", "marks": [{"type": "bold"}], "text": "Access token"},
                                            {"type": "text", "text": ": 30 minutes (configurable via ACCESS_TOKEN_EXPIRE_MINUTES)"},
                                        ],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {"type": "text", "marks": [{"type": "bold"}], "text": "Refresh token"},
                                            {"type": "text", "text": ": 7 days (configurable via REFRESH_TOKEN_EXPIRE_DAYS)"},
                                        ],
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Service Account Tokens"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Service accounts are used for machine-to-machine communication, particularly for MCP integrations. Service account tokens are long-lived and scoped to specific permissions. They are created via the Admin dashboard under Settings > Service Accounts.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Session Management"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Each access token is linked to a server-side session record via a JTI (JWT Token ID). Sessions track the user agent, IP address, and last activity time. Sessions expire after 30 minutes of inactivity (configurable). An administrator can revoke individual sessions or all sessions for a user.",
                            }
                        ],
                    },
                ],
            },
        },
        {
            "title": "Database Schema Reference",
            "slug": "database-schema-reference",
            "workspace_slug": "engineering",
            "space_slug": "reference",
            "classification": "confidential",
            "summary": "Complete reference for the PostgreSQL database schema including all tables, columns, relationships, and indexes.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Database Schema Reference"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This document provides a reference for the core database tables in the documentation-service platform. All tables use UUID primary keys and include created_at and updated_at timestamp columns managed by the TimestampMixin.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Core Tables"}],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "users"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Stores authenticated user accounts. Passwords are hashed using Argon2. The clearance_level column (0-3) controls access to classified content.",
                            }
                        ],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "sql"},
                        "content": [
                            {
                                "type": "text",
                                "text": "CREATE TABLE users (\n    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n    email           VARCHAR(255) UNIQUE NOT NULL,\n    hashed_password VARCHAR(255) NOT NULL,\n    full_name       VARCHAR(255) NOT NULL,\n    is_active       BOOLEAN DEFAULT TRUE,\n    is_superuser    BOOLEAN DEFAULT FALSE,\n    clearance_level INTEGER DEFAULT 0,\n    created_at      TIMESTAMPTZ DEFAULT NOW(),\n    updated_at      TIMESTAMPTZ DEFAULT NOW()\n);",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "organizations"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Top-level container. Each organization has its own Git repository, workspaces, and member list. The slug is used for URL routing and Git repository naming.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "workspaces"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Logical groupings within an organization (e.g., Quality Management, Engineering). Each workspace contains multiple spaces.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "spaces"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Containers for pages, optionally typed by Diataxis category. Spaces support nesting via the parent_id self-referential foreign key. Classification is stored as an integer (0=Public, 1=Internal, 2=Confidential, 3=Restricted).",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "pages"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "The core content table. Each page stores TipTap JSON content, version information, lifecycle status, and document control metadata. Pages support hierarchical nesting via parent_id and supersession tracking.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Content Hierarchy"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "Organization\n  \u2514\u2500\u2500 Workspace\n        \u2514\u2500\u2500 Space (diataxis_type)\n              \u2514\u2500\u2500 Page (content, version, status)\n                    \u2514\u2500\u2500 Page (nested child pages)",
                            }
                        ],
                    },
                ],
            },
        },
        # =====================================================================
        # Engineering > Explanation
        # =====================================================================
        {
            "title": "Architecture Decision: Git-Based Content Storage",
            "slug": "adr-git-based-content-storage",
            "workspace_slug": "engineering",
            "space_slug": "explanation",
            "classification": "public",
            "summary": "An ADR explaining why the platform uses Git repositories for content storage and how this supports compliance requirements.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Architecture Decision: Git-Based Content Storage"}],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Status"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Accepted"}],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Context"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "We need a content storage mechanism that provides immutable version history, supports branching for draft workflows, and enables offline-capable operation for air-gapped environments. The system must also satisfy ISO 9001 requirements for document version control and traceability.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Decision"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "We will use local Git repositories as the primary content store. Each organization gets its own repository. Content is stored as JSON files (TipTap document format) organized by workspace and space slugs. Git operations are abstracted behind a service layer so that users never interact with Git concepts directly.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Consequences"}],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "Benefits"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Immutable history satisfies audit trail requirements without additional infrastructure"}],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Branching enables parallel draft workflows without affecting published content"}],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Content can be replicated and backed up using standard Git tooling"}],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Works in air-gapped environments without external service dependencies"}],
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "Trade-offs"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Requires pygit2 (libgit2 bindings), adding a native dependency to the backend"}],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Full-text search requires a separate index (Meilisearch) since Git does not provide search capabilities"}],
                                    }
                                ],
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": "Metadata and relational queries still require PostgreSQL; Git only stores content"}],
                                    }
                                ],
                            },
                        ],
                    },
                ],
            },
        },
        # =====================================================================
        # Compliance > System Documentation
        # =====================================================================
        {
            "title": "System Design Specification (SDS)",
            "slug": "system-design-specification",
            "workspace_slug": "compliance",
            "space_slug": "system-docs",
            "classification": "internal",
            "summary": "Formal system design specification covering platform architecture, technology stack, module breakdown, data model, and security architecture.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "System Design Specification (SDS)"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Document Number: "},
                            {"type": "text", "text": "SDS-PLAT-001 | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Revision: "},
                            {"type": "text", "text": "A | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Classification: "},
                            {"type": "text", "text": "Internal"},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "1. Purpose"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This document defines the system design for the Documentation Service Platform, a Diataxis-based documentation platform with ISO/GxP document control and Git-based content architecture. It provides a technical blueprint for implementation, verification, and ongoing maintenance.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "2. Architecture Overview"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "The platform follows a three-layer architecture: Presentation Layer (React SPA with TipTap editor), Application Layer (FastAPI backend with module-based organization), and Data Layer (PostgreSQL for metadata, Git repositories for content, optional Redis for caching).",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "2.1 Presentation Layer"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "React 18 with TypeScript for type-safe component development"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "TipTap block-based editor with custom extensions (slash commands, code blocks, tables, diagrams)"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "TanStack Query for server state management with optimistic updates"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Zustand for client-side state (authentication, UI preferences)"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Code-split vendor bundles: vendor-react, vendor-editor, vendor-query, vendor-ui"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "2.2 Application Layer"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "FastAPI with async endpoints and Pydantic v2 validation"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Module-based organization: content, access, document-control, audit, learning, ai, mcp, publishing"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "SQLAlchemy 2.0 async ORM with Alembic migrations"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "structlog for structured JSON logging with request context middleware"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "JWT authentication with server-side session tracking"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "2.3 Data Layer"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "PostgreSQL: Metadata, user accounts, permissions, workflows, audit events, assessments"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Git Repositories: Content storage (TipTap JSON), version history, branching for drafts"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Meilisearch: Full-text search indexing across all content"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Redis (optional): Response caching with configurable TTL via @cached decorator"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "3. Module Breakdown"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "The system is organized into nine functional modules, each with its own models, schemas, service layer, and API endpoints:",
                            }
                        ],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Content"}, {"type": "text", "text": " — Organization/Workspace/Space/Page hierarchy, Git abstraction, Diataxis typing"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Access Control"}, {"type": "text", "text": " — Role-based (Owner/Admin/Editor/Reviewer/Viewer) plus classification-based (Public/Internal/Confidential/Restricted) dual-dimension model"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Document Control"}, {"type": "text", "text": " — Lifecycle management (Draft/In Review/Approved/Effective/Obsolete), approval matrices, document numbering, retention policies"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Electronic Signatures"}, {"type": "text", "text": " — 21 CFR Part 11 compliant signatures with re-authentication, NTP timestamps, SHA-256 content hashing, meaning capture"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Audit Trail"}, {"type": "text", "text": " — Append-only event store with cryptographic hash chaining, compliance reporting, export capability"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Learning"}, {"type": "text", "text": " — Document acknowledgment, assessments with multiple question types, learning assignments, quiz attempts, training records"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "AI Services"}, {"type": "text", "text": " — Provider-agnostic service (OpenAI/Anthropic/OpenRouter/Ollama), question generation, writing assistant, document masking"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "MCP Integration"}, {"type": "text", "text": " — Platform as MCP server (expose content) and client (consume external sources), service account management"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Publishing"}, {"type": "text", "text": " — Static site generation, theming, custom domains, visitor access control"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "4. Security Architecture"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Passwords hashed with Argon2; JWT tokens with configurable expiry and server-side session revocation"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Re-authentication challenge tokens for electronic signatures (timed, single-use)"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Classification-based content isolation enforced at query level"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Cryptographic hash chain for audit trail integrity verification"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Request context middleware adding X-Request-ID for traceability"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "5. Deployment Topology"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "The platform supports containerized deployment via Docker Compose for development and single-server production. The backend serves the API on port 8000, the frontend on port 5173 (dev) or as static assets. PostgreSQL, Meilisearch, and Redis run as separate services. Git repositories are stored on a persistent volume. The platform is designed for air-gapped operation with no mandatory external service dependencies.",
                            }
                        ],
                    },
                ],
            },
        },
        {
            "title": "User Requirements Specification (URS)",
            "slug": "user-requirements-specification",
            "workspace_slug": "compliance",
            "space_slug": "system-docs",
            "classification": "internal",
            "summary": "Formal user requirements specification defining intended use, user roles, functional and non-functional requirements, and regulatory requirements.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "User Requirements Specification (URS)"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Document Number: "},
                            {"type": "text", "text": "URS-PLAT-001 | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Revision: "},
                            {"type": "text", "text": "A | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Classification: "},
                            {"type": "text", "text": "Internal"},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "1. Intended Use"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "The Documentation Service Platform is intended for organizations that require controlled documentation with regulatory compliance. It provides collaborative authoring, structured content management using the Diataxis framework, document lifecycle control with electronic signatures, and integrated training and assessment capabilities.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "2. User Roles and Responsibilities"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Owner"}, {"type": "text", "text": " — Full administrative control including organization settings, user management, and approval matrix configuration"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Admin"}, {"type": "text", "text": " — Workspace and space management, approval authority, access control configuration, audit trail review"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Editor"}, {"type": "text", "text": " — Document creation and editing, submission for review, content authoring within assigned spaces"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Reviewer"}, {"type": "text", "text": " — Document review, comment and feedback, approval or rejection of change requests"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Viewer"}, {"type": "text", "text": " — Read-only access to published content, training completion, assessment participation"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "3. Functional Requirements"}],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.1 Content Management"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-CM-001: Users shall be able to create, edit, and organize documentation in a hierarchical structure (Organization > Workspace > Space > Page)"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-CM-002: The editor shall support rich content including headings, lists, tables, code blocks, and diagrams"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-CM-003: Content shall be categorized using the Diataxis framework (Tutorial, How-to, Reference, Explanation)"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-CM-004: Full-text search shall be available across all accessible content"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.2 Document Control"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-DC-001: Documents shall follow a defined lifecycle (Draft > In Review > Approved > Effective > Obsolete)"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-DC-002: Approval workflows shall be configurable per document type with multi-stage approval matrices"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-DC-003: Electronic signatures shall meet 21 CFR Part 11 requirements for identity verification, meaning capture, and non-repudiation"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-DC-004: All document changes shall be captured in an immutable, cryptographically chained audit trail"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.3 Learning and Training"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-LT-001: Assessments shall be linkable to documents for training verification"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-LT-002: Multiple question types shall be supported (multiple choice, true/false, fill in the blank)"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-LT-003: Training completion shall be tracked with pass/fail records and attempt limits"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "4. Non-Functional Requirements"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-NF-001: The system shall support concurrent editing by multiple users"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-NF-002: API response times shall be under 500ms for standard operations"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-NF-003: The system shall be deployable in air-gapped environments without external service dependencies"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-NF-004: The platform shall meet WCAG 2.1 AA accessibility standards"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "5. Regulatory Requirements"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-REG-001: Comply with 21 CFR Part 11 for electronic records and signatures (Sections 11.10, 11.50, 11.70, 11.100, 11.200)"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-REG-002: Comply with ISO 9001:2015 Section 7.5 (Documented Information) for document control"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-REG-003: Comply with ISO 13485:2016 Sections 4.2.4-4.2.5 for medical device documentation control"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "UR-REG-004: Comply with ISO 15489 for records management principles"}]}]},
                        ],
                    },
                ],
            },
        },
        {
            "title": "Functional Requirements Specification (FRS)",
            "slug": "functional-requirements-specification",
            "workspace_slug": "compliance",
            "space_slug": "system-docs",
            "classification": "internal",
            "summary": "Detailed functional requirements organized by module with requirement IDs, traceability to URS, and acceptance criteria.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Functional Requirements Specification (FRS)"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Document Number: "},
                            {"type": "text", "text": "FRS-PLAT-001 | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Revision: "},
                            {"type": "text", "text": "A | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Classification: "},
                            {"type": "text", "text": "Internal"},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "1. Authentication and Session Management"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "ID          Requirement                                          Traces To   Acceptance Criteria\n----------  -------------------------------------------------------  ----------  -----------------------------------------------\nFR-AUTH-001 System shall authenticate users via email/password       UR-NF-001   Login returns JWT access + refresh tokens\nFR-AUTH-002 Passwords shall be hashed with Argon2                    UR-REG-001  Raw passwords never stored or logged\nFR-AUTH-003 Sessions shall track user agent, IP, last activity       UR-REG-001  Session record created on login\nFR-AUTH-004 Sessions shall expire after configurable inactivity      UR-NF-002   Default 30 min, configurable via settings\nFR-AUTH-005 Admin shall be able to revoke individual sessions        UR-REG-001  Revoked token returns 401",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "2. Content Management"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "ID          Requirement                                          Traces To   Acceptance Criteria\n----------  -------------------------------------------------------  ----------  -----------------------------------------------\nFR-CM-001   CRUD operations for Organizations                       UR-CM-001   POST/GET/PUT/DELETE /organizations\nFR-CM-002   CRUD operations for Workspaces within Organizations     UR-CM-001   Workspace scoped to organization\nFR-CM-003   CRUD operations for Spaces with Diataxis typing         UR-CM-003   Space accepts tutorial/how_to/reference/explanation\nFR-CM-004   CRUD operations for Pages with TipTap JSON content      UR-CM-002   Page stores structured JSON content\nFR-CM-005   Content versioned in Git with commit per save           UR-DC-004   Each save creates a Git commit\nFR-CM-006   Full-text search via Meilisearch integration            UR-CM-004   Search returns ranked results across spaces",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "3. Access Control"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "ID          Requirement                                          Traces To   Acceptance Criteria\n----------  -------------------------------------------------------  ----------  -----------------------------------------------\nFR-AC-001   Role hierarchy: Owner > Admin > Editor > Reviewer > Viewer  UR-CM-001  Higher roles inherit lower role permissions\nFR-AC-002   Classification levels: Public/Internal/Confidential/Restricted  UR-REG-002  User clearance_level checked against content\nFR-AC-003   Both role AND classification must grant access           UR-REG-002  Dual-check enforced at query level\nFR-AC-004   Service accounts for machine-to-machine (MCP) access    UR-NF-003   Service account with scoped permissions",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "4. Document Control"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "ID          Requirement                                          Traces To   Acceptance Criteria\n----------  -------------------------------------------------------  ----------  -----------------------------------------------\nFR-DC-001   Lifecycle states: Draft/In Review/Approved/Effective/Obsolete  UR-DC-001  State machine with valid transitions only\nFR-DC-002   Approval matrices configurable per document type         UR-DC-002   Matrix defines stages, roles, min approvals\nFR-DC-003   Document numbering with configurable prefixes            UR-REG-004  Auto-generated numbers (e.g., SOP-QMS-001)\nFR-DC-004   Retention policies with disposition methods              UR-REG-004  Configurable retention periods per type\nFR-DC-005   Periodic review reminders with configurable intervals    UR-REG-002  Review date tracking with notifications",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "5. Electronic Signatures"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "ID          Requirement                                          Traces To   Acceptance Criteria\n----------  -------------------------------------------------------  ----------  -----------------------------------------------\nFR-ES-001   Re-authentication required at signature time             UR-DC-003   Challenge token verified before signing\nFR-ES-002   Signature captures meaning (Authored/Reviewed/Approved/Witnessed)  UR-DC-003  Meaning stored with signature record\nFR-ES-003   NTP-sourced trusted timestamp on each signature          UR-DC-003   Timestamp from server, not client clock\nFR-ES-004   SHA-256 content hash computed and stored at signing      UR-DC-003   Hash enables integrity verification\nFR-ES-005   Signature verification endpoint                         UR-DC-003   GET /signatures/{id}/verify returns validity",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "6. Audit Trail"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "ID          Requirement                                          Traces To   Acceptance Criteria\n----------  -------------------------------------------------------  ----------  -----------------------------------------------\nFR-AT-001   Append-only audit event store                            UR-DC-004   No UPDATE or DELETE on audit_events table\nFR-AT-002   Cryptographic hash chain linking sequential events       UR-DC-004   Each event hashes previous event's hash\nFR-AT-003   Audit events capture: who, what, when, where, why       UR-DC-004   All fields populated on every event\nFR-AT-004   Export capability for external auditors                  UR-REG-001  CSV/JSON export with date range filtering\nFR-AT-005   Chain integrity verification endpoint                   UR-DC-004   Detects any tampered or missing events",
                            }
                        ],
                    },
                ],
            },
        },
        {
            "title": "Risk Assessment (FMEA)",
            "slug": "risk-assessment-fmea",
            "workspace_slug": "compliance",
            "space_slug": "system-docs",
            "classification": "internal",
            "summary": "Failure Modes and Effects Analysis covering data integrity, access control, audit trail, electronic signatures, and system availability risks.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Risk Assessment — Failure Modes and Effects Analysis (FMEA)"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Document Number: "},
                            {"type": "text", "text": "RA-PLAT-001 | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Revision: "},
                            {"type": "text", "text": "A | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Classification: "},
                            {"type": "text", "text": "Internal"},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "1. Methodology"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This FMEA uses a Risk Priority Number (RPN) calculated as Severity (1-10) x Probability (1-10) x Detectability (1-10). Risks with RPN above 100 require mitigation controls. The assessment covers five categories: Data Integrity, Access Control, Audit Trail, Electronic Signatures, and System Availability.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "2. Risk Matrix"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "Severity Scale          Probability Scale       Detectability Scale\n1-2: Negligible         1-2: Remote             1-2: Almost certain detection\n3-4: Minor              3-4: Unlikely           3-4: High detection\n5-6: Moderate           5-6: Possible           5-6: Moderate detection\n7-8: Major              7-8: Likely             7-8: Low detection\n9-10: Critical          9-10: Almost certain    9-10: Undetectable",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "3. Data Integrity Risks"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "ID        Failure Mode                      S   P   D   RPN  Mitigation Control\n--------  --------------------------------  --  --  --  ---  -----------------------------------------\nDI-001    Content corruption during save     9   2   3   54   Git atomic commits; content validated before write\nDI-002    Database/Git content mismatch      8   3   4   96   Reconciliation check on page load\nDI-003    Loss of version history            9   2   2   36   Git immutable history; backup procedures\nDI-004    Unauthorized content modification  9   3   2   54   Role-based access + audit trail detection\nDI-005    Search index stale after update    4   5   3   60   Sync-on-write to Meilisearch; health check",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "4. Access Control Risks"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "ID        Failure Mode                      S   P   D   RPN  Mitigation Control\n--------  --------------------------------  --  --  --  ---  -----------------------------------------\nAC-001    Privilege escalation               9   2   3   54   Role hierarchy enforced at API layer\nAC-002    Classification bypass              8   2   4   64   Dual-dimension check at query level\nAC-003    Session hijacking                  8   3   3   72   Server-side sessions; IP/UA tracking\nAC-004    Stale permissions after role change 6   4   3   72   Permission check on every request\nAC-005    Service account over-permissioning 7   4   5  140   Scoped permissions; usage audit logging",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "5. Audit Trail Risks"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "ID        Failure Mode                      S   P   D   RPN  Mitigation Control\n--------  --------------------------------  --  --  --  ---  -----------------------------------------\nAT-001    Audit event not recorded           9   2   3   54   Middleware captures all state changes\nAT-002    Hash chain broken by tampering    10   2   2   40   Chain verification endpoint; periodic check\nAT-003    Audit storage exhaustion           6   4   5  120   Retention policies; monitoring alerts\nAT-004    Missing reason for change          7   3   3   63   Required field validation on state transitions",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "6. Electronic Signature Risks"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "ID        Failure Mode                      S   P   D   RPN  Mitigation Control\n--------  --------------------------------  --  --  --  ---  -----------------------------------------\nES-001    Signature applied without re-auth 10   2   2   40   Challenge token required; timed expiry\nES-002    Content modified after signing    10   2   2   40   SHA-256 hash comparison on verification\nES-003    Clock skew in timestamps           7   3   3   63   NTP-sourced server timestamps\nES-004    Signature meaning not captured     8   2   2   32   Required field; enum validation",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "7. System Availability Risks"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "ID        Failure Mode                      S   P   D   RPN  Mitigation Control\n--------  --------------------------------  --  --  --  ---  -----------------------------------------\nSA-001    Database connection pool exhausted 7   4   3   84   Configurable pool size; health check\nSA-002    Git repository corruption          9   2   4   72   Regular backups; fsck verification\nSA-003    Redis cache unavailable            3   4   2   24   Graceful degradation; cache optional\nSA-004    Meilisearch index failure          5   3   3   45   Re-index capability; health check",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "8. Summary"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Two risks exceed the RPN threshold of 100 and require active mitigation: AC-005 (service account over-permissioning, RPN 140) is mitigated by scoped permissions and mandatory usage audit logging. AT-003 (audit storage exhaustion, RPN 120) is mitigated by configurable retention policies and disk space monitoring. All other risks are within acceptable limits with existing platform controls.",
                            }
                        ],
                    },
                ],
            },
        },
        {
            "title": "Validation Plan (IQ/OQ/PQ)",
            "slug": "validation-plan",
            "workspace_slug": "compliance",
            "space_slug": "system-docs",
            "classification": "internal",
            "summary": "Validation strategy with Installation, Operational, and Performance Qualification protocols, acceptance criteria, and deviation handling.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Validation Plan (IQ/OQ/PQ)"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Document Number: "},
                            {"type": "text", "text": "VP-PLAT-001 | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Revision: "},
                            {"type": "text", "text": "A | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Classification: "},
                            {"type": "text", "text": "Internal"},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "1. Validation Strategy"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This plan follows GAMP 5 Category 5 (Custom Application) validation methodology with a risk-based approach. Validation activities are organized into three qualification phases: Installation Qualification (IQ), Operational Qualification (OQ), and Performance Qualification (PQ). Each phase includes specific test protocols, acceptance criteria, and documentation requirements.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "2. Installation Qualification (IQ)"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "IQ verifies that all system components are installed correctly and match approved specifications."}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "ID        Test                                  Acceptance Criteria\n--------  ------------------------------------  -------------------------------------------\nIQ-001    PostgreSQL version and configuration  Version >= 15; UTF-8 encoding; UUID extension\nIQ-002    Python runtime version                Version >= 3.12\nIQ-003    Backend dependencies installed         All requirements.txt packages present\nIQ-004    Database migrations applied            Alembic 'current' matches latest revision\nIQ-005    Git service initialized                Organization repo created successfully\nIQ-006    Meilisearch connectivity               Health endpoint returns 200\nIQ-007    Redis connectivity (if configured)     PING returns PONG\nIQ-008    Frontend build artifacts               dist/ directory contains index.html + assets",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "3. Operational Qualification (OQ)"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "OQ verifies that the system operates according to functional requirements under normal conditions."}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "ID        Test                                  Traces To    Acceptance Criteria\n--------  ------------------------------------  -----------  -------------------------------------------\nOQ-001    User registration and login           FR-AUTH-001  Token returned; session created\nOQ-002    Role-based access enforcement          FR-AC-001    Viewer cannot edit; Editor cannot approve\nOQ-003    Classification-based filtering         FR-AC-002    Users see only content at their clearance\nOQ-004    Document lifecycle transitions         FR-DC-001    Invalid transitions rejected with 400\nOQ-005    Electronic signature with re-auth      FR-ES-001    Signature fails without valid challenge\nOQ-006    Audit event creation                   FR-AT-001    Event recorded for each state change\nOQ-007    Hash chain integrity                   FR-AT-002    Verification endpoint confirms chain valid\nOQ-008    Content search indexing                FR-CM-006    New content searchable within 5 seconds\nOQ-009    Assessment creation and scoring        UR-LT-002    Questions saved; scoring calculated correctly\nOQ-010    Approval matrix enforcement            FR-DC-002    Document requires all matrix approvals",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "4. Performance Qualification (PQ)"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "PQ verifies that the system performs reliably under realistic operational conditions."}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "ID        Test                                  Acceptance Criteria\n--------  ------------------------------------  -------------------------------------------\nPQ-001    API response time under load           95th percentile < 500ms at 50 concurrent users\nPQ-002    Concurrent document editing            No data loss with 5 simultaneous editors\nPQ-003    Database connection pool behavior       No connection failures under normal load\nPQ-004    Git operations under volume             1000 pages in repo; operations < 2 seconds\nPQ-005    Search performance at scale             Search returns results < 200ms with 1000 docs\nPQ-006    Audit trail integrity after volume      Hash chain valid after 10,000 events",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "5. Deviation Handling"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Any test failure is documented as a deviation. Deviations are classified as Critical (blocks release — compliance or data integrity impact), Major (requires resolution before production use), or Minor (acceptable with documented justification). Critical deviations require root cause analysis and corrective action before retest. All deviations are recorded in the audit trail with resolution details.",
                            }
                        ],
                    },
                ],
            },
        },
        # =====================================================================
        # Compliance > SOPs
        # =====================================================================
        {
            "title": "SOP: Document Creation and Approval",
            "slug": "sop-document-creation-and-approval",
            "workspace_slug": "compliance",
            "space_slug": "sops",
            "classification": "public",
            "summary": "Standard Operating Procedure for creating, reviewing, approving, and publishing controlled documents.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "SOP: Document Creation and Approval"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "marks": [{"type": "bold"}], "text": "SOP Number: "},
                            {"type": "text", "text": "SOP-DOC-001 | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Effective Date: "},
                            {"type": "text", "text": "2025-01-15 | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Review Date: "},
                            {"type": "text", "text": "2026-01-15"},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "1. Purpose and Scope"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This SOP defines the procedure for creating, reviewing, approving, and publishing controlled documents in the Documentation Service Platform. It applies to all document types including SOPs, work instructions, policies, and reference documents. Compliance: ISO 9001:2015 Section 7.5.2 (Creating and Updating), ISO 13485:2016 Section 4.2.4.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "2. Responsibilities"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Document Author (Editor role)"}, {"type": "text", "text": " — Creates document content, assigns metadata, submits for review"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Reviewer (Reviewer role)"}, {"type": "text", "text": " — Reviews content for accuracy and completeness, provides feedback or approval"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Approver (Admin role)"}, {"type": "text", "text": " — Final approval authority, applies electronic signature, transitions to Effective"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Quality Manager (Admin role)"}, {"type": "text", "text": " — Configures approval matrices, monitors periodic review compliance"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "3. Procedure"}],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.1 Document Creation"}],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Navigate to the appropriate workspace and space for the document type."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Click \"New Page\" and enter a descriptive title following naming conventions (e.g., \"SOP: [Process Name]\")."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Set the classification level (Public, Internal, Confidential, or Restricted) based on content sensitivity."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Author the document content using the block editor. Use the slash command menu (/) for formatting options."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Content is auto-saved. Each save creates a version in the Git history for traceability."}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.2 Submission for Review"}],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Verify the document is complete and self-review is done."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Click \"Submit for Review\" to transition from Draft to In Review status."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "The system routes the document to reviewers per the configured approval matrix for the document type."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Content is locked from editing while In Review (reviewers may add comments)."}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.3 Review and Approval"}],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Reviewers evaluate technical accuracy, regulatory compliance, and completeness."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Reviewers select Approve, Request Changes, or Reject for their review stage."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "If changes are requested, the document returns to Draft with reviewer feedback attached."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "The final approver applies an electronic signature (see SOP-ESIG-001) to transition to Approved status."}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.4 Publishing and Periodic Review"}],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Approved documents are transitioned to Effective status, making them visible on published sites."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Any previous effective version is automatically moved to Obsolete status."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "The system sets the next periodic review date based on the document type's review interval."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Periodic review notifications are sent to the document owner when the review date approaches."}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "4. References"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "SOP-ESIG-001: Electronic Signature Use"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "ISO 9001:2015 Section 7.5.2 — Creating and Updating Documented Information"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "ISO 13485:2016 Section 4.2.4 — Control of Documents"}]}]},
                        ],
                    },
                ],
            },
        },
        {
            "title": "SOP: Electronic Signature Use",
            "slug": "sop-electronic-signature-use",
            "workspace_slug": "compliance",
            "space_slug": "sops",
            "classification": "public",
            "summary": "Standard Operating Procedure for applying and verifying electronic signatures in compliance with 21 CFR Part 11.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "SOP: Electronic Signature Use"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "marks": [{"type": "bold"}], "text": "SOP Number: "},
                            {"type": "text", "text": "SOP-ESIG-001 | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Effective Date: "},
                            {"type": "text", "text": "2025-01-15 | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Review Date: "},
                            {"type": "text", "text": "2026-01-15"},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "1. Purpose and Scope"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This SOP defines the procedure for applying electronic signatures to controlled documents. Electronic signatures in this platform are legally binding and equivalent to handwritten signatures per 21 CFR Part 11 Sections 11.50, 11.70, 11.100, and 11.200. This procedure applies to all approval, review, and witnessing actions that require a signature.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "2. Responsibilities"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Signer"}, {"type": "text", "text": " — Ensures they are authorized, understands the meaning of their signature, and completes re-authentication"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "System Administrator"}, {"type": "text", "text": " — Maintains NTP synchronization, monitors signature verification logs"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "3. Procedure"}],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.1 When Signatures Are Required"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Electronic signatures are required for: transitioning a document from In Review to Approved status, approving a change request, and witnessing a document acknowledgment where mandated by the approval matrix."}],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.2 Signature Meanings"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Each signature must include one of the following meanings:"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Authored"}, {"type": "text", "text": " — The signer created or substantially contributed to the document content"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Reviewed"}, {"type": "text", "text": " — The signer has reviewed the document for accuracy and completeness"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Approved"}, {"type": "text", "text": " — The signer authorizes the document for release as an effective document"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Witnessed"}, {"type": "text", "text": " — The signer attests to having observed the signing process or acknowledges the document"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.3 Applying a Signature"}],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Navigate to the document and click the \"Sign\" or \"Approve\" button."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Select the signature meaning from the dropdown (Authored, Reviewed, Approved, or Witnessed)."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "The system will prompt for re-authentication. Enter your email and password to confirm your identity."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "The system generates a timed challenge token (valid for 5 minutes). Complete the signing within this window."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Upon successful re-authentication, the system records: your identity, signature meaning, NTP-sourced timestamp, and a SHA-256 hash of the document content at signing time."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "The signature is linked to the specific Git commit of the content, ensuring non-repudiation."}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.4 Signature Verification"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Any user can verify a signature by navigating to the document's signature panel and clicking \"Verify.\" The system recomputes the content hash and compares it with the stored hash. A valid verification confirms that the content has not been modified since signing. Verification results are logged in the audit trail.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "4. References"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "21 CFR Part 11, Sections 11.50, 11.70, 11.100, 11.200"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "SOP-DOC-001: Document Creation and Approval"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "SOP-AUDIT-001: Audit Trail Review"}]}]},
                        ],
                    },
                ],
            },
        },
        {
            "title": "SOP: Access Control Management",
            "slug": "sop-access-control-management",
            "workspace_slug": "compliance",
            "space_slug": "sops",
            "classification": "internal",
            "summary": "Standard Operating Procedure for managing user roles, classification levels, and access permissions.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "SOP: Access Control Management"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "marks": [{"type": "bold"}], "text": "SOP Number: "},
                            {"type": "text", "text": "SOP-AC-001 | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Effective Date: "},
                            {"type": "text", "text": "2025-01-15 | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Review Date: "},
                            {"type": "text", "text": "2026-01-15"},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "1. Purpose and Scope"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This SOP defines the procedure for managing access controls in the Documentation Service Platform. It covers role assignment, classification clearance levels, periodic access reviews, and service account management. Compliance: ISO 9001:2015 Section 7.5.3 (Control of Documented Information), 21 CFR Part 11 Section 11.10(d).",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "2. Responsibilities"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Organization Owner"}, {"type": "text", "text": " — Ultimate authority for access grants; approves Admin role assignments"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Administrator"}, {"type": "text", "text": " — Day-to-day access management; assigns Editor, Reviewer, Viewer roles; manages classification clearances"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "All Users"}, {"type": "text", "text": " — Report access issues; do not share credentials; log out of shared workstations"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "3. Procedure"}],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.1 Role Definitions"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "Role       Permissions                                    Hierarchy Level\n---------  ---------------------------------------------  ---------------\nOwner      Full control, org settings, user management     5 (highest)\nAdmin      Workspace/space mgmt, approvals, audit review   4\nEditor     Create/edit documents, submit for review        3\nReviewer   Review documents, approve/reject                2\nViewer     Read-only access, training completion           1 (lowest)",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.2 Classification Levels"}],
                    },
                    {
                        "type": "codeBlock",
                        "attrs": {"language": "text"},
                        "content": [
                            {
                                "type": "text",
                                "text": "Level        Clearance Required   Description\n-----------  -------------------  ------------------------------------------\nPublic       0                    Available to all authenticated users\nInternal     1                    Restricted to organization members\nConfidential 2                    Limited to specifically authorized users\nRestricted   3                    Highest sensitivity; Owner/Admin only",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.3 Granting Access"}],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Navigate to Settings > Users & Permissions."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Select the user and assign the appropriate role based on their job function."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Set the clearance level based on the sensitivity of content they need to access."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Both role AND clearance must be sufficient for content access (dual-dimension model)."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "All access changes are recorded in the audit trail automatically."}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.4 Periodic Access Reviews"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Access reviews shall be conducted quarterly by the Organization Owner or designated Administrator. Review all active user accounts, verify role assignments are current, remove access for departed users, and document the review outcome. Users with Confidential or Restricted clearance require explicit re-authorization during each review.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.5 Service Account Management"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Service accounts for MCP integrations are created under Settings > Service Accounts. Each service account must have a designated human owner, scoped permissions limited to required resources, and mandatory usage audit logging. Service account tokens are long-lived but can be revoked immediately. Review service account permissions during quarterly access reviews.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "4. References"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "ISO 9001:2015 Section 7.5.3 — Control of Documented Information"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "21 CFR Part 11 Section 11.10(d) — Limiting system access to authorized individuals"}]}]},
                        ],
                    },
                ],
            },
        },
        {
            "title": "SOP: Audit Trail Review",
            "slug": "sop-audit-trail-review",
            "workspace_slug": "compliance",
            "space_slug": "sops",
            "classification": "internal",
            "summary": "Standard Operating Procedure for reviewing, verifying, and reporting on the system audit trail.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "SOP: Audit Trail Review"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "marks": [{"type": "bold"}], "text": "SOP Number: "},
                            {"type": "text", "text": "SOP-AUDIT-001 | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Effective Date: "},
                            {"type": "text", "text": "2025-01-15 | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Review Date: "},
                            {"type": "text", "text": "2026-01-15"},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "1. Purpose and Scope"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This SOP defines the procedure for reviewing the system audit trail, verifying hash chain integrity, and identifying anomalies. The audit trail is the primary compliance evidence for 21 CFR Part 11 Section 11.10(e) and ISO 9001:2015 Section 7.5.3. This procedure applies to routine scheduled reviews and ad-hoc investigations.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "2. Responsibilities"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Quality Assurance / Auditor"}, {"type": "text", "text": " — Conducts routine reviews, documents findings, escalates anomalies"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "System Administrator"}, {"type": "text", "text": " — Maintains audit storage, runs integrity verification, provides export access"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "3. Procedure"}],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.1 Routine Review Schedule"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Audit trail reviews shall be conducted monthly. The review covers all events from the previous calendar month. Schedule additional reviews after security incidents, system updates, or regulatory audit preparation."}],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.2 Hash Chain Verification"}],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Navigate to Admin > Audit Trail > Integrity Check."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Click \"Verify Chain\" to initiate a full hash chain verification."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "The system recalculates each event's hash using the previous event's hash as input."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "A successful verification confirms that no events have been tampered with, deleted, or inserted."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "If verification fails, document the break point and escalate immediately per the incident response procedure."}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.3 Anomaly Detection"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "During review, look for the following anomalies:"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Access attempts outside normal business hours"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Repeated failed login attempts for any account"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Permission changes not correlated with approved access requests"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Document lifecycle transitions that bypass normal workflow (e.g., Draft directly to Effective)"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Service account activity outside expected patterns"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.4 Export and Reporting"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Audit events can be exported via Admin > Audit Trail > Export. Select the date range, event types, and format (CSV or JSON). Exports include all event fields: timestamp, user, action, resource, IP address, and hash chain values. Store exports securely and include them in regulatory submission packages as required.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "4. References"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "21 CFR Part 11 Section 11.10(e) — Audit trail requirements"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "ISO 9001:2015 Section 7.5.3 — Control of Documented Information"}]}]},
                        ],
                    },
                ],
            },
        },
        {
            "title": "SOP: System Administration and Backup",
            "slug": "sop-system-administration-and-backup",
            "workspace_slug": "compliance",
            "space_slug": "sops",
            "classification": "internal",
            "summary": "Standard Operating Procedure for system health monitoring, backup procedures, disaster recovery, and environment management.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "SOP: System Administration and Backup"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "marks": [{"type": "bold"}], "text": "SOP Number: "},
                            {"type": "text", "text": "SOP-ADMIN-001 | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Effective Date: "},
                            {"type": "text", "text": "2025-01-15 | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Review Date: "},
                            {"type": "text", "text": "2026-01-15"},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "1. Purpose and Scope"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This SOP defines procedures for system administration including health monitoring, database backup, Git repository backup, Redis cache management, and disaster recovery. It ensures system availability and data integrity as required by ISO 9001:2015 and 21 CFR Part 11.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "2. Responsibilities"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "System Administrator"}, {"type": "text", "text": " — Performs all procedures in this SOP; monitors system health daily"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Organization Owner"}, {"type": "text", "text": " — Approves backup schedules and disaster recovery plans"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "3. Procedure"}],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.1 Health Monitoring"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "The platform exposes a health check endpoint at GET /health that returns the status of all service dependencies:"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "database"}, {"type": "text", "text": " — PostgreSQL connectivity and query execution"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "redis"}, {"type": "text", "text": " — Redis connectivity (if configured)"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "meilisearch"}, {"type": "text", "text": " — Search engine connectivity and index status"}]}]},
                        ],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Configure monitoring to poll /health every 60 seconds. Alert on any non-healthy component status."}],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.2 Database Backup"}],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Schedule daily automated pg_dump backups with point-in-time recovery enabled."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Store backups on a separate volume or off-site location with encryption at rest."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Retain daily backups for 30 days, weekly backups for 90 days, and monthly backups for 1 year."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Test backup restoration quarterly on a staging environment to verify integrity."}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.3 Git Repository Backup"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Git repositories are stored under the configured git_repos_path. Back up the entire directory using filesystem-level snapshots or rsync. Git's built-in integrity checking (git fsck) should be run weekly to detect any repository corruption. If a remote is configured, push to the remote regularly as an additional backup layer.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.4 Disaster Recovery"}],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Restore the PostgreSQL database from the most recent backup using pg_restore."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Restore Git repositories from filesystem backup to the configured git_repos_path."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Verify database migrations are current with alembic current."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Rebuild the Meilisearch index from database records."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Verify system health via the /health endpoint before restoring user access."}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "4. References"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "SOP-CC-001: Change Control for System Updates"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Operations Runbook (docs/how-to/ops-runbook.md)"}]}]},
                        ],
                    },
                ],
            },
        },
        {
            "title": "SOP: Change Control for System Updates",
            "slug": "sop-change-control-system-updates",
            "workspace_slug": "compliance",
            "space_slug": "sops",
            "classification": "internal",
            "summary": "Standard Operating Procedure for managing system changes including impact assessment, testing, deployment, and rollback.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "SOP: Change Control for System Updates"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "marks": [{"type": "bold"}], "text": "SOP Number: "},
                            {"type": "text", "text": "SOP-CC-001 | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Effective Date: "},
                            {"type": "text", "text": "2025-01-15 | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Review Date: "},
                            {"type": "text", "text": "2026-01-15"},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "1. Purpose and Scope"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "This SOP defines the change control process for all system updates including code changes, dependency updates, configuration changes, and infrastructure modifications. It ensures that changes are assessed for risk, tested in a staging environment, and deployed with rollback capability. Compliance: ISO 9001:2015 Section 8.5.6 (Control of Changes).",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "2. Responsibilities"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Change Requestor"}, {"type": "text", "text": " — Submits change request with description, justification, and impact assessment"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "System Administrator"}, {"type": "text", "text": " — Implements approved changes, executes deployment, performs verification"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Change Approver (Admin/Owner)"}, {"type": "text", "text": " — Reviews impact assessment, approves or rejects change request"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "3. Procedure"}],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.1 Change Request Submission"}],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Document the proposed change with: description, justification, affected components, and risk classification (Low/Medium/High)."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Identify potential impacts on data integrity, audit trail, electronic signatures, and access controls."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Submit the change request for approval. High-risk changes require Owner-level approval."}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.2 Testing Requirements"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Low risk"}, {"type": "text", "text": " — Unit tests pass; peer code review completed"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Medium risk"}, {"type": "text", "text": " — Unit + integration tests pass; deployed and verified on staging environment"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "High risk"}, {"type": "text", "text": " — Full test suite including compliance tests; staging verification with sign-off; rollback procedure tested"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.3 Deployment"}],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Create a database backup before deployment (see SOP-ADMIN-001)."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Apply database migrations if required (alembic upgrade head)."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Deploy the updated application code."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Verify system health via the /health endpoint."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Run post-deployment verification checks (audit trail integrity, search index, signature verification)."}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.4 Rollback Procedure"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "If post-deployment verification fails or critical issues are discovered: revert the application to the previous version, run alembic downgrade if migrations were applied, restore the database from the pre-deployment backup if data corruption occurred, and verify system health before restoring user access. Document all rollback actions in the change request record.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 3},
                        "content": [{"type": "text", "text": "3.5 Post-Deployment Documentation"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "After successful deployment, update all affected documentation including API references, configuration guides, and user-facing help content. Record the change in the system changelog. If the change affects compliance features (audit trail, signatures, access control), update the corresponding validation records.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "4. References"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "SOP-ADMIN-001: System Administration and Backup"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "ISO 9001:2015 Section 8.5.6 — Control of Changes"}]}]},
                        ],
                    },
                ],
            },
        },
        # =====================================================================
        # Compliance > Training
        # =====================================================================
        {
            "title": "System Administrator Training",
            "slug": "training-system-administrator",
            "workspace_slug": "compliance",
            "space_slug": "training",
            "classification": "internal",
            "summary": "Role-based training module for system administrators covering platform architecture, configuration, monitoring, backup, and troubleshooting.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "System Administrator Training"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Target Role: "},
                            {"type": "text", "text": "System Administrators | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Estimated Duration: "},
                            {"type": "text", "text": "2 hours"},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Learning Objectives"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "After completing this training, you will be able to:"}],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Describe the platform's three-layer architecture and key service dependencies"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Configure environment settings for database connections, caching, and logging"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Manage user accounts, roles, and classification clearances"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Monitor system health and respond to alerts"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Perform backup and disaster recovery procedures"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Verify audit trail integrity using the hash chain verification endpoint"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 1: Platform Architecture"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "The Documentation Service Platform consists of three layers. The Presentation Layer is a React SPA served as static files. The Application Layer is a FastAPI backend providing REST APIs. The Data Layer includes PostgreSQL (metadata and workflows), Git repositories (content storage), Meilisearch (search indexing), and optionally Redis (response caching). All components communicate over local network connections. The platform is designed for air-gapped deployment with no mandatory external dependencies.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 2: Environment Configuration"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Configuration is managed through environment variables loaded via Pydantic BaseSettings. Key settings include: DATABASE_URL for PostgreSQL connection, REDIS_URL for cache (optional), MEILISEARCH_URL and MEILISEARCH_API_KEY for search, GIT_REPOS_PATH for content storage location, and SECRET_KEY for JWT signing. Database pool tuning is available via DB_POOL_SIZE (default 5), DB_MAX_OVERFLOW (default 10), and DB_POOL_TIMEOUT (default 30 seconds).",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 3: Health Monitoring"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "The /health endpoint returns a JSON response with the status of each service dependency: database, redis, and meilisearch. Each check reports \"healthy\" or \"unhealthy\" with details. The overall status is \"healthy\" only when all configured services are operational. Configure your monitoring system to poll this endpoint at 60-second intervals and alert on degraded status. Response times are included via the X-Response-Time header added by the request context middleware.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 4: Backup and Recovery"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Database backups use pg_dump with custom format for efficient storage and selective restoration. Git repositories are backed up via filesystem-level copies of the git_repos_path directory. Run git fsck weekly on each repository to verify integrity. For disaster recovery, restore PostgreSQL first, then Git repositories, verify migrations with alembic current, rebuild the Meilisearch index, and validate via /health before restoring user access. See SOP-ADMIN-001 for detailed procedures.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 5: Audit Trail Verification"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "The audit trail uses a cryptographic hash chain where each event includes a hash computed from the event data combined with the previous event's hash. To verify integrity, navigate to Admin > Audit Trail > Integrity Check and click Verify Chain. A broken chain indicates potential tampering and must be investigated immediately. See SOP-AUDIT-001 for the full review procedure.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Key Takeaways"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Always verify system health via /health after any configuration change or deployment"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Back up both PostgreSQL and Git repositories — they contain complementary data"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Audit trail integrity verification should be part of your monthly routine"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Redis is optional — the platform degrades gracefully without it"}]}]},
                        ],
                    },
                ],
            },
            "assessment": {
                "title": "System Administrator Competency Assessment",
                "description": "Verify understanding of system administration responsibilities and procedures.",
                "passing_score": 80,
                "max_attempts": 3,
                "questions": [
                    {
                        "question_type": "multiple_choice",
                        "question_text": "What components does the /health endpoint check?",
                        "options": [
                            {"id": "a", "text": "CPU usage, memory, and disk space", "is_correct": False},
                            {"id": "b", "text": "Database, Redis, and Meilisearch", "is_correct": True},
                            {"id": "c", "text": "Frontend build status and API latency", "is_correct": False},
                            {"id": "d", "text": "Git repository size and commit count", "is_correct": False},
                        ],
                        "correct_answer": "b",
                        "explanation": "The /health endpoint checks the status of three service dependencies: database (PostgreSQL), redis (if configured), and meilisearch. It does not monitor system resources like CPU or disk.",
                        "points": 2,
                    },
                    {
                        "question_type": "multiple_choice",
                        "question_text": "Which database backup approach does the platform recommend?",
                        "options": [
                            {"id": "a", "text": "Application-level data export via the API", "is_correct": False},
                            {"id": "b", "text": "pg_dump with custom format and point-in-time recovery", "is_correct": True},
                            {"id": "c", "text": "Filesystem copy of the PostgreSQL data directory", "is_correct": False},
                            {"id": "d", "text": "Replication to a read-only standby server only", "is_correct": False},
                        ],
                        "correct_answer": "b",
                        "explanation": "The platform recommends pg_dump with custom format for efficient storage and selective restoration, combined with point-in-time recovery for minimal data loss.",
                        "points": 2,
                    },
                    {
                        "question_type": "multiple_choice",
                        "question_text": "What should you do immediately if the hash chain verification fails?",
                        "options": [
                            {"id": "a", "text": "Restart the application server and retry", "is_correct": False},
                            {"id": "b", "text": "Delete and rebuild the audit trail from Git history", "is_correct": False},
                            {"id": "c", "text": "Document the break point and escalate per the incident response procedure", "is_correct": True},
                            {"id": "d", "text": "Ignore it if the overall system health is healthy", "is_correct": False},
                        ],
                        "correct_answer": "c",
                        "explanation": "A hash chain verification failure indicates potential tampering with the audit trail, which is a compliance-critical issue. The break point must be documented and escalated immediately for investigation.",
                        "points": 2,
                    },
                    {
                        "question_type": "true_false",
                        "question_text": "Redis cache is required for the Documentation Service Platform to function correctly.",
                        "options": None,
                        "correct_answer": "false",
                        "explanation": "Redis is optional. The platform is designed to degrade gracefully without Redis — caching simply improves response times but is not required for correctness.",
                        "points": 2,
                    },
                    {
                        "question_type": "fill_blank",
                        "question_text": "The environment variable that controls the database connection pool size is ___.",
                        "options": None,
                        "correct_answer": "DB_POOL_SIZE",
                        "explanation": "DB_POOL_SIZE controls how many connections are maintained in the SQLAlchemy connection pool. The default value is 5.",
                        "points": 2,
                    },
                ],
            },
        },
        {
            "title": "Document Author Training",
            "slug": "training-document-author",
            "workspace_slug": "compliance",
            "space_slug": "training",
            "classification": "public",
            "summary": "Role-based training module for document authors covering the editor, content types, document lifecycle, and submission for review.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Document Author Training"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Target Role: "},
                            {"type": "text", "text": "Document Authors (Editor role) | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Estimated Duration: "},
                            {"type": "text", "text": "1.5 hours"},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Learning Objectives"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "After completing this training, you will be able to:"}],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Create and format documents using the block-based editor"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Select the correct Diataxis content type for your document"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Use slash commands for efficient content creation"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Navigate the document lifecycle from Draft to submission"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Work with change requests for effective documents"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 1: The Block Editor"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "The platform uses a TipTap-based block editor. Each element (paragraph, heading, list, table, code block) is a discrete block that can be rearranged, styled, and nested. Content is auto-saved on every change, with each save creating a version in the Git history for full traceability. Use the toolbar for formatting or type the slash (/) character to open the command menu.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 2: Diataxis Content Types"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Each space is associated with a Diataxis content type. Choose the correct type based on your document's purpose:"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Tutorial"}, {"type": "text", "text": " — Step-by-step learning exercises for beginners. Focus on teaching skills, not completing tasks."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "How-to Guide"}, {"type": "text", "text": " — Task-oriented instructions for experienced users. Assumes competence, solves a specific problem."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Reference"}, {"type": "text", "text": " — Technical descriptions of APIs, schemas, configurations. Structured around the code, not user tasks."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "marks": [{"type": "bold"}], "text": "Explanation"}, {"type": "text", "text": " — Conceptual background answering \"why\" questions. Provides context for design decisions."}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 3: Slash Commands"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "Type / at the start of a line to access the slash command menu. Common commands include:"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "/heading 1, /heading 2, /heading 3 — Insert headings at different levels"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "/bullet list, /ordered list — Insert list blocks"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "/table — Insert a table with configurable rows and columns"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "/code block — Insert a code block with syntax highlighting"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "/image — Insert an image from an attachment or URL"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 4: Document Lifecycle"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Documents follow this lifecycle: Draft (editable, only visible to author and collaborators), In Review (locked, under formal review), Approved (signed off, ready to go effective), Effective (current active version, visible on published sites), Obsolete (superseded by newer version, retained for audit). As an author, you create documents in Draft and submit them for review. Once a document is Effective, changes require creating a new change request which starts a new Draft revision.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 5: Working with Attachments"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Files can be attached to documents via the attachment panel or by dragging and dropping into the editor. Supported formats include images (PNG, JPG, SVG), documents (PDF), and data files (CSV, XLSX). Attachments are stored in the configured storage backend (local filesystem or S3-compatible) and linked to the page record.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Key Takeaways"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Every save is versioned — you can always recover previous content from Git history"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Choose the right Diataxis type before writing — it guides the structure and tone"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Effective documents cannot be edited directly — create a change request for modifications"}]}]},
                        ],
                    },
                ],
            },
            "assessment": {
                "title": "Document Author Competency Assessment",
                "description": "Verify understanding of document authoring procedures and editor functionality.",
                "passing_score": 80,
                "max_attempts": 3,
                "questions": [
                    {
                        "question_type": "multiple_choice",
                        "question_text": "What is the correct sequence of document lifecycle states?",
                        "options": [
                            {"id": "a", "text": "Draft > Approved > In Review > Effective > Obsolete", "is_correct": False},
                            {"id": "b", "text": "Draft > In Review > Approved > Effective > Obsolete", "is_correct": True},
                            {"id": "c", "text": "Draft > Effective > In Review > Approved > Obsolete", "is_correct": False},
                            {"id": "d", "text": "Draft > In Review > Effective > Approved > Obsolete", "is_correct": False},
                        ],
                        "correct_answer": "b",
                        "explanation": "The correct lifecycle is Draft > In Review > Approved > Effective > Obsolete. Documents must be reviewed before approval, and approved before becoming effective.",
                        "points": 2,
                    },
                    {
                        "question_type": "multiple_choice",
                        "question_text": "Which slash command inserts a table in the editor?",
                        "options": [
                            {"id": "a", "text": "/grid", "is_correct": False},
                            {"id": "b", "text": "/table", "is_correct": True},
                            {"id": "c", "text": "/spreadsheet", "is_correct": False},
                            {"id": "d", "text": "/columns", "is_correct": False},
                        ],
                        "correct_answer": "b",
                        "explanation": "The /table slash command inserts a table block with configurable rows and columns.",
                        "points": 2,
                    },
                    {
                        "question_type": "multiple_choice",
                        "question_text": "When a document is in 'Effective' status, how do you make changes to it?",
                        "options": [
                            {"id": "a", "text": "Click Edit to modify it directly", "is_correct": False},
                            {"id": "b", "text": "Change its status back to Draft first", "is_correct": False},
                            {"id": "c", "text": "Create a new change request which starts a new Draft revision", "is_correct": True},
                            {"id": "d", "text": "Ask an Admin to unlock it for editing", "is_correct": False},
                        ],
                        "correct_answer": "c",
                        "explanation": "Effective documents cannot be edited directly. Changes require creating a new change request, which creates a new Draft revision that goes through the full review and approval cycle.",
                        "points": 2,
                    },
                    {
                        "question_type": "true_false",
                        "question_text": "Documents can be directly edited while in 'Approved' status without creating a new revision.",
                        "options": None,
                        "correct_answer": "false",
                        "explanation": "Approved documents are locked. Content cannot be modified after approval signatures have been applied, as this would invalidate the electronic signatures and break compliance with 21 CFR Part 11.",
                        "points": 2,
                    },
                    {
                        "question_type": "fill_blank",
                        "question_text": "Type ___ at the start of a line to open the slash command menu in the editor.",
                        "options": None,
                        "correct_answer": "/",
                        "explanation": "The forward slash character (/) at the start of a line opens the slash command menu, which provides access to all block types and formatting options.",
                        "points": 2,
                    },
                ],
            },
        },
        {
            "title": "Approver/Reviewer Training",
            "slug": "training-approver-reviewer",
            "workspace_slug": "compliance",
            "space_slug": "training",
            "classification": "public",
            "summary": "Role-based training module for approvers and reviewers covering review responsibilities, electronic signatures, and approval workflows.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Approver/Reviewer Training"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Target Roles: "},
                            {"type": "text", "text": "Approvers and Reviewers | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Estimated Duration: "},
                            {"type": "text", "text": "1.5 hours"},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Learning Objectives"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "After completing this training, you will be able to:"}],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Understand your review responsibilities under ISO 9001 and ISO 13485"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Evaluate change requests using the diff view"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Apply electronic signatures correctly with proper meaning selection"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Understand the legal implications of your electronic signature"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Conduct periodic document reviews per schedule"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 1: Review Responsibilities"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Under ISO 9001:2015 Section 7.5.2, controlled documents must be reviewed and approved before release. As a reviewer, you verify technical accuracy, regulatory compliance, and completeness. As an approver, you authorize the document for release, confirming it meets organizational standards. Your review creates a quality gate — documents cannot proceed to Effective status without your explicit approval.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 2: Using the Diff View"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "When reviewing a change request, use the diff view to see exactly what has changed. The diff view shows additions in green and deletions in red. For new documents, the entire content is shown as additions. Review every change, not just the summary. Pay attention to: content accuracy, referenced standards and procedures, terminology consistency, and classification level appropriateness.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 3: Electronic Signatures"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Your electronic signature is legally binding under 21 CFR Part 11. When you sign, the system records your identity, a timestamp from a trusted NTP source, the meaning of your signature, and a SHA-256 hash of the content. The re-authentication step (entering your password again) ensures that your signature cannot be applied by someone else who has access to your session. Signature meanings are: Authored (you wrote it), Reviewed (you checked it), Approved (you authorize release), and Witnessed (you observed the process).",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 4: Approval Workflow"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "The approval workflow consists of these steps:"}],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "You receive a notification that a document is ready for your review."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Open the document and review all content, including the diff view for revisions."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Select your decision: Approve, Request Changes, or Reject."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "If approving, complete the electronic signature process with re-authentication."}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "If requesting changes, provide specific feedback explaining what needs to be revised."}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 5: Periodic Reviews"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Effective documents have periodic review dates. When a review date approaches, the document owner and designated reviewers receive notifications. During a periodic review, verify: the content still reflects current practice, referenced standards are still current, no regulatory changes affect the document, and contact information and role references are accurate. Record the outcome as No Changes Required, Minor Updates, or Major Revision Required.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Key Takeaways"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Your electronic signature is legally equivalent to a handwritten signature — take it seriously"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Always review the full content diff, not just the document summary"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Request changes with specific, actionable feedback rather than vague rejections"}]}]},
                        ],
                    },
                ],
            },
            "assessment": {
                "title": "Approver/Reviewer Competency Assessment",
                "description": "Verify understanding of review responsibilities and electronic signature procedures.",
                "passing_score": 80,
                "max_attempts": 3,
                "questions": [
                    {
                        "question_type": "multiple_choice",
                        "question_text": "Which signature meanings are available in the electronic signature system?",
                        "options": [
                            {"id": "a", "text": "Authored, Reviewed, Approved, Witnessed", "is_correct": True},
                            {"id": "b", "text": "Created, Checked, Released, Archived", "is_correct": False},
                            {"id": "c", "text": "Drafted, Verified, Certified, Published", "is_correct": False},
                            {"id": "d", "text": "Written, Inspected, Signed, Filed", "is_correct": False},
                        ],
                        "correct_answer": "a",
                        "explanation": "The four signature meanings defined in the platform are Authored, Reviewed, Approved, and Witnessed, aligned with 21 CFR Part 11 requirements.",
                        "points": 2,
                    },
                    {
                        "question_type": "multiple_choice",
                        "question_text": "What does 'non-repudiation' ensure in the context of electronic signatures?",
                        "options": [
                            {"id": "a", "text": "That the document cannot be deleted after signing", "is_correct": False},
                            {"id": "b", "text": "That the signer cannot deny having signed the document", "is_correct": True},
                            {"id": "c", "text": "That the signature is visible on the printed document", "is_correct": False},
                            {"id": "d", "text": "That the document is encrypted after signing", "is_correct": False},
                        ],
                        "correct_answer": "b",
                        "explanation": "Non-repudiation means the signer cannot deny having signed. The platform achieves this through re-authentication, content hashing, trusted timestamps, and audit trail recording.",
                        "points": 2,
                    },
                    {
                        "question_type": "multiple_choice",
                        "question_text": "Under ISO 9001, what is the reviewer's primary responsibility?",
                        "options": [
                            {"id": "a", "text": "Fixing grammatical errors in the document", "is_correct": False},
                            {"id": "b", "text": "Verifying technical accuracy, regulatory compliance, and completeness", "is_correct": True},
                            {"id": "c", "text": "Formatting the document according to templates", "is_correct": False},
                            {"id": "d", "text": "Publishing the document to the external site", "is_correct": False},
                        ],
                        "correct_answer": "b",
                        "explanation": "Under ISO 9001:2015 Section 7.5.2, reviewers verify that documents are technically accurate, comply with applicable regulations, and are complete before release.",
                        "points": 2,
                    },
                    {
                        "question_type": "true_false",
                        "question_text": "An electronic signature can be applied without re-entering your password if you have an active session.",
                        "options": None,
                        "correct_answer": "false",
                        "explanation": "Re-authentication is always required at signature time, even with an active session. This is a 21 CFR Part 11 requirement to verify the signer's identity at the moment of signing.",
                        "points": 2,
                    },
                    {
                        "question_type": "fill_blank",
                        "question_text": "The content hash algorithm used for electronic signature integrity verification is ___.",
                        "options": None,
                        "correct_answer": "SHA-256",
                        "explanation": "SHA-256 is used to compute a content hash at signing time. This hash is stored with the signature and can be recomputed later to verify that the content has not been modified.",
                        "points": 2,
                    },
                ],
            },
        },
        {
            "title": "Audit Trail Review Training",
            "slug": "training-audit-trail-review",
            "workspace_slug": "compliance",
            "space_slug": "training",
            "classification": "internal",
            "summary": "Role-based training module for auditors and QA staff covering audit trail structure, hash chain verification, anomaly detection, and compliance reporting.",
            "content": {
                "type": "doc",
                "content": [
                    {
                        "type": "heading",
                        "attrs": {"level": 1},
                        "content": [{"type": "text", "text": "Audit Trail Review Training"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Target Role: "},
                            {"type": "text", "text": "Auditors and Quality Assurance | "},
                            {"type": "text", "marks": [{"type": "bold"}], "text": "Estimated Duration: "},
                            {"type": "text", "text": "1.5 hours"},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Learning Objectives"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "After completing this training, you will be able to:"}],
                    },
                    {
                        "type": "orderedList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Explain the audit trail structure and what data each event captures"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Understand and verify the cryptographic hash chain"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Query and filter audit events effectively"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Identify common anomalies that may indicate compliance issues"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Export audit data for regulatory submissions"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 1: Audit Trail Structure"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Every significant action in the platform generates an audit event. Each event records: who (user ID and email), what (action type and details), when (server-side timestamp), where (IP address and resource identifier), and why (reason for change, if applicable). Events are stored in an append-only table — they cannot be modified or deleted through the application. This satisfies 21 CFR Part 11 Section 11.10(e) requirements for audit trails.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 2: Hash Chain Integrity"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "The audit trail uses a cryptographic hash chain for tamper detection. Each event includes a hash computed from the event's own data combined with the previous event's hash. This means any modification, deletion, or insertion of an event would break the chain at that point. The chain can be verified at any time: if the recomputed hash for each event matches the stored hash, the trail is intact. A break in the chain is a critical finding that requires immediate investigation.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 3: Querying Audit Events"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Navigate to Admin > Audit Trail to access the event browser. Filter events by: date range, user, action type (login, create, update, delete, approve, sign), resource type (page, workspace, user, assessment), and specific resource ID. Use the search bar for free-text search across event details. Results are displayed chronologically with newest events first. Click any event to see its full details including the hash chain values.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 4: Identifying Anomalies"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": "During routine reviews, watch for these indicators of potential issues:"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Multiple failed login attempts for the same account (potential unauthorized access attempt)"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Access or modifications outside normal working hours (unusual activity patterns)"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Permission changes not preceded by an access request workflow"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Document lifecycle transitions that skip expected states"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Service account activity volume spikes or unexpected resource access"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Signature verifications that fail (content modified after signing)"}]}]},
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 5: Export and Regulatory Reporting"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Audit data can be exported via Admin > Audit Trail > Export. Select CSV for spreadsheet analysis or JSON for programmatic processing. Exports include all event fields and hash chain values. For regulatory submissions, include the date range, a summary of findings, the chain verification result, and any deviations with their resolution. Store exports with restricted access and include them in your audit documentation package.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Module 6: Preparing for External Audits"}],
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Before an external audit, prepare by: running a full hash chain verification, exporting the relevant date range of audit events, documenting any anomalies found during routine reviews and their resolutions, verifying that all electronic signatures are intact, and confirming that retention policies are current. Present the audit trail as evidence of ongoing compliance with 21 CFR Part 11 Section 11.10(e) and ISO 9001:2015 Section 7.5.3.",
                            }
                        ],
                    },
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Key Takeaways"}],
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "The hash chain is your primary tool for proving audit trail integrity — verify it monthly"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "A broken hash chain is always a critical finding requiring immediate investigation"}]}]},
                            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Document your review findings even when nothing abnormal is found — this proves due diligence"}]}]},
                        ],
                    },
                ],
            },
            "assessment": {
                "title": "Audit Trail Review Competency Assessment",
                "description": "Verify understanding of audit trail review procedures and compliance verification.",
                "passing_score": 80,
                "max_attempts": 3,
                "questions": [
                    {
                        "question_type": "multiple_choice",
                        "question_text": "What is the primary purpose of the hash chain in the audit trail?",
                        "options": [
                            {"id": "a", "text": "To encrypt audit events so they cannot be read", "is_correct": False},
                            {"id": "b", "text": "To detect if any events have been tampered with, deleted, or inserted", "is_correct": True},
                            {"id": "c", "text": "To compress audit events for efficient storage", "is_correct": False},
                            {"id": "d", "text": "To link audit events to Git commits", "is_correct": False},
                        ],
                        "correct_answer": "b",
                        "explanation": "The hash chain provides tamper detection. Each event's hash depends on the previous event's hash, so any modification, deletion, or insertion breaks the chain at the tampered point.",
                        "points": 2,
                    },
                    {
                        "question_type": "multiple_choice",
                        "question_text": "Which of the following should you check during a routine audit trail review?",
                        "options": [
                            {"id": "a", "text": "Only failed login attempts", "is_correct": False},
                            {"id": "b", "text": "Only document lifecycle transitions", "is_correct": False},
                            {"id": "c", "text": "Hash chain integrity, access patterns, permission changes, and lifecycle transitions", "is_correct": True},
                            {"id": "d", "text": "Only events from the past 24 hours", "is_correct": False},
                        ],
                        "correct_answer": "c",
                        "explanation": "A comprehensive routine review covers hash chain integrity, access patterns (including after-hours activity), permission changes, lifecycle transitions, and service account activity.",
                        "points": 2,
                    },
                    {
                        "question_type": "multiple_choice",
                        "question_text": "How do you verify that the audit trail has not been tampered with?",
                        "options": [
                            {"id": "a", "text": "Count the total number of events and compare with expected count", "is_correct": False},
                            {"id": "b", "text": "Check that the database table has not been modified by examining PostgreSQL logs", "is_correct": False},
                            {"id": "c", "text": "Run the hash chain verification which recomputes and compares each event's hash", "is_correct": True},
                            {"id": "d", "text": "Export the data and manually review each event", "is_correct": False},
                        ],
                        "correct_answer": "c",
                        "explanation": "Hash chain verification recomputes the hash for each event using the previous event's hash as input. If all recomputed hashes match stored hashes, the chain is intact and no tampering has occurred.",
                        "points": 2,
                    },
                    {
                        "question_type": "true_false",
                        "question_text": "Audit trail events can be modified or deleted through the application after they are created.",
                        "options": None,
                        "correct_answer": "false",
                        "explanation": "Audit events are stored in an append-only table. The application does not provide any mechanism to modify or delete events, satisfying the immutability requirement of 21 CFR Part 11 Section 11.10(e).",
                        "points": 2,
                    },
                    {
                        "question_type": "fill_blank",
                        "question_text": "The regulatory standard that requires an immutable audit trail for electronic records is ___.",
                        "options": None,
                        "correct_answer": "21 CFR Part 11",
                        "explanation": "21 CFR Part 11, specifically Section 11.10(e), requires the use of secure, computer-generated, time-stamped audit trails to independently record the date and time of operator entries and actions.",
                        "points": 2,
                    },
                ],
            },
        },
    ],
}
