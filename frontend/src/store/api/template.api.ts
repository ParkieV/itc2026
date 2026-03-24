import { api } from '@store/api/api'

export const templateApi = api.injectEndpoints({
	endpoints: builder => ({
		getTemplateList: builder.query({
			query: () => ({ url: '/template', method: 'GET' }),
			providesTags: ['Documents'],
		}),
		postTemplate: builder.mutation({
			query: (body: { name: string }) => ({
				url: '/template',
				method: 'POST',
				body,
			}),
			invalidatesTags: ['Documents'],
		}),
	}),
})

export const { useGetTemplateListQuery, usePostTemplateMutation } = templateApi
