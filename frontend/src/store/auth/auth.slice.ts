import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface initialState {
	token: string | null
}

const TOKEN_STORAGE_KEY = 'token'

const readTokenFromStorage = (): string | null => {
	try {
		if (typeof window === 'undefined') return null
		return localStorage.getItem(TOKEN_STORAGE_KEY)
	} catch {
		return null
	}
}

const initialState: initialState = {
	token: readTokenFromStorage(),
}

export const authSlice = createSlice({
	name: 'auth',
	initialState,
	reducers: {
		setToken: (state, action: PayloadAction<string>) => {
			state.token = action.payload
			try {
				localStorage.setItem(TOKEN_STORAGE_KEY, action.payload)
			} catch {
				// если storage недоступен — оставляем state.token без падения приложения
			}
		},
		clearToken: (state) => {
			state.token = null
			try {
				localStorage.removeItem(TOKEN_STORAGE_KEY)
			} catch {
				// ignore
			}
		},
	}
})

export const { actions, reducer } = authSlice
