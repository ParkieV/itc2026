import type { FetchBaseQueryError } from '@reduxjs/toolkit/query'
import { FC, FormEvent, useId, useState } from 'react'
import { createPortal } from 'react-dom'
import { useSelector } from 'react-redux'

import { useAuthenticateMutation } from '@store/api/auth.api'
import type { RootState } from '@store/store'

import cls from './LoginModal.module.scss'

export interface LoginModalProps {
	open: boolean
}

function isFetchBaseQueryError(error: unknown): error is FetchBaseQueryError {
	return typeof error === 'object' && error !== null && 'status' in error
}

function getAuthenticateErrorMessage(error: unknown): string {
	if (isFetchBaseQueryError(error)) {
		const { data, status } = error
		if (data && typeof data === 'object' && 'detail' in data) {
			const detail = (data as { detail: unknown }).detail
			if (typeof detail === 'string' && detail.trim()) {
				return detail
			}
			if (Array.isArray(detail)) {
				return detail
					.map((item) => {
						if (item && typeof item === 'object' && 'msg' in item) {
							return String((item as { msg: unknown }).msg)
						}
						return String(item)
					})
					.join(', ')
			}
		}
		if (status === 400) {
			return 'Неверный пароль.'
		}
		if (status === 404) {
			return 'Пользователь с таким логином не найден.'
		}
	}
	return 'Не удалось выполнить вход. Проверьте подключение к серверу.'
}

export const LoginModal: FC<LoginModalProps> = ({ open }) => {
	const titleId = useId()
	const [username, setUsername] = useState('')
	const [password, setPassword] = useState('')
	const [localError, setLocalError] = useState<string | null>(null)
	const [authenticate, { isLoading }] = useAuthenticateMutation()

	if (!open) {
		return null
	}

	const handleSubmit = async (e: FormEvent): Promise<void> => {
		e.preventDefault()
		setLocalError(null)
		const login = username.trim()
		if (!login || !password) {
			setLocalError('Введите логин и пароль.')
			return
		}
		try {
			await authenticate({ username: login, password }).unwrap()
		} catch (err) {
			setLocalError(getAuthenticateErrorMessage(err))
		}
	}

	const node = (
		<div className={cls.overlay} role="presentation">
			<div className={cls.dialog} role="dialog" aria-modal="true" aria-labelledby={titleId}>
				<h2 id={titleId} className={cls.title}>
					Вход
				</h2>
				<p className={cls.subtitle}>Войдите под учётной записью кабинета</p>
				<form className={cls.form} onSubmit={(ev) => void handleSubmit(ev)}>
					{localError ? (
						<p className={cls.error} role="alert">
							{localError}
						</p>
					) : null}
					<label className={cls.label}>
						<span className={cls.labelText}>Логин</span>
						<input
							className={cls.input}
							name="username"
							autoComplete="username"
							value={username}
							onChange={(ev) => setUsername(ev.target.value)}
							disabled={isLoading}
						/>
					</label>
					<label className={cls.label}>
						<span className={cls.labelText}>Пароль</span>
						<input
							className={cls.input}
							name="password"
							type="password"
							autoComplete="current-password"
							value={password}
							onChange={(ev) => setPassword(ev.target.value)}
							disabled={isLoading}
						/>
					</label>
					<button type="submit" className={cls.submit} disabled={isLoading}>
						{isLoading ? 'Вход…' : 'Войти'}
					</button>
				</form>
			</div>
		</div>
	)

	return createPortal(node, document.body)
}

/** Модалка поверх приложения, пока в store нет токена */
export const LoginModalGate: FC = () => {
	const token = useSelector((s: RootState) => s.auth.token)
	return <LoginModal open={!token} />
}
