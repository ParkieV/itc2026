import { api } from '@store/api/api'
import { commentsStorage } from '@mocks/commentsStorage'
import type {
	CreateCommentInput,
	DocumentComment,
	UpdateCommentInput,
} from '@shared/types/comments'

export const commentsApi = api.injectEndpoints({
	endpoints: builder => ({
		getDocumentComments: builder.query<DocumentComment[], string>({
			queryFn: async documentId => ({
				data: commentsStorage.getByDocument(documentId),
			}),
			providesTags: (_result, _error, documentId) => [
				{ type: 'Comments', id: documentId },
			],
		}),
		createComment: builder.mutation<DocumentComment, CreateCommentInput>({
			queryFn: async input => ({ data: commentsStorage.create(input) }),
			invalidatesTags: (_result, _error, input) => [
				{ type: 'Comments', id: input.documentId },
			],
		}),
		updateComment: builder.mutation<DocumentComment, UpdateCommentInput>({
			queryFn: async input => ({ data: commentsStorage.update(input) }),
			invalidatesTags: (_result, _error, input) => [
				{ type: 'Comments', id: input.documentId },
			],
		}),
		deleteComment: builder.mutation<void, { documentId: string; id: string }>({
			queryFn: async ({ documentId, id }) => {
				commentsStorage.remove(documentId, id)
				return { data: undefined }
			},
			invalidatesTags: (_result, _error, input) => [
				{ type: 'Comments', id: input.documentId },
			],
		}),
	}),
})

export const {
	useGetDocumentCommentsQuery,
	useCreateCommentMutation,
	useUpdateCommentMutation,
	useDeleteCommentMutation,
} = commentsApi

