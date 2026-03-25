import { FC, useEffect, useId, useMemo, useRef, type MouseEvent as ReactMouseEvent } from 'react'
import { createPortal } from 'react-dom'
import { PencilLineIcon, XIcon } from '@phosphor-icons/react'

import cls from './UserProfileModal.module.scss'

export interface UserProfileModalProps {
	open: boolean
	onClose: () => void
	onLogout: () => void
	fio: string
	organization: string | null | undefined
}

export const UserProfileModal: FC<UserProfileModalProps> = ({
	open,
	onClose,
	onLogout,
	fio,
	organization,
}) => {
	const titleId = useId()
	const closeBtnRef = useRef<HTMLButtonElement | null>(null)

	const initials = useMemo(() => {
		const s = fio?.trim()
		if (!s) {
			return '—'
		}
		return s.slice(0, 2).toUpperCase()
	}, [fio])

	useEffect(() => {
		if (!open) {
			return
		}

		const prevOverflow = document.body.style.overflow
		document.body.style.overflow = 'hidden'

		const onKeyDown = (e: globalThis.KeyboardEvent): void => {
			if (e.key === 'Escape') {
				onClose()
			}
		}

		document.addEventListener('keydown', onKeyDown)
		// После монтирования даем фокус закрывающей кнопке.
		window.requestAnimationFrame(() => closeBtnRef.current?.focus())

		return () => {
			document.body.style.overflow = prevOverflow
			document.removeEventListener('keydown', onKeyDown)
		}
	}, [open, onClose])

	const onOverlayMouseDown = (e: ReactMouseEvent<HTMLDivElement>): void => {
		if (e.target === e.currentTarget) {
			onClose()
		}
	}

	if (!open) {
		return null
	}

	// Mock-тексты из Figma. Имя/организация берём из store, остальное оставляем моковым.
	const mockAbout =
		'Эксперт в области интеллектуальных транспортных систем с опытом разработки стандартов обмена данными и архитектур цифровой инфраструктуры. Участвует в экспертной оценке нормативных документов и технических рекомендаций.'
	const mockPosition =
		'Эксперт по интеллектуальным транспортным системам'
	const mockRole = 'Эксперт, рецензент'
	const competencyChips = [
		'ITS',
		'Data Exchange',
		'Smart Infrastructure',
		'Transport Analytics',
		'Digital Standards',
	]

	return createPortal(
		<div className={cls.overlay} role="presentation" onMouseDown={onOverlayMouseDown}>
			<div
				className={cls.dialog}
				role="dialog"
				aria-modal="true"
				aria-labelledby={titleId}
				onMouseDown={(e) => e.stopPropagation()}
			>
				<div className={cls.header}>
					<div className={cls.headerLeft}>
						<div className={cls.avatarCircle} aria-hidden>
							{initials}
						</div>
						<div className={cls.headerText}>
							<h2 id={titleId} className={cls.name}>
								{fio}
							</h2>
							<p className={cls.email}>
								{organization?.toString().trim() ? organization : '—'}
							</p>
						</div>
					</div>

					{/* В макете X расположен в правой части заголовка. */}
					<div className={cls.headerRight}>
						<button
							ref={closeBtnRef}
							type="button"
							className={cls.closeBtn}
							aria-label="Закрыть"
							onClick={onClose}
						>
							<XIcon size={22} weight="regular" />
						</button>
					</div>
				</div>

				<div className={cls.contentStack}>
					<section className={cls.mainCard}>
						<div className={cls.cardCol}>
							<div className={cls.cardBlock}>
								<p className={cls.label}>О специалисте</p>
								<p className={cls.value}>{mockAbout}</p>
							</div>

							<div className={cls.cardBlock}>
								<p className={cls.label}>Должность</p>
								<p className={cls.value}>{mockPosition}</p>
							</div>

							<div className={cls.cardBlock}>
								<p className={cls.label}>Роль в системе</p>
								<p className={cls.value}>{mockRole}</p>
							</div>

							<div className={cls.cardBlock}>
								<p className={cls.label}>Компетенции</p>
								<div className={cls.chips}>
									{competencyChips.map((t) => (
										<div key={t} className={cls.chip}>
											{t}
										</div>
									))}
								</div>
							</div>
						</div>
					</section>

					<section className={cls.statsCard}>
						<div className={cls.statsRow}>
							<div className={cls.statItem}>
								<p className={cls.statLabel}>Документы на экспертизе</p>
								<p className={cls.statValue}>3</p>
							</div>
							<div className={cls.statDivider} aria-hidden />
							<div className={cls.statItem}>
								<p className={cls.statLabel}>Завершенные экспертизы</p>
								<p className={cls.statValue}>67</p>
							</div>
							<div className={cls.statDivider} aria-hidden />
							<div className={cls.statItem}>
								<p className={cls.statLabel}>Среднее время ответа</p>
								<p className={cls.statValueAccent}>4 дня</p>
							</div>
							<div className={cls.statDivider} aria-hidden />
							<div className={cls.statItem}>
								<p className={cls.statLabel}>Комментарии и рекомендации</p>
								<p className={cls.statValue}>86</p>
							</div>
						</div>
					</section>

					<button type="button" className={cls.editBtn} onClick={onClose}>
						редактировать профиль
						<PencilLineIcon className={cls.editIcon} size={18} />
					</button>
				</div>

				<button
					type="button"
					className={cls.exitBtn}
					onClick={() => {
						onLogout()
						onClose()
					}}
				>
					выйти
				</button>
			</div>
		</div>,
		document.body
	)
}

