/** Тело ошибки от бэка (подстройте под контракт API). */
export interface ApiErrorBody {
	message?: string;
	code?: string;
	errors?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
	items: T[];
	total: number;
	page: number;
	pageSize: number;
}

export interface AuthResponse {
	token: string;
}

export interface AuthRequest {
	tmaToken: string;
	refId?: string;
}

/** POST /v1/auth/authenticate (OAuth2 password, form body). */
export interface V1AuthenticateRequest {
	username: string;
	password: string;
}

export interface V1AuthenticateResponse {
	access_token: string;
	token_type: string;
}

/** POST /v1/cabinet/document/file (multipart). */
export interface V1CabinetDocumentFilePostResponse200 {
	document_id: number;
	file_id: number;
	pdf_file_id: number;
}

/** GET /v1/cabinet/me */
export interface V1CabinetMeGetResponse {
	user_id: number;
	fio: string;
	login: string;
	organization: string;
}

/** GET /v1/cabinet/stages */
export interface StageSummaryGetResponse {
	stage_id: number;
	next_stage: number;
	title: string;
}

export interface StageReviewerUserGetResponse {
	user_id: string;
	fio: string;
}

export type DocumentUserStatus =
	| 'new_comment'
	| 'not_viewed'
	| 'viewed'
	| 'waiting'
	| 'action_required'
	| 'sent'
	| 'edits_required';

/** GET /v1/cabinet/stages query params (для модалки фильтров). */
export type CabinetStageRoleFilter = 'author' | 'coauthor' | 'reviewer';
export type CabinetDocStatusFilter = 'new_comment' | 'not_viewed' | 'viewed' | 'waiting' | 'action_required' | 'sent';
export type CabinetStagesStageIndex = 0 | 1 | 2 | 3;

export interface V1StagesListQueryParams {
	roles?: Array<'author' | 'reviewer'> | null;
	review_statuses?: Array<'accepted' | 'declined'> | null;
	categories?: string[] | null;
	doc_statuses?: CabinetDocStatusFilter[] | null;
}

/** Состав фильтров, который хранит UI. */
export interface CabinetStagesFilters {
	/** UI-роль (Автор/Соавтор/Эксперт). В запрос это преобразуем в `roles`. */
	myRole: CabinetStageRoleFilter[];
	/** Стадии доски (клиентская фильтрация колонок). */
	stageVerification: CabinetStagesStageIndex[];
	/** Фильтр по статусам документа (серверная фильтрация через `doc_statuses`). */
	docStatuses: CabinetDocStatusFilter[];
	/** Категории документа (серверная фильтрация через `categories`). */
	categories: string[];
}

export interface DocumentGetResponse {
	doc_id: number;
	title: string;
	description: string;
	authors: { id: number; fio: string }[];
	created_at: string;
	modified_at: string;
	status?: DocumentUserStatus | null;
}

export type CommentStatus = 'accepted' | 'declined';

export type ReviewStatus = 'accepted' | 'declined';

/** GET /v1/cabinet/document/{doc_id} → document (фрагмент). */
export interface V1CabinetDocumentGetDocumentResponse {
	title: string;
	description: string;
	file_id: number;
	authors: number[];
	stage_id: number;
	created_at: string;
	modified_at: string;
	pdf_file_id?: number | null;
	status?: DocumentUserStatus | null;
}

export interface V1CabinetDocumentCommentResponse {
	comment_id: number;
	doc_id: number;
	stage_id: number;
	user_id?: number;
	author?: {
		user_id: number
		fio: string
	}
	reply_to?: number | null;
	remark?: string | null;
	proposal?: string | null;
	justification?: string | null;
	developer_response?: string | null;
	xfdf: string;
	status?: CommentStatus | null;
	is_viewed?: boolean;
	created_at: string;
}

export interface V1CabinetDocumentGetReviewResponse {
	stage_id: number;
	doc_id: number;
	user_id: number;
	status?: ReviewStatus | null;
	is_viewed: boolean;
}

/** GET /v1/cabinet/document/{doc_id} — document + reviews + comments этапа документа. */
export interface V1CabinetDocumentGetResponse {
	document: V1CabinetDocumentGetDocumentResponse;
	reviews: V1CabinetDocumentGetReviewResponse[];
	comments: V1CabinetDocumentCommentResponse[];
}

/** POST /v1/cabinet/document/{doc_id}/comments */
export interface V1CabinetDocumentCreateCommentRequest {
	stage_id: number;
	xfdf: string;
	remark?: string | null;
	proposal?: string | null;
	justification?: string | null;
	developer_response?: string | null;
	reply_to?: number | null;
}

/** PATCH /v1/cabinet/documents/{doc_id}/comments/{comment_id} */
export interface V1CabinetDocumentsCommentPatchRequest {
	is_viewed?: boolean | null;
	status?: CommentStatus | null;
}

export interface V1StageWithReviewerAndDocsGetResponse {
	stage: StageSummaryGetResponse;
	docs?: DocumentGetResponse[];
	reviewers?: StageReviewerUserGetResponse[];
}

export type V1StagesListGetResponse200 = V1StageWithReviewerAndDocsGetResponse[];

/** POST /v1/cabinet/document/move */
export interface V1ChangeDocStagePostRequest {
	doc_id: number;
	stage_id: number;
}

/** GET /v1/cabinet/notifications/unread */
export interface V1CabinetNotificationUnreadItem {
	id: number;
	event_type: string;
	title: string;
	body: string;
	payload: Record<string, unknown>;
	created_at: number;
}

export interface V1CabinetNotificationsUnreadGetResponse {
	items: V1CabinetNotificationUnreadItem[];
}

export interface TUser {
	email: string;
	password: string;
	name: string;
	avatar: string;
}
