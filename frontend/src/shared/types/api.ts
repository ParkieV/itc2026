/** Тело ошибки от бэка (подстройте под контракт API). */
export interface ApiErrorBody {
	message?: string
	code?: string
	errors?: Record<string, string[]>
}

export interface PaginatedResponse<T> {
	items: T[]
	total: number
	page: number
	pageSize: number
}

export interface AuthResponse {
	token: string
}

export interface AuthRequest {
	tmaToken: string
	refId?: string
}

export interface TUser {
	email: string
	password: string
	name: string
	avatar: string
}