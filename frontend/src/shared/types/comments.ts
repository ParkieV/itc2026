export interface DocumentComment {
	id: string
	documentId: string
	annotationId?: string
	selectedText: string
	content: string
	pageNumber?: number
	createdAt: string
	updatedAt: string
}

export interface CreateCommentInput {
	documentId: string
	annotationId?: string
	selectedText: string
	content: string
	pageNumber?: number
}

export interface UpdateCommentInput {
	id: string
	documentId: string
	content: string
}

