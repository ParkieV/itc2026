import { FC, useEffect, useMemo, useRef, useState } from 'react'
import { Avatar } from '@heroui/react';
import cls from './Header.module.scss';
import { useLocation, useNavigate } from 'react-router-dom';
import BellRingIcon from '@assets/icons/bellring.svg';
import { useDispatch, useSelector } from 'react-redux'
import type { RootState, AppDispatch } from '@store/store'
import { actions as authActions } from '@store/auth/auth.slice'
import { actions as userActions } from '@store/user/user.slice'
const NAV_ITEMS = [
	{ id: 'home', label: 'главная', count: null },
	{ id: 'kanban', label: 'все документы', count: 7 },
];

export const Header: FC = () => {
	const navigate = useNavigate();
	const { pathname } = useLocation();
	const dispatch = useDispatch<AppDispatch>()

	const profile = useSelector((s: RootState) => s.user.profile)
	const [logoutOpen, setLogoutOpen] = useState(false)
	const logoutRef = useRef<HTMLDivElement | null>(null)

	const activeItem =
		NAV_ITEMS.find((item) => pathname === `/${item.id}` || pathname.startsWith(`/${item.id}/`))
			?.id ?? (pathname === '/' ? 'home' : '');

	const handleNavClick = (itemId: string) => {
		navigate(`/${itemId}`);
	};

	const organizationName = useMemo(() => {
		// ожидаемый формат URL: `/${orgName}/...`
		const firstSeg = pathname.split('/').filter(Boolean)[0] ?? ''
		const banned = new Set(['pdf', 'kanban', 'home'])
		if (!firstSeg || banned.has(firstSeg.toLowerCase())) {
			return '—'
		}
		return firstSeg
	}, [pathname])

	useEffect(() => {
		if (!logoutOpen) {
			return
		}
		const onMouseDown = (e: MouseEvent) => {
			const el = logoutRef.current
			if (!el) {
				return
			}
			if (e.target instanceof Node && !el.contains(e.target)) {
				setLogoutOpen(false)
			}
		}
		document.addEventListener('mousedown', onMouseDown)
		return () => document.removeEventListener('mousedown', onMouseDown)
	}, [logoutOpen])

	const handleLogout = () => {
		dispatch(authActions.clearToken())
		dispatch(userActions.clearProfile())
		setLogoutOpen(false)
		navigate('/')
	}

	return (
		<header className={cls.header}>
			<div className={cls.searchPill}>
				<span className={cls.searchIcon}>⌕</span>
				<span className={cls.searchText}>поиск по данным</span>
			</div>

			<nav className={cls.nav}>
				{NAV_ITEMS.map((item) => (
					<button
						key={item.id}
						type="button"
						className={`${cls.navItem} ${activeItem === item.id ? cls.navItemActive : ''}`}
						onClick={() => handleNavClick(item.id)}
					>
						<span>{item.label}</span>
						{item.count !== null && <span className={cls.navBadge}>{item.count}</span>}
					</button>
				))}
				<button type="button" className={cls.navItem} onClick={() => {}}>
					<img src={BellRingIcon} alt="bell" />
				</button>
			</nav>

			<div ref={logoutRef} className={cls.profilePill} onClick={() => setLogoutOpen((v) => !v)} role="button" tabIndex={0}>
				<span className={cls.profileDots}>⋮⋮</span>
				<span className={cls.profileName}>
					{profile?.fio ?? '—'} / {organizationName}
				</span>
				<Avatar className={cls.profileAvatar} size="md">
					<Avatar.Fallback>
						{(profile?.fio?.trim()?.slice(0, 2) ?? '—').toUpperCase()}
					</Avatar.Fallback>
				</Avatar>

				{logoutOpen && (
					<div className={cls.logoutTooltip} role="dialog" aria-label="Профиль">
						<button type="button" className={cls.logoutBtn} onClick={(e) => { e.stopPropagation(); handleLogout() }}>
							выйти
						</button>
					</div>
				)}
			</div>
		</header>
	);
};
