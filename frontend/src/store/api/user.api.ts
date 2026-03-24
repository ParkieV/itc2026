import { api } from '@store/api/api'
import { TUser } from '@shared/types/api'
export const arsenalApi = api.injectEndpoints({
	endpoints: builder => ({
		patchUser: builder.mutation({
			query: (body: { user: TUser }) => ({
				method: 'PATCH',
				url: '/user',
				body,
			}),
			invalidatesTags: ['User'],
		}),
		getUser: builder.query({
			query: () => '/user',
			providesTags: ['User'],
		}),
	}),
})

export const {
	usePatchUserMutation,
	useGetUserQuery,
} = arsenalApi
