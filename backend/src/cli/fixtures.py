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
    ],
}
