import { FC, useEffect, useRef, useState } from 'react'
import { Avatar } from '@heroui/react';
import cls from './Header.module.scss';
import { useLocation, useNavigate } from 'react-router-dom';
import BellRingIcon from '@assets/icons/bellring.svg';
import { useDispatch, useSelector } from 'react-redux'
import type { RootState, AppDispatch } from '@store/store'
import { actions as authActions } from '@store/auth/auth.slice'
import { actions as userActions } from '@store/user/user.slice'
import { UserProfileModal } from '@components/UserProfileModal/UserProfileModal'
import { NotificationsPopover } from '@components/NotificationsPopover/NotificationsPopover'
const NAV_ITEMS = [
	// { id: 'home', label: 'главная', count: null },
	{ id: 'home', label: 'все документы', count: 7 },
];

export const Header: FC = () => {
	const navigate = useNavigate();
	const { pathname } = useLocation();
	const dispatch = useDispatch<AppDispatch>()

	const profile = useSelector((s: RootState) => s.user.profile)
	const [profileOpen, setProfileOpen] = useState(false)
	const [notificationsOpen, setNotificationsOpen] = useState(false)
	const bellButtonRef = useRef<HTMLButtonElement | null>(null)

	useEffect(() => {
		setNotificationsOpen(false)
	}, [pathname])

	const activeItem =
		NAV_ITEMS.find((item) => pathname === `/${item.id}` || pathname.startsWith(`/${item.id}/`))
			?.id ?? (pathname === '/' ? 'home' : '');

	const handleNavClick = (itemId: string) => {
		navigate(`/${itemId}`);
	};

	const handleLogout = () => {
		dispatch(authActions.clearToken())
		dispatch(userActions.clearProfile())
		navigate('/')
	}

	const fio = profile?.fio ?? '—'
	const organization = profile?.organization ?? null

	return (
		<>
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
				<div className={cls.bellWrap}>
					<button
						ref={bellButtonRef}
						type="button"
						className={cls.navItem}
						aria-label="Открыть уведомления"
						onClick={() => setNotificationsOpen((v) => !v)}
					>
						<img src={BellRingIcon} alt="bell" />
					</button>
					<NotificationsPopover
						open={notificationsOpen}
						onClose={() => setNotificationsOpen(false)}
						bellButtonRef={bellButtonRef}
					/>
				</div>
			</nav>

			<div
				className={cls.profilePill}
				onClick={() => setProfileOpen(true)}
				onKeyDown={(e) => {
					if (e.key === 'Enter' || e.key === ' ') {
						setProfileOpen(true)
					}
				}}
				role="button"
				tabIndex={0}
			>
				<span className={cls.profileDots}>⋮⋮</span>
				<span className={cls.profileName}>
					{fio} / {organization ?? '—'}
				</span>
				<Avatar className={cls.profileAvatar} size="md">
					<Avatar.Fallback>
						{fio?.trim()?.slice(0, 2)?.toUpperCase() ?? '—'}
					</Avatar.Fallback>
				</Avatar>
			</div>
			</header>

			<UserProfileModal
				open={profileOpen}
				onClose={() => setProfileOpen(false)}
				onLogout={handleLogout}
				fio={fio}
				organization={organization}
			/>
		</>
	);
};
