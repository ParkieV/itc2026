import type {
	CreateCommentInput,
	DocumentComment,
	UpdateCommentInput,
} from '@/shared/types/comments'

const STORAGE_KEY = 'pdf-comments-v1'

type CommentsMap = Record<string, DocumentComment[]>

const loadMap = (): CommentsMap => {
	try {
		const raw = localStorage.getItem(STORAGE_KEY)
		if (!raw) {
			return {}
		}
		const parsed = JSON.parse(raw) as CommentsMap
		return parsed ?? {}
	} catch {
		return {}
	}
}

const saveMap = (map: CommentsMap): void => {
	localStorage.setItem(STORAGE_KEY, JSON.stringify(map))
}

const generateId = (): string =>
	`c_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`

export const commentsStorage = {
	getByDocument(documentId: string): DocumentComment[] {
		const map = loadMap()
		return [...(map[documentId] ?? [])].sort((a, b) =>
			a.createdAt < b.createdAt ? -1 : 1
		)
	},

	create(input: CreateCommentInput): DocumentComment {
		const map = loadMap()
		const now = new Date().toISOString()
		const comment: DocumentComment = {
			id: generateId(),
			documentId: input.documentId,
			annotationId: input.annotationId,
			selectedText: input.selectedText,
			content: input.content,
			pageNumber: input.pageNumber,
			createdAt: now,
			updatedAt: now,
		}
		const existing = map[input.documentId] ?? []
		map[input.documentId] = [...existing, comment]
		saveMap(map)
		return comment
	},

	update(input: UpdateCommentInput): DocumentComment {
		const map = loadMap()
		const existing = map[input.documentId] ?? []
		const idx = existing.findIndex(item => item.id === input.id)
		if (idx === -1) {
			throw new Error('Comment not found')
		}
		const updated: DocumentComment = {
			...existing[idx],
			content: input.content,
			updatedAt: new Date().toISOString(),
		}
		existing[idx] = updated
		map[input.documentId] = existing
		saveMap(map)
		return updated
	},

	remove(documentId: string, id: string): void {
		const map = loadMap()
		const existing = map[documentId] ?? []
		map[documentId] = existing.filter(item => item.id !== id)
		saveMap(map)
	},
}

