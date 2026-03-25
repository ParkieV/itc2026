import { createSlice, PayloadAction } from '@reduxjs/toolkit'


interface initialState {
	token: string | null
}

const initialState: initialState = {
	token: localStorage.getItem('token') || null
}

export const authSlice = createSlice({
	name: 'auth',
	initialState,
	reducers: {
		setToken: (state, action: PayloadAction<string>) => {
			state.token = action.payload
			localStorage.setItem('token', action.payload)
		},
		clearToken: (state) => {
			state.token = null
			localStorage.removeItem('token')
		},
	}
})

export const { actions, reducer } = authSlice
