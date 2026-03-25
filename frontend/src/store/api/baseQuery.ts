import { fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import type { FetchArgs } from '@reduxjs/toolkit/query'

import { prepareHeaders } from '@shared/utils/prepareHeaders'
import type { RootState } from '@store/store'
import { actions as authActions } from '@store/auth/auth.slice'

const rawBaseQuery = fetchBaseQuery({
	baseUrl: import.meta.env.VITE_API_URL,
	prepareHeaders: (headers, { getState }) =>
		prepareHeaders(headers, getState() as RootState),
})

const isAuthAuthenticateRequest = (args: string | FetchArgs): boolean => {
	const path = typeof args === 'string' ? args : args.url
	return path.includes('auth/authenticate')
}

export const baseQuery = async (
	args: string | FetchArgs,
	api: Parameters<typeof rawBaseQuery>[1],
	extraOptions: Parameters<typeof rawBaseQuery>[2],
) => {
	const result = await rawBaseQuery(args, api, extraOptions)

	if (
		result.error?.status === 401 &&
		!isAuthAuthenticateRequest(args)
	) {
		const data = result.error.data as { detail?: string } | undefined
		if (data?.detail === 'invalid_token') {
			api.dispatch(authActions.clearToken())
		}
	}

	return result
}
