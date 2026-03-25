import { api } from '@store/api/api'
import { actions as userActions } from '@store/user/user.slice'

import type {
	V1CabinetDocumentCommentResponse,
	V1CabinetDocumentCreateCommentRequest,
	V1CabinetDocumentGetResponse,
	ReviewStatus,
	V1CabinetDocumentsCommentPatchRequest,
	V1CabinetMeGetResponse,
	V1ChangeDocStagePostRequest,
	V1StagesListQueryParams,
	V1StagesListGetResponse200,
} from '@shared/types/api'

export const cabinetApi = api.injectEndpoints({
	endpoints: (builder) => ({
		getCabinetMe: builder.query<V1CabinetMeGetResponse, void>({
			query: () => '/cabinet/me',
			providesTags: ['User'],
			async onQueryStarted(_arg, { dispatch, queryFulfilled }) {
				try {
					const { data } = await queryFulfilled
					dispatch(userActions.setProfile(data))
				} catch {
					dispatch(userActions.clearProfile())
				}
			},
		}),
		listCabinetStages: builder.query<V1StagesListGetResponse200, V1StagesListQueryParams | undefined>({
			query: (params) =>
				params
					? {
							url: '/cabinet/stages',
							params,
						}
					: '/cabinet/stages',
			providesTags: ['Stages'],
		}),
		moveCabinetDocument: builder.mutation<void, V1ChangeDocStagePostRequest>({
			query: (body) => ({
				method: 'POST',
				url: '/cabinet/document/move',
				body,
			}),
			invalidatesTags: ['Stages'],
		}),
		getCabinetDocument: builder.query<V1CabinetDocumentGetResponse, number>({
			query: (docId) => `/cabinet/document/${docId}`,
			providesTags: (_r, _e, docId) => [{ type: 'Documents', id: docId }],
		}),
		getCabinetDocumentPdf: builder.query<string, number>({
			query: (documentId) => ({
				url: '/cabinet/document/pdf_file',
				params: { document_id: documentId },
				// Возвращаем Object URL вместо Blob, чтобы Blob не попадал в state RTK Query.
				// Объектный URL нужно будет освободить на уровне страницы.
				responseHandler: async (response) => {
					const blob = await response.blob()
					return URL.createObjectURL(blob)
				},
			}),
		}),
		downloadCabinetReviewsPdf: builder.mutation<string, number>({
			// Кабинет: скачивание "сводки" (PDF) для текущего review.
			query: (docId) => ({
				method: 'POST',
				url: '/cabinet/reviews/pdf',
				params: { doc_id: docId },
				responseHandler: async (response) => {
					const blob = await response.blob()
					return URL.createObjectURL(blob)
				},
			}),
		}),
		viewCabinetReviews: builder.mutation<void, {docId: number; stageId: number}>({
			// Кабинет: отметить review как "просмотренный" при входе на страницу документа.
			query: ({docId, stageId}: {docId: number; stageId: number}) => ({
				method: 'POST',
				url: '/cabinet/reviews/view',
				params: { doc_id: docId, stage_id: stageId},
			}),
		}),
		createCabinetDocumentComment: builder.mutation<
			Record<string, unknown>,
			{ docId: number; body: V1CabinetDocumentCreateCommentRequest }
		>({
			query: ({ docId, body }) => ({
				method: 'POST',
				url: `/cabinet/document/${docId}/comments`,
				body,
			}),
			invalidatesTags: (_r, _e, { docId }) => [{ type: 'Documents', id: docId }],
		}),
		patchCabinetDocumentComment: builder.mutation<
			V1CabinetDocumentCommentResponse,
			{ docId: number; commentId: number; body: V1CabinetDocumentsCommentPatchRequest }
		>({
			query: ({ docId, commentId, body }) => ({
				method: 'PATCH',
				url: `/cabinet/documents/${docId}/comments/${commentId}`,
				body,
			}),
			invalidatesTags: (_r, _e, { docId }) => [{ type: 'Documents', id: docId }],
		}),
		setCabinetReviewStatus: builder.mutation<
			void,
			{
				docId: number
				stageId: number
				status: ReviewStatus
			}
		>({
			query: ({ docId, stageId, status }) => ({
				method: 'POST',
				url: '/cabinet/reviews/status',
				body: {
					doc_id: docId,
					stage_id: stageId,
					status,
				},
			}),
		}),
	}),
})

export const {
	useGetCabinetMeQuery,
	useListCabinetStagesQuery,
	useMoveCabinetDocumentMutation,
	useGetCabinetDocumentQuery,
	useLazyGetCabinetDocumentQuery,
	useLazyGetCabinetDocumentPdfQuery,
	useDownloadCabinetReviewsPdfMutation,
	useViewCabinetReviewsMutation,
	useCreateCabinetDocumentCommentMutation,
	usePatchCabinetDocumentCommentMutation,
	useSetCabinetReviewStatusMutation,
} = cabinetApi
