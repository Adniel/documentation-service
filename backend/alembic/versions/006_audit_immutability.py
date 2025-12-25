"""Add audit trail immutability enforcement.

Revision ID: 006_audit_immutability
Revises: 005_electronic_signatures
Create Date: 2024-01-01 00:00:00.000000

Compliance:
- 21 CFR §11.10(e) - Audit trail immutability
- ISO 9001 §7.5.3 - Control of documented information

This migration adds database-level triggers to prevent modification
or deletion of audit events, ensuring regulatory compliance.
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006_audit_immutability'
down_revision = '005_electronic_signatures'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create function to prevent UPDATE on audit_events
    op.execute("""
        CREATE OR REPLACE FUNCTION prevent_audit_update()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'Audit events cannot be modified (21 CFR §11.10(e) compliance). Event ID: %', OLD.id;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger to prevent UPDATE
    op.execute("""
        CREATE TRIGGER audit_events_no_update
            BEFORE UPDATE ON audit_events
            FOR EACH ROW
            EXECUTE FUNCTION prevent_audit_update();
    """)

    # Create function to prevent DELETE on audit_events
    # Allows deletion only when app.audit_retention_mode is set to 'enabled'
    # This is for compliant archival/retention policy execution
    op.execute("""
        CREATE OR REPLACE FUNCTION prevent_audit_delete()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Only allow deletion by system retention process
            IF current_setting('app.audit_retention_mode', true) IS DISTINCT FROM 'enabled' THEN
                RAISE EXCEPTION 'Audit events cannot be deleted (21 CFR §11.10(e) compliance). Event ID: %. Set app.audit_retention_mode to enable compliant archival.', OLD.id;
            END IF;
            -- Log the deletion attempt (will be captured by application)
            RAISE NOTICE 'Audit retention: Deleting event % as part of retention policy', OLD.id;
            RETURN OLD;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger to prevent DELETE
    op.execute("""
        CREATE TRIGGER audit_events_no_delete
            BEFORE DELETE ON audit_events
            FOR EACH ROW
            EXECUTE FUNCTION prevent_audit_delete();
    """)

    # Create index on event_hash for chain verification performance
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_audit_events_event_hash
            ON audit_events (event_hash);
    """)

    # Create index on previous_hash for chain traversal
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_audit_events_previous_hash
            ON audit_events (previous_hash)
            WHERE previous_hash IS NOT NULL;
    """)

    # Add comment to table documenting compliance
    op.execute("""
        COMMENT ON TABLE audit_events IS
            '21 CFR Part 11 compliant audit trail. This table is protected by database triggers that prevent modification or deletion of records. All changes to electronic records are logged here with cryptographic hash chain for tamper detection.';
    """)


def downgrade() -> None:
    # Remove triggers
    op.execute("DROP TRIGGER IF EXISTS audit_events_no_update ON audit_events;")
    op.execute("DROP TRIGGER IF EXISTS audit_events_no_delete ON audit_events;")

    # Remove functions
    op.execute("DROP FUNCTION IF EXISTS prevent_audit_update();")
    op.execute("DROP FUNCTION IF EXISTS prevent_audit_delete();")

    # Remove indexes
    op.execute("DROP INDEX IF EXISTS ix_audit_events_event_hash;")
    op.execute("DROP INDEX IF EXISTS ix_audit_events_previous_hash;")

    # Remove comment
    op.execute("COMMENT ON TABLE audit_events IS NULL;")
