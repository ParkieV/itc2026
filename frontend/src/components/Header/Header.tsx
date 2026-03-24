import { FC } from 'react';
import { Avatar } from '@heroui/react';
import cls from './Header.module.scss';
import { useLocation, useNavigate } from 'react-router-dom';

const NAV_ITEMS = [
	{ id: 'home', label: 'главная', count: null },
	{ id: 'kanban', label: 'все документы', count: 7 },
	{ id: 'news', label: 'новости', count: 7 },
	{ id: 'reco', label: 'рекомендации', count: 11 },
];

export const Header: FC = () => {
	const navigate = useNavigate();
	const { pathname } = useLocation();

	const activeItem =
		NAV_ITEMS.find(
			(item) => pathname === `/${item.id}` || pathname.startsWith(`/${item.id}/`),
		)?.id ?? (pathname === '/' ? 'home' : '');

	const handleNavClick = (itemId: string) => {
		navigate(`/${itemId}`);
	};

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
			</nav>

			<div className={cls.profilePill}>
				<span className={cls.profileDots}>⋮⋮</span>
				<span className={cls.profileName}>Мартин Кабаре / Глава НИИ ФГУ</span>
				<Avatar className={cls.profileAvatar} size="md">
					<Avatar.Fallback>МК</Avatar.Fallback>
				</Avatar>
			</div>
		</header>
	);
};
