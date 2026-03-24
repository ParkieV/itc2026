import { fetchBaseQuery } from '@reduxjs/toolkit/query/react'

import { prepareHeaders } from '@shared/utils/prepareHeaders'
import type { RootState } from '@store/store'

export const baseQuery = fetchBaseQuery({
	baseUrl: import.meta.env.VITE_API_URL,
	prepareHeaders: (headers, { getState }) =>
		prepareHeaders(headers, getState() as RootState),
})
