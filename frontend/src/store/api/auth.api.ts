import { api } from '@store/api/api'
import { actions } from '@store/auth/auth.slice'
import type { V1AuthenticateRequest, V1AuthenticateResponse } from '@shared/types/api'

const formBody = (username: string, password: string): URLSearchParams => {
	const params = new URLSearchParams()
	params.set('username', username)
	params.set('password', password)
	params.set('grant_type', 'password')
	return params
}

export const authApi = api.injectEndpoints({
	endpoints: (builder) => ({
		authenticate: builder.mutation<V1AuthenticateResponse, V1AuthenticateRequest>({
			query: ({ username, password }) => ({
				method: 'POST',
				url: '/auth/authenticate',
				body: formBody(username, password),
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded',
				},
			}),
			async onQueryStarted(_arg, { dispatch, queryFulfilled }) {
				try {
					const { data } = await queryFulfilled
					if (data.access_token) {
						dispatch(actions.setToken(data.access_token))
					}
				} catch {
					// токен не ставим; ошибку читает хук мутации
				}
			},
		}),
	}),
})

export const { useAuthenticateMutation } = authApi
