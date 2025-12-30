// User types
export interface User {
  id: string;
  email: string;
  full_name: string;
  title: string | null;
  is_active: boolean;
  email_verified: boolean;
  clearance_level: number;
  avatar_url: string | null;
  created_at: string;
  updated_at: string;
}

// Organization types
export interface Organization {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  is_active: boolean;
  logo_url: string | null;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

// Workspace types
export interface Workspace {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  organization_id: string;
  is_active: boolean;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

// Space types
export type DiataxisType = 'tutorial' | 'how_to' | 'reference' | 'explanation' | 'mixed';

export interface Space {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  workspace_id: string;
  parent_id: string | null;
  diataxis_type: DiataxisType;
  classification: number;
  sort_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Page types
export type PageStatus = 'draft' | 'in_review' | 'approved' | 'effective' | 'obsolete' | 'archived';

export interface Page {
  id: string;
  title: string;
  slug: string;
  space_id: string;
  author_id: string;
  parent_id: string | null;
  document_number: string | null;
  version: string;
  status: PageStatus;
  classification: number;
  content: Record<string, unknown> | null;
  summary: string | null;
  git_path: string | null;
  git_commit_sha: string | null;
  is_active: boolean;
  is_template: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface PageSummary {
  id: string;
  title: string;
  slug: string;
  status: PageStatus;
  version: string;
  space_id: string;
  document_number?: string;
  summary?: string;
  updated_at: string;
}

// Auth types
export interface LoginRequest {
  username: string; // email
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegisterRequest {
  email: string;
  full_name: string;
  password: string;
  title?: string;
}

// Version history
export interface VersionHistoryEntry {
  sha: string;
  message: string;
  author_name: string;
  author_email: string;
  timestamp: string;
}

// Change Request (Draft) types
export type ChangeRequestStatus =
  | 'draft'
  | 'submitted'
  | 'in_review'
  | 'changes_requested'
  | 'approved'
  | 'published'
  | 'rejected'
  | 'cancelled';

export interface ChangeRequest {
  id: string;
  page_id: string;
  title: string;
  description: string | null;
  number: number;
  status: ChangeRequestStatus;
  branch_name: string;
  base_commit_sha: string;
  head_commit_sha: string | null;
  author_id: string;
  author_name: string | null;
  author_email: string | null;
  submitted_at: string | null;
  reviewer_id: string | null;
  reviewer_name: string | null;
  reviewed_at: string | null;
  review_comment: string | null;
  published_at: string | null;
  published_by_id: string | null;
  merge_commit_sha: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChangeRequestListResponse {
  items: ChangeRequest[];
  total: number;
}

export interface ChangeRequestCreate {
  title: string;
  description?: string;
}

export interface ChangeRequestUpdate {
  title?: string;
  description?: string;
}

export interface ChangeRequestSubmit {
  reviewer_id?: string;
  approval_matrix_id?: string;
  comment?: string;
}

export interface ChangeRequestReview {
  comment?: string;
}

export interface ChangeRequestComment {
  id: string;
  change_request_id: string;
  author_id: string;
  author_name: string | null;
  content: string;
  file_path: string | null;
  line_number: number | null;
  parent_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface CommentCreate {
  content: string;
  file_path?: string;
  line_number?: number;
  parent_id?: string;
}

// Diff types
export interface DiffHunk {
  old_start: number;
  old_lines: number;
  new_start: number;
  new_lines: number;
  content: string;
}

export interface DiffResult {
  from_sha: string;
  to_sha: string;
  hunks: DiffHunk[];
  additions: number;
  deletions: number;
  is_binary: boolean;
}

// Organization member types (Sprint B)
export type MemberRole = 'viewer' | 'reviewer' | 'editor' | 'admin' | 'owner';

export interface OrganizationMember {
  user_id: string;
  organization_id: string;
  role: MemberRole;
  user_email: string;
  user_full_name: string;
  user_avatar_url: string | null;
  is_active: boolean;
  joined_at: string | null;
}

export interface OrganizationMemberListResponse {
  members: OrganizationMember[];
  total: number;
}

export interface InviteMemberRequest {
  email: string;
  role: MemberRole;
}

export interface UpdateMemberRoleRequest {
  role: MemberRole;
}

// Organization settings types (Sprint B)
export interface OrganizationSettingsUpdate {
  name?: string;
  description?: string;
  logo_url?: string;
  doc_numbering_enabled?: boolean;
  default_classification?: number;
}

// Audit event types (Sprint B)
export interface AuditEvent {
  id: string;
  event_type: string;
  timestamp: string;
  actor_id: string | null;
  actor_email: string | null;
  actor_ip: string | null;
  resource_type: string | null;
  resource_id: string | null;
  resource_name: string | null;
  details: Record<string, unknown> | null;
  event_hash: string;
  previous_hash: string | null;
}

export interface AuditEventListResponse {
  events: AuditEvent[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface AuditQueryParams {
  event_type?: string;
  actor_id?: string;
  resource_type?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
  offset?: number;
}

export interface AuditExportParams {
  format: 'csv' | 'json';
  start_date: string;
  end_date: string;
  event_types?: string[];
  include_details?: boolean;
}

export interface AuditStats {
  total_events: number;
  events_by_type: Record<string, number>;
  events_today: number;
  events_this_week: number;
  unique_actors: number;
  chain_head_hash: string | null;
  oldest_event: string | null;
  newest_event: string | null;
}

export interface ChainVerificationResponse {
  is_valid: boolean;
  total_events: number;
  verified_events: number;
  first_invalid_event_id: string | null;
  first_invalid_reason: string | null;
  verification_timestamp: string;
  chain_head_hash: string | null;
  verification_duration_ms: number;
}
