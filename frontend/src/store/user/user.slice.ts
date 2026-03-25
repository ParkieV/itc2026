import { createSlice, PayloadAction } from '@reduxjs/toolkit'

import type { V1CabinetMeGetResponse } from '@shared/types/api'

interface UserState {
	profile: V1CabinetMeGetResponse | null
}

const initialState: UserState = {
	profile: null,
}

export const userSlice = createSlice({
	name: 'user',
	initialState,
	reducers: {
		setProfile: (state, action: PayloadAction<V1CabinetMeGetResponse>) => {
			state.profile = action.payload
		},
		clearProfile: (state) => {
			state.profile = null
		},
	},
})

export const { actions, reducer } = userSlice
