import { FC, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Outlet } from 'react-router-dom'

import { Header } from '@components/Header/Header'
import { LoginModalGate } from '@components/LoginModal/LoginModal'
import { useGetCabinetMeQuery } from '@store/api/cabinet.api'
import type { AppDispatch, RootState } from '@store/store'
import { actions as userActions } from '@store/user/user.slice'
import cls from './AppShell.module.scss'

export const AppShell: FC = () => {
	const dispatch = useDispatch<AppDispatch>()
	const token = useSelector((s: RootState) => s.auth.token)

	useGetCabinetMeQuery(undefined, { skip: !token })

	useEffect(() => {
		if (!token) {
			dispatch(userActions.clearProfile())
		}
	}, [token, dispatch])

	return (
		<div className={cls.shell}>
			<Header />
			<div className={cls.content}>
				<Outlet />
			</div>
			<LoginModalGate />
		</div>
	)
}
