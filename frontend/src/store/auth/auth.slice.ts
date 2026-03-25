import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import cookies from 'js-cookie'

interface initialState {
	token: string | null
}

const initialState: initialState = {
	token: cookies.get('token') || null
}

export const authSlice = createSlice({
	name: 'auth',
	initialState,
	reducers: {
		setToken: (state, action: PayloadAction<string>) => {
			state.token = action.payload
			cookies.set('token', action.payload, { expires: 1 / 24, secure: true })
		},
		clearToken: (state) => {
			state.token = null
			cookies.remove('token')
		},
	}
})

export const { actions, reducer } = authSlice
