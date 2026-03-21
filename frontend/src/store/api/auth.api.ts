import { api } from '@/store/api/api'
import { actions } from '@/store/auth/auth.slice'
import type { AuthRequest, AuthResponse } from '@/types/api'

export const authApi = api.injectEndpoints({
	endpoints: builder => ({
		auth: builder.mutation<AuthResponse, AuthRequest>({
			query: body => ({
				method: 'POST',
				url: '/user/login',
				body,
			}),
			async onQueryStarted(_arg, { dispatch, queryFulfilled }) {
				try {
					const { data } = await queryFulfilled
					if (data.token) {
						dispatch(actions.setToken(data.token))
					}
				} catch {
					// ошибка уже в result.error у хука
				}
			},
		}),
	}),
})

export const { useAuthMutation } = authApi
