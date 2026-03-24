import { RootState } from '@store/store'

export const prepareHeaders = (headers: Headers, state: RootState) => {
  const token = state.auth.token;
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
	return headers
}
