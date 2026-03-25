import { api } from '@store/api/api'

import type { V1CabinetDocumentFilePostResponse200 } from '@shared/types/api'

export const documentsApi = api.injectEndpoints({
	endpoints: (builder) => ({
		createCabinetDocumentFile: builder.mutation<
			V1CabinetDocumentFilePostResponse200,
			FormData
		>({
			query: (body) => ({
				method: 'POST',
				url: '/cabinet/document/file',
				body,
			}),
			invalidatesTags: ['Documents', 'Stages'],
		}),
	}),
})

export const { useCreateCabinetDocumentFileMutation } = documentsApi
