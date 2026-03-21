import { createApi } from '@reduxjs/toolkit/query/react'

import { baseQuery } from '@/store/api/baseQuery'
import { API_TAG_TYPES } from '@/store/api/tags'

export const api = createApi({
	reducerPath: 'api',
	tagTypes: [...API_TAG_TYPES],
	baseQuery,
	endpoints: () => ({}),
})
