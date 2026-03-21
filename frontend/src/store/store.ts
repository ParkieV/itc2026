import { combineReducers, configureStore } from '@reduxjs/toolkit'

import { reducer as authReducer } from '@/store/auth/auth.slice.ts'


import { api } from '@/store/api/api'
import '@/store/api/auth.api'
import '@/store/api/user.api'
import '@/store/api/template.api'

const reducers = combineReducers({
	auth: authReducer,
	[api.reducerPath]: api.reducer,
})

export const store = configureStore({
	reducer: reducers,
	devTools: true,
	middleware: getDefaultMiddleware => getDefaultMiddleware().concat(api.middleware)
})
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
