import axios from 'axios';
import { useAuthStore } from '../stores/authStore';
import type {
  User,
  Organization,
  Workspace,
  Space,
  Page,
  PageSummary,
  TokenResponse,
  RegisterRequest,
  VersionHistoryEntry,
  ChangeRequest,
  ChangeRequestListResponse,
  ChangeRequestCreate,
  ChangeRequestUpdate,
  ChangeRequestSubmit,
  ChangeRequestReview,
  ChangeRequestComment,
  CommentCreate,
  DiffResult,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = useAuthStore.getState().refreshToken;
      if (refreshToken) {
        try {
          const response = await axios.post<TokenResponse>(
            `${API_BASE_URL}/api/v1/auth/refresh`,
            { refresh_token: refreshToken }
          );

          const { access_token, refresh_token } = response.data;
          useAuthStore.getState().setTokens(access_token, refresh_token);

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch {
          useAuthStore.getState().logout();
        }
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (email: string, password: string): Promise<TokenResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post<TokenResponse>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<User> => {
    const response = await api.post<User>('/auth/register', data);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  changePassword: async (currentPassword: string, newPassword: string): Promise<void> => {
    await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },
};

// Organization API
export const organizationApi = {
  list: async (): Promise<Organization[]> => {
    const response = await api.get<Organization[]>('/organizations/');
    return response.data;
  },

  get: async (id: string): Promise<Organization> => {
    const response = await api.get<Organization>(`/organizations/${id}`);
    return response.data;
  },

  create: async (data: { name: string; slug: string; description?: string }): Promise<Organization> => {
    const response = await api.post<Organization>('/organizations/', data);
    return response.data;
  },

  update: async (id: string, data: Partial<Organization>): Promise<Organization> => {
    const response = await api.patch<Organization>(`/organizations/${id}`, data);
    return response.data;
  },
};

// Workspace API
export const workspaceApi = {
  listByOrg: async (orgId: string): Promise<Workspace[]> => {
    const response = await api.get<Workspace[]>(`/workspaces/org/${orgId}`);
    return response.data;
  },

  get: async (id: string): Promise<Workspace> => {
    const response = await api.get<Workspace>(`/workspaces/${id}`);
    return response.data;
  },

  create: async (data: {
    name: string;
    slug: string;
    organization_id: string;
    description?: string;
    is_public?: boolean;
  }): Promise<Workspace> => {
    const response = await api.post<Workspace>('/workspaces/', data);
    return response.data;
  },
};

// Space API
export const spaceApi = {
  listByWorkspace: async (workspaceId: string): Promise<Space[]> => {
    const response = await api.get<Space[]>(`/spaces/workspace/${workspaceId}`);
    return response.data;
  },

  get: async (id: string): Promise<Space> => {
    const response = await api.get<Space>(`/spaces/${id}`);
    return response.data;
  },

  create: async (data: {
    name: string;
    slug: string;
    workspace_id: string;
    description?: string;
    diataxis_type?: string;
  }): Promise<Space> => {
    const response = await api.post<Space>('/spaces/', data);
    return response.data;
  },
};

// Content (Pages) API
export const contentApi = {
  listBySpace: async (spaceId: string): Promise<PageSummary[]> => {
    const response = await api.get<PageSummary[]>(`/content/space/${spaceId}/pages`);
    return response.data;
  },

  get: async (id: string): Promise<Page> => {
    const response = await api.get<Page>(`/content/pages/${id}`);
    return response.data;
  },

  create: async (data: {
    title: string;
    slug: string;
    space_id: string;
    content?: Record<string, unknown>;
    summary?: string;
  }): Promise<Page> => {
    const response = await api.post<Page>('/content/pages', data);
    return response.data;
  },

  update: async (id: string, data: Partial<Page>): Promise<Page> => {
    const response = await api.patch<Page>(`/content/pages/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/content/pages/${id}`);
  },

  getHistory: async (id: string): Promise<VersionHistoryEntry[]> => {
    const response = await api.get<VersionHistoryEntry[]>(`/content/pages/${id}/history`);
    return response.data;
  },

  // Lifecycle management (Sprint 9.5)
  transitionStatus: async (
    id: string,
    toStatus: PageStatus,
    reason: string,
    effectiveDate?: string
  ): Promise<Page> => {
    const params: Record<string, string> = {
      to_status: toStatus,
      reason,
    };
    if (effectiveDate) {
      params.effective_date = effectiveDate;
    }
    const response = await api.post<Page>(`/content/pages/${id}/transition`, null, { params });
    return response.data;
  },

  getControlDashboard: async (): Promise<DocumentControlDashboard> => {
    const response = await api.get<DocumentControlDashboard>('/content/pages/control/dashboard');
    return response.data;
  },
};

// Document control dashboard type
export interface DocumentControlDashboard {
  total_documents: number;
  by_status: Record<string, number>;
  pending_reviews: number;
  effective_documents: number;
  draft_documents: number;
}

// Page status type
export type PageStatus = 'draft' | 'in_review' | 'approved' | 'effective' | 'obsolete' | 'archived';

// Change Request (Draft) API
export const changeRequestApi = {
  // Draft CRUD
  create: async (pageId: string, data: ChangeRequestCreate): Promise<ChangeRequest> => {
    const response = await api.post<ChangeRequest>(`/content/pages/${pageId}/drafts`, data);
    return response.data;
  },

  list: async (
    pageId: string,
    params?: { status?: string; limit?: number; offset?: number }
  ): Promise<ChangeRequestListResponse> => {
    const response = await api.get<ChangeRequestListResponse>(
      `/content/pages/${pageId}/drafts`,
      { params }
    );
    return response.data;
  },

  get: async (draftId: string): Promise<ChangeRequest> => {
    const response = await api.get<ChangeRequest>(`/content/drafts/${draftId}`);
    return response.data;
  },

  update: async (draftId: string, data: ChangeRequestUpdate): Promise<ChangeRequest> => {
    const response = await api.patch<ChangeRequest>(`/content/drafts/${draftId}`, data);
    return response.data;
  },

  cancel: async (draftId: string): Promise<void> => {
    await api.delete(`/content/drafts/${draftId}`);
  },

  // Workflow actions
  submit: async (draftId: string, data?: ChangeRequestSubmit): Promise<ChangeRequest> => {
    const response = await api.post<ChangeRequest>(
      `/content/drafts/${draftId}/submit`,
      data || {}
    );
    return response.data;
  },

  approve: async (draftId: string, data?: ChangeRequestReview): Promise<ChangeRequest> => {
    const response = await api.post<ChangeRequest>(
      `/content/drafts/${draftId}/approve`,
      data || {}
    );
    return response.data;
  },

  requestChanges: async (draftId: string, data: ChangeRequestReview): Promise<ChangeRequest> => {
    const response = await api.post<ChangeRequest>(
      `/content/drafts/${draftId}/request-changes`,
      data
    );
    return response.data;
  },

  reject: async (draftId: string, data?: ChangeRequestReview): Promise<ChangeRequest> => {
    const response = await api.post<ChangeRequest>(
      `/content/drafts/${draftId}/reject`,
      data || {}
    );
    return response.data;
  },

  publish: async (draftId: string): Promise<ChangeRequest> => {
    const response = await api.post<ChangeRequest>(`/content/drafts/${draftId}/publish`);
    return response.data;
  },

  // Diff
  getDiff: async (draftId: string): Promise<DiffResult> => {
    const response = await api.get<DiffResult>(`/content/drafts/${draftId}/diff`);
    return response.data;
  },

  getPageDiff: async (pageId: string, fromSha: string, toSha: string): Promise<DiffResult> => {
    const response = await api.get<DiffResult>(`/content/pages/${pageId}/diff`, {
      params: { from_sha: fromSha, to_sha: toSha },
    });
    return response.data;
  },

  // Comments
  createComment: async (draftId: string, data: CommentCreate): Promise<ChangeRequestComment> => {
    const response = await api.post<ChangeRequestComment>(
      `/content/drafts/${draftId}/comments`,
      data
    );
    return response.data;
  },

  listComments: async (draftId: string): Promise<ChangeRequestComment[]> => {
    const response = await api.get<ChangeRequestComment[]>(
      `/content/drafts/${draftId}/comments`
    );
    return response.data;
  },
};

// Search API
export interface SearchResult {
  hits: Array<{
    id: string;
    title: string;
    summary?: string;
    status: string;
    version: string;
    document_number?: string;
    space_id: string;
    diataxis_type?: string;
    updated_at: string;
    _formatted?: {
      title?: string;
      content_text?: string;
      summary?: string;
    };
  }>;
  total: number;
  processing_time_ms: number;
  query: string;
  limit: number;
  offset: number;
}

export interface SearchSuggestion {
  type: 'page' | 'space';
  id: string;
  title: string;
  description?: string;
}

export const searchApi = {
  searchPages: async (params: {
    q: string;
    space_id?: string;
    workspace_id?: string;
    organization_id?: string;
    status?: string;
    diataxis_type?: string;
    limit?: number;
    offset?: number;
    sort?: string;
  }): Promise<SearchResult> => {
    const response = await api.get<SearchResult>('/search/pages', { params });
    return response.data;
  },

  searchSpaces: async (params: {
    q: string;
    workspace_id?: string;
    organization_id?: string;
    diataxis_type?: string;
    limit?: number;
  }): Promise<{ hits: Space[]; total: number }> => {
    const response = await api.get('/search/spaces', { params });
    return response.data;
  },

  getSuggestions: async (q: string, limit = 5): Promise<SearchSuggestion[]> => {
    const response = await api.get<SearchSuggestion[]>('/search/suggestions', {
      params: { q, limit },
    });
    return response.data;
  },
};

// Navigation API
export interface NavigationTreeNode {
  id: string;
  name: string;
  slug: string;
  type: 'workspace' | 'space' | 'page';
  diataxis_type?: string;
  classification?: number;
  children?: NavigationTreeNode[];
  pages?: Array<{
    id: string;
    title: string;
    slug: string;
    status: string;
    version: string;
    document_number?: string;
  }>;
}

export interface WorkspaceTree extends NavigationTreeNode {
  type: 'workspace';
  organization: {
    id: string;
    name: string;
    slug: string;
  };
}

export interface Breadcrumb {
  type: 'organization' | 'workspace' | 'space' | 'page';
  id: string;
  name: string;
  slug: string;
}

export const navigationApi = {
  getWorkspaceTree: async (
    workspaceId: string,
    includePages = true,
    maxDepth = 3
  ): Promise<WorkspaceTree> => {
    const response = await api.get<WorkspaceTree>(`/nav/tree/workspace/${workspaceId}`, {
      params: { include_pages: includePages, max_depth: maxDepth },
    });
    return response.data;
  },

  getSpaceTree: async (
    spaceId: string,
    includeChildren = true
  ): Promise<NavigationTreeNode> => {
    const response = await api.get<NavigationTreeNode>(`/nav/tree/space/${spaceId}`, {
      params: { include_children: includeChildren },
    });
    return response.data;
  },

  getPageBreadcrumbs: async (pageId: string): Promise<Breadcrumb[]> => {
    const response = await api.get<Breadcrumb[]>(`/nav/breadcrumbs/page/${pageId}`);
    return response.data;
  },

  getSpaceBreadcrumbs: async (spaceId: string): Promise<Breadcrumb[]> => {
    const response = await api.get<Breadcrumb[]>(`/nav/breadcrumbs/space/${spaceId}`);
    return response.data;
  },

  getRecentPages: async (limit = 10, workspaceId?: string): Promise<PageSummary[]> => {
    const response = await api.get<PageSummary[]>('/nav/recent', {
      params: { limit, workspace_id: workspaceId },
    });
    return response.data;
  },
};

// Electronic Signatures API (21 CFR Part 11)
export type SignatureMeaning = 'authored' | 'reviewed' | 'approved' | 'witnessed' | 'acknowledged';

export interface InitiateSignatureRequest {
  page_id?: string;
  change_request_id?: string;
  meaning: SignatureMeaning;
  reason?: string;
}

export interface InitiateSignatureResponse {
  challenge_token: string;
  expires_at: string;
  expires_in_seconds: number;
  content_preview: string;
  content_hash: string;
  meaning: SignatureMeaning;
  meaning_description: string;
  document_title?: string;
}

export interface CompleteSignatureRequest {
  challenge_token: string;
  password: string;
  reason?: string;
}

export interface ElectronicSignature {
  id: string;
  page_id?: string;
  change_request_id?: string;
  signer_id: string;
  signer_name: string;
  signer_email: string;
  signer_title?: string;
  meaning: SignatureMeaning;
  meaning_description: string;
  reason?: string;
  content_hash: string;
  git_commit_sha?: string;
  signed_at: string;
  ntp_server: string;
  is_valid: boolean;
  invalidated_at?: string;
  invalidation_reason?: string;
  created_at: string;
}

export interface SignatureVerification {
  signature_id: string;
  is_valid: boolean;
  signer_name: string;
  signer_email: string;
  meaning: SignatureMeaning;
  meaning_description: string;
  signed_at: string;
  ntp_server: string;
  content_hash_matches: boolean;
  git_commit_verified: boolean;
  verification_timestamp: string;
  issues: string[];
}

export interface SignatureListResponse {
  signatures: ElectronicSignature[];
  total: number;
  has_valid_signatures: boolean;
}

// Learning Module API (Sprint 9)
export type QuestionType = 'multiple_choice' | 'true_false' | 'fill_blank';
export type AssignmentStatus = 'assigned' | 'in_progress' | 'completed' | 'overdue' | 'cancelled';
export type AttemptStatus = 'in_progress' | 'submitted' | 'passed' | 'failed' | 'abandoned';

export interface QuestionOption {
  id: string;
  text: string;
  is_correct?: boolean;
}

export interface QuestionPublic {
  id: string;
  question_type: QuestionType;
  question_text: string;
  options?: { id: string; text: string }[];
  points: number;
  sort_order: number;
}

export interface AssessmentPublic {
  id: string;
  title: string;
  description?: string;
  passing_score: number;
  max_attempts?: number;
  time_limit_minutes?: number;
  question_count: number;
  total_points: number;
  questions: QuestionPublic[];
}

export interface Assessment {
  id: string;
  page_id: string;
  title: string;
  description?: string;
  passing_score: number;
  max_attempts?: number;
  time_limit_minutes?: number;
  is_active: boolean;
  created_by_id: string;
  created_at: string;
  updated_at: string;
}

export interface AssessmentQuestion {
  id: string;
  assessment_id: string;
  question_type: QuestionType;
  question_text: string;
  options?: QuestionOption[];
  correct_answer?: string;
  points: number;
  explanation?: string;
  sort_order: number;
}

export interface LearningAssignment {
  id: string;
  page_id: string;
  user_id: string;
  assigned_by_id: string;
  status: AssignmentStatus;
  due_date?: string;
  assigned_at: string;
  started_at?: string;
  completed_at?: string;
  page?: { id: string; title: string };
  user?: { id: string; email: string; full_name?: string };
}

export interface QuizAttempt {
  id: string;
  assessment_id: string;
  user_id: string;
  assignment_id?: string;
  status: AttemptStatus;
  score?: number;
  earned_points?: number;
  total_points?: number;
  passing_score?: number;
  attempt_number: number;
  started_at: string;
  submitted_at?: string;
  time_spent_seconds?: number;
  answers?: Record<string, string>;
}

export interface GradeResult {
  score: number;
  passed: boolean;
  earned_points: number;
  total_points: number;
  passing_score: number;
  question_results: Array<{
    question_id: string;
    question_type: string;
    user_answer?: string;
    is_correct: boolean;
    points_earned: number;
    points_possible: number;
    correct_answer?: string;
    explanation?: string;
  }>;
}

export interface AcknowledgmentStatus {
  page_id: string;
  has_valid_acknowledgment: boolean;
  acknowledgment?: TrainingAcknowledgment;
  requires_training: boolean;
  has_assessment: boolean;
  has_passed_quiz: boolean;
  can_acknowledge: boolean;
  reason?: string;
}

export interface TrainingAcknowledgment {
  id: string;
  page_id: string;
  user_id: string;
  signature_id: string;
  acknowledged_at: string;
  valid_until?: string;
  is_valid: boolean;
  page_version: string;
}

export interface InitiateAcknowledgmentResponse {
  challenge_token: string;
  expires_at: string;
  content_hash: string;
  document_title?: string;
  requires_quiz: boolean;
  quiz_passed?: boolean;
}

// Reporting types
export interface CompletionReportItem {
  page_id: string;
  page_title: string;
  total_assigned: number;
  completed: number;
  in_progress: number;
  overdue: number;
  completion_rate: number;
}

export interface OverdueReport {
  total_overdue: number;
  assignments: LearningAssignment[];
}

export interface UserTrainingHistory {
  user_id: string;
  user_email: string;
  user_name: string;
  total_assignments: number;
  completed: number;
  in_progress: number;
  overdue: number;
  acknowledgments: TrainingAcknowledgment[];
}

export interface PageTrainingReport {
  page_id: string;
  page_title: string;
  requires_training: boolean;
  has_assessment: boolean;
  assessment_id?: string;
  total_assigned: number;
  completed: number;
  completion_rate: number;
  assignments: LearningAssignment[];
}

export interface ReportExportRequest {
  report_type: 'completion' | 'overdue' | 'user' | 'page';
  format?: 'json' | 'csv';
  page_id?: string;
  user_id?: string;
  start_date?: string;
  end_date?: string;
}

export interface ReportExportResponse {
  report_type: string;
  generated_at: string;
  data: unknown[];
}

export const learningApi = {
  // Assessments
  listAssessments: async (params?: {
    page_id?: string;
    is_active?: boolean;
    limit?: number;
    offset?: number;
  }): Promise<Assessment[]> => {
    const response = await api.get<Assessment[]>('/learning/assessments', { params });
    return response.data;
  },

  createAssessment: async (data: {
    page_id: string;
    title: string;
    description?: string;
    passing_score?: number;
    max_attempts?: number;
    time_limit_minutes?: number;
  }): Promise<Assessment> => {
    const response = await api.post<Assessment>('/learning/assessments', data);
    return response.data;
  },

  getAssessment: async (assessmentId: string): Promise<Assessment & { questions: AssessmentQuestion[] }> => {
    const response = await api.get(`/learning/assessments/${assessmentId}`);
    return response.data;
  },

  getAssessmentForPage: async (pageId: string): Promise<Assessment & { questions: AssessmentQuestion[] }> => {
    const response = await api.get(`/learning/pages/${pageId}/assessment`);
    return response.data;
  },

  updateAssessment: async (
    assessmentId: string,
    data: Partial<Assessment>
  ): Promise<Assessment> => {
    const response = await api.patch<Assessment>(`/learning/assessments/${assessmentId}`, data);
    return response.data;
  },

  deleteAssessment: async (assessmentId: string): Promise<void> => {
    await api.delete(`/learning/assessments/${assessmentId}`);
  },

  // Questions
  addQuestion: async (
    assessmentId: string,
    data: {
      question_type: QuestionType;
      question_text: string;
      options?: QuestionOption[];
      correct_answer?: string;
      points?: number;
      explanation?: string;
    }
  ): Promise<AssessmentQuestion> => {
    const response = await api.post<AssessmentQuestion>(
      `/learning/assessments/${assessmentId}/questions`,
      data
    );
    return response.data;
  },

  updateQuestion: async (
    questionId: string,
    data: Partial<AssessmentQuestion>
  ): Promise<AssessmentQuestion> => {
    const response = await api.patch<AssessmentQuestion>(
      `/learning/questions/${questionId}`,
      data
    );
    return response.data;
  },

  deleteQuestion: async (questionId: string): Promise<void> => {
    await api.delete(`/learning/questions/${questionId}`);
  },

  reorderQuestions: async (
    assessmentId: string,
    questionIds: string[]
  ): Promise<AssessmentQuestion[]> => {
    const response = await api.put<AssessmentQuestion[]>(
      `/learning/assessments/${assessmentId}/questions/order`,
      questionIds
    );
    return response.data;
  },

  // Assignments
  createAssignment: async (data: {
    page_id: string;
    user_id: string;
    due_date?: string;
    notes?: string;
  }): Promise<LearningAssignment> => {
    const response = await api.post<LearningAssignment>('/learning/assignments', data);
    return response.data;
  },

  createBulkAssignments: async (data: {
    page_id: string;
    user_ids: string[];
    due_date?: string;
    notes?: string;
  }): Promise<LearningAssignment[]> => {
    const response = await api.post<LearningAssignment[]>('/learning/assignments/bulk', data);
    return response.data;
  },

  listAssignments: async (params?: {
    user_id?: string;
    page_id?: string;
    status?: AssignmentStatus;
    limit?: number;
    offset?: number;
  }): Promise<{ assignments: LearningAssignment[]; total: number }> => {
    const response = await api.get('/learning/assignments', { params });
    return response.data;
  },

  getAssignment: async (assignmentId: string): Promise<LearningAssignment> => {
    const response = await api.get<LearningAssignment>(`/learning/assignments/${assignmentId}`);
    return response.data;
  },

  getMyAssignments: async (includeCompleted = false): Promise<LearningAssignment[]> => {
    const response = await api.get<LearningAssignment[]>('/learning/assignments/me', {
      params: { include_completed: includeCompleted },
    });
    return response.data;
  },

  cancelAssignment: async (assignmentId: string): Promise<void> => {
    await api.delete(`/learning/assignments/${assignmentId}`);
  },

  // Quiz Taking
  getQuiz: async (pageId: string): Promise<AssessmentPublic> => {
    const response = await api.get<AssessmentPublic>(`/learning/pages/${pageId}/quiz`);
    return response.data;
  },

  startAttempt: async (
    assessmentId: string,
    assignmentId?: string
  ): Promise<QuizAttempt> => {
    const response = await api.post<QuizAttempt>(`/learning/assessments/${assessmentId}/start`, {
      assignment_id: assignmentId,
    });
    return response.data;
  },

  getAttempt: async (attemptId: string): Promise<QuizAttempt> => {
    const response = await api.get<QuizAttempt>(`/learning/attempts/${attemptId}`);
    return response.data;
  },

  saveAnswer: async (
    attemptId: string,
    questionId: string,
    answer: string
  ): Promise<QuizAttempt> => {
    const response = await api.patch<QuizAttempt>(`/learning/attempts/${attemptId}/answer`, {
      question_id: questionId,
      answer,
    });
    return response.data;
  },

  submitAttempt: async (attemptId: string): Promise<QuizAttempt & { grade_result: GradeResult }> => {
    const response = await api.post(`/learning/attempts/${attemptId}/submit`);
    return response.data;
  },

  getAttemptResults: async (attemptId: string): Promise<GradeResult> => {
    const response = await api.get<GradeResult>(`/learning/attempts/${attemptId}/results`);
    return response.data;
  },

  getMyAttempts: async (assessmentId?: string): Promise<QuizAttempt[]> => {
    const response = await api.get<QuizAttempt[]>('/learning/attempts/me', {
      params: { assessment_id: assessmentId },
    });
    return response.data;
  },

  // Acknowledgments
  getAcknowledgmentStatus: async (pageId: string): Promise<AcknowledgmentStatus> => {
    const response = await api.get<AcknowledgmentStatus>(
      `/learning/pages/${pageId}/acknowledgment`
    );
    return response.data;
  },

  initiateAcknowledgment: async (
    pageId: string,
    quizAttemptId?: string
  ): Promise<InitiateAcknowledgmentResponse> => {
    const response = await api.post<InitiateAcknowledgmentResponse>(
      `/learning/pages/${pageId}/acknowledge`,
      { quiz_attempt_id: quizAttemptId }
    );
    return response.data;
  },

  completeAcknowledgment: async (
    challengeToken: string,
    password: string
  ): Promise<TrainingAcknowledgment> => {
    const response = await api.post<TrainingAcknowledgment>(
      '/learning/acknowledgments/complete',
      { challenge_token: challengeToken, password }
    );
    return response.data;
  },

  getMyAcknowledgments: async (validOnly = false): Promise<TrainingAcknowledgment[]> => {
    const response = await api.get<TrainingAcknowledgment[]>('/learning/acknowledgments/me', {
      params: { valid_only: validOnly },
    });
    return response.data;
  },

  // Reporting
  getCompletionReport: async (pageId?: string): Promise<CompletionReportItem[]> => {
    const response = await api.get<CompletionReportItem[]>('/learning/reports/completion', {
      params: pageId ? { page_id: pageId } : undefined,
    });
    return response.data;
  },

  getOverdueReport: async (): Promise<OverdueReport> => {
    const response = await api.get<OverdueReport>('/learning/reports/overdue');
    return response.data;
  },

  getUserTrainingHistory: async (userId: string): Promise<UserTrainingHistory> => {
    const response = await api.get<UserTrainingHistory>(`/learning/reports/user/${userId}`);
    return response.data;
  },

  getPageTrainingReport: async (pageId: string): Promise<PageTrainingReport> => {
    const response = await api.get<PageTrainingReport>(`/learning/reports/page/${pageId}`);
    return response.data;
  },

  exportReport: async (request: ReportExportRequest): Promise<ReportExportResponse | Blob> => {
    if (request.format === 'csv') {
      const response = await api.post('/learning/reports/export', request, {
        responseType: 'blob',
      });
      return response.data;
    }
    const response = await api.post<ReportExportResponse>('/learning/reports/export', request);
    return response.data;
  },
};

export const signatureApi = {
  // Initiate signature flow
  initiate: async (data: InitiateSignatureRequest): Promise<InitiateSignatureResponse> => {
    const response = await api.post<InitiateSignatureResponse>('/signatures/initiate', data);
    return response.data;
  },

  // Complete signature with re-authentication
  complete: async (data: CompleteSignatureRequest): Promise<ElectronicSignature> => {
    const response = await api.post<ElectronicSignature>('/signatures/complete', data);
    return response.data;
  },

  // Get signature by ID
  get: async (signatureId: string): Promise<ElectronicSignature> => {
    const response = await api.get<ElectronicSignature>(`/signatures/${signatureId}`);
    return response.data;
  },

  // Verify signature integrity
  verify: async (signatureId: string, verifyContent = true): Promise<SignatureVerification> => {
    const response = await api.get<SignatureVerification>(
      `/signatures/${signatureId}/verify`,
      { params: { verify_content: verifyContent } }
    );
    return response.data;
  },

  // Invalidate a signature
  invalidate: async (signatureId: string, reason: string): Promise<ElectronicSignature> => {
    const response = await api.post<ElectronicSignature>(
      `/signatures/${signatureId}/invalidate`,
      { reason }
    );
    return response.data;
  },

  // List signatures for a page
  listForPage: async (
    pageId: string,
    includeInvalid = false
  ): Promise<SignatureListResponse> => {
    const response = await api.get<SignatureListResponse>(
      `/pages/${pageId}/signatures`,
      { params: { include_invalid: includeInvalid } }
    );
    return response.data;
  },

  // List signatures for a change request
  listForChangeRequest: async (
    changeRequestId: string,
    includeInvalid = false
  ): Promise<SignatureListResponse> => {
    const response = await api.get<SignatureListResponse>(
      `/change-requests/${changeRequestId}/signatures`,
      { params: { include_invalid: includeInvalid } }
    );
    return response.data;
  },
};

export default api;
