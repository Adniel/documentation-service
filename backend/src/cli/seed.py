"""Database seeding logic."""

import sys

from sqlalchemy import delete, select

from src.db.models import Organization, User
from src.db.models.organization import organization_members
from src.db.session import async_session_maker
from src.modules.access.security import hash_password
from src.modules.content.git_service import get_git_service
from src.modules.content.schemas import (
    ClassificationLevel,
    DiataxisType,
    OrganizationCreate,
    PageCreate,
    SpaceCreate,
    WorkspaceCreate,
)
from src.modules.content.service import (
    create_organization,
    create_page,
    create_space,
    create_workspace,
    get_organization_by_slug,
)


async def seed_database(fixture: str = "demo", force: bool = False) -> None:
    """Seed the database with sample data."""
    if fixture == "demo":
        from src.cli.fixtures import DEMO_FIXTURE as data
    else:
        from src.cli.fixtures import MINIMAL_FIXTURE as data

    async with async_session_maker() as db:
        # Check if org already exists
        existing = await get_organization_by_slug(db, data["organization"]["slug"])
        if existing and not force:
            print(f"Organization '{data['organization']['slug']}' already exists. Use --force to overwrite.")
            sys.exit(1)

        if existing and force:
            print("Force mode: cleaning existing data...")
            # Delete org members, then org (cascade handles workspaces/spaces/pages)
            await db.execute(
                delete(organization_members).where(
                    organization_members.c.organization_id == existing.id
                )
            )
            await db.delete(existing)
            await db.commit()
            print("  Existing organization removed.")

        # Create users
        print("Creating users...")
        users = {}
        for user_data in data["users"]:
            # Check if user already exists
            result = await db.execute(
                select(User).where(User.email == user_data["email"])
            )
            user = result.scalar_one_or_none()
            if user is None:
                user = User(
                    email=user_data["email"],
                    hashed_password=hash_password(user_data["password"]),
                    full_name=user_data["full_name"],
                    is_superuser=user_data.get("is_superuser", False),
                    clearance_level=user_data.get("clearance_level", 0),
                    is_active=True,
                    email_verified=True,
                )
                db.add(user)
                await db.flush()
                print(f"  Created user: {user.email}")
            else:
                print(f"  User already exists: {user.email}")
            users[user_data["email"]] = user

        # Create organization (first user is owner)
        print("Creating organization...")
        owner = users[data["users"][0]["email"]]
        org = await create_organization(
            db,
            OrganizationCreate(**data["organization"]),
            owner,
        )
        print(f"  Created org: {org.name} ({org.slug})")

        # Add additional users as org members
        for user_data in data["users"][1:]:
            user = users[user_data["email"]]
            role = "editor" if user_data.get("clearance_level", 0) >= 1 else "viewer"
            await db.execute(
                organization_members.insert().values(
                    organization_id=org.id,
                    user_id=user.id,
                    role=role,
                )
            )
            print(f"  Added member: {user.email} as {role}")

        # Initialize Git repo
        print("Initializing Git repository...")
        git_service = get_git_service()
        git_service.init_repo(org.slug)
        print(f"  Git repo initialized at: {org.slug}")

        # Create workspaces, spaces, pages
        workspace_map = {}  # slug -> Workspace
        space_map = {}  # (ws_slug, space_slug) -> Space

        print("Creating workspaces and spaces...")
        for ws_data in data["workspaces"]:
            workspace = await create_workspace(
                db,
                WorkspaceCreate(
                    name=ws_data["name"],
                    slug=ws_data["slug"],
                    description=ws_data.get("description"),
                    organization_id=org.id,
                ),
            )
            workspace_map[ws_data["slug"]] = workspace
            print(f"  Created workspace: {ws_data['name']}")

            for sp_data in ws_data["spaces"]:
                space = await create_space(
                    db,
                    SpaceCreate(
                        name=sp_data["name"],
                        slug=sp_data["slug"],
                        description=sp_data.get("description"),
                        workspace_id=workspace.id,
                        diataxis_type=DiataxisType(sp_data["diataxis_type"]),
                        classification=ClassificationLevel(sp_data.get("classification", "public")),
                    ),
                )
                space_map[(ws_data["slug"], sp_data["slug"])] = space
                print(f"    Created space: {sp_data['name']}")

        # Create pages
        page_count = 0
        print("Creating pages...")
        for page_data in data.get("pages", []):
            ws_slug = page_data["workspace_slug"]
            sp_slug = page_data["space_slug"]
            space = space_map.get((ws_slug, sp_slug))
            if not space:
                print(f"  Warning: space not found for {ws_slug}/{sp_slug}, skipping page")
                continue

            page = await create_page(
                db,
                PageCreate(
                    title=page_data["title"],
                    slug=page_data["slug"],
                    space_id=space.id,
                    content=page_data.get("content"),
                    summary=page_data.get("summary"),
                    classification=ClassificationLevel(page_data.get("classification", "public")),
                ),
                author_id=owner.id,
            )

            # Also commit content to Git
            if page_data.get("content"):
                git_service.create_file(
                    org_slug=org.slug,
                    workspace_slug=ws_slug,
                    space_slug=sp_slug,
                    page_slug=page_data["slug"],
                    content=page_data["content"],
                    author_name=owner.full_name,
                    author_email=owner.email,
                    message=f"Seed: create {page_data['title']}",
                )

            page_count += 1
            print(f"  Created page: {page_data['title']}")

        await db.commit()

        print()
        print("=" * 50)
        print(f"Seed complete ({fixture} fixture)")
        print(f"  Users:      {len(data['users'])}")
        print(f"  Workspaces: {len(data['workspaces'])}")
        spaces_count = sum(len(ws.get("spaces", [])) for ws in data["workspaces"])
        print(f"  Spaces:     {spaces_count}")
        print(f"  Pages:      {page_count}")
        print("=" * 50)
