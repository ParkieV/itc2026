import type { FC, RefObject } from 'react'
import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ChecksIcon, ExclamationMarkIcon, ArrowCircleUpRightIcon, CaretDoubleLeftIcon } from '@phosphor-icons/react'
import { toast } from '@heroui/react'

import cls from './NotificationsPopover.module.scss'

import type {
	V1CabinetNotificationUnreadItem,
	V1CabinetNotificationsUnreadGetResponse,
} from '@shared/types/api'
import { useListCabinetUnreadNotificationsQuery, useMarkCabinetNotificationReadMutation } from '@store/api/notifications.api'
import { AVATAR_EUGENIA, AVATAR_MARTIN } from '@components/CreateDocumentModal/assets'

type Props = {
	open: boolean
	onClose: () => void
	bellButtonRef: RefObject<HTMLButtonElement | null>
}

const pluralRu = (n: number, one: string, few: string, many: string): string => {
	const mod10 = n % 10
	const mod100 = n % 100
	if (mod10 === 1 && mod100 !== 11) return one
	if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return few
	return many
}

const toUnixSeconds = (ts: number): number => {
	// На всякий случай: если прилетели миллисекунды.
	if (ts > 1_000_000_000_000) {
		return Math.floor(ts / 1000)
	}
	return ts
}

const formatRelativeRU = (unixCreatedAt: number): string => {
	const createdSec = toUnixSeconds(unixCreatedAt)
	const nowSec = Math.floor(Date.now() / 1000)
	const delta = Math.max(0, nowSec - createdSec)

	const minutes = Math.floor(delta / 60)
	if (minutes < 60) {
		return `${minutes} ${pluralRu(minutes, 'минуту', 'минуты', 'минут')} назад`
	}

	const hours = Math.floor(minutes / 60)
	if (hours < 24) {
		return `${hours} ${pluralRu(hours, 'час', 'часа', 'часов')} назад`
	}

	const days = Math.floor(hours / 24)
	return `${days} ${pluralRu(days, 'день', 'дня', 'дней')} назад`
}

const isSameLocalDate = (a: Date, b: Date): boolean => {
	return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate()
}

const extractDocIdFromPayload = (payload: Record<string, unknown>): number | null => {
	const keys = ['doc_id', 'document_id', 'docId', 'documentId']
	for (const k of keys) {
		const v = payload?.[k]
		if (typeof v === 'number' && Number.isFinite(v)) {
			return Math.trunc(v)
		}
		if (typeof v === 'string') {
			const parsed = Number.parseInt(v, 10)
			if (!Number.isNaN(parsed)) return parsed
		}
	}
	return null
}

const mapEventToAvatarIcon = (item: V1CabinetNotificationUnreadItem): 'none' | 'required' | 'stage' => {
	const t = item.event_type?.toLowerCase?.() ?? ''
	if (t.includes('action_required') || t.includes('edits_required') || t.includes('required')) {
		return 'required'
	}
	if (t.includes('next_stage') || t.includes('stage') || t.includes('moved')) {
		return 'stage'
	}
	if (t.includes('comment')) {
		return 'none'
	}
	return 'none'
}

export const NotificationsPopover: FC<Props> = ({ open, onClose, bellButtonRef }) => {
	const popoverRef = useRef<HTMLDivElement | null>(null)
	const navigate = useNavigate()

	const { data, isLoading, isError } = useListCabinetUnreadNotificationsQuery(undefined, {
		skip: !open,
	})
	const [markRead] = useMarkCabinetNotificationReadMutation()

	const [isMarkingAll, setIsMarkingAll] = useState(false)

	const groups = useMemo(() => {
		const response = data as V1CabinetNotificationsUnreadGetResponse | undefined
		const items = response?.items ?? []
		const today = new Date()
		const todayItems: V1CabinetNotificationUnreadItem[] = []
		const earlierItems: V1CabinetNotificationUnreadItem[] = []

		for (const it of items) {
			const createdSec = toUnixSeconds(it.created_at)
			const createdDate = new Date(createdSec * 1000)
			if (isSameLocalDate(createdDate, today)) {
				todayItems.push(it)
			} else {
				earlierItems.push(it)
			}
		}

		return {
			today: todayItems,
			earlier: earlierItems,
		}
	}, [data])

	useEffect(() => {
		if (!open) return

		const onMouseDown = (e: globalThis.MouseEvent): void => {
			const target = e.target as Node | null
			if (!target) return

			if (popoverRef.current?.contains(target)) return
			if (bellButtonRef.current?.contains(target)) return

			onClose()
		}

		const onKeyDown = (e: globalThis.KeyboardEvent): void => {
			if (e.key === 'Escape') {
				onClose()
			}
		}

		document.addEventListener('mousedown', onMouseDown)
		document.addEventListener('keydown', onKeyDown)
		return () => {
			document.removeEventListener('mousedown', onMouseDown)
			document.removeEventListener('keydown', onKeyDown)
		}
	}, [open, onClose, bellButtonRef])

	const onItemClick = async (item: V1CabinetNotificationUnreadItem): Promise<void> => {
		// 1) отметим как прочитанное
		try {
			await markRead(item.id).unwrap()
		} catch {
			// Ошибка не должна ломать UX перехода — просто покажем уведомление.
			toast('Не удалось отметить уведомление как прочитанное', {
				variant: 'accent',
				description: 'Попробуйте ещё раз.',
			})
		}

		// 2) затем — попытка перехода к документу
		const docId = extractDocIdFromPayload(item.payload ?? {})
		if (docId != null) {
			navigate(`/pdf/${docId}`)
		}

		onClose()
	}

	const onMarkAllRead = async (): Promise<void> => {
		if (isMarkingAll) return
		const ids = data?.items?.map((x) => x.id) ?? []
		if (!ids.length) {
			onClose()
			return
		}
		setIsMarkingAll(true)
		try {
			await Promise.allSettled(ids.map((id) => markRead(id).unwrap()))
		} finally {
			setIsMarkingAll(false)
			onClose()
		}
	}

	if (!open) return null

	return (
		<div ref={popoverRef} className={cls.popover} role="dialog" aria-modal="false">
			<div className={cls.headerRow}>
				<p className={cls.headerTitle}>уведомления</p>
				<button
					type="button"
					className={cls.checksBtn}
					aria-label="Отметить все уведомления как прочитанные"
					onClick={() => void onMarkAllRead()}
					disabled={isLoading || isError || isMarkingAll}
				>
					<ChecksIcon size={22} weight="regular" />
				</button>
			</div>

			<div className={cls.listCard}>
				{isLoading ? <div className={cls.loading}>Загрузка…</div> : null}
				{isError ? (
					<div className={cls.loading}>
						Не удалось загрузить уведомления. Попробуйте обновить страницу.
					</div>
				) : null}

				{!isLoading && !isError ? (
					<div className={cls.groups}>
						{groups.today.length ? (
							<div className={cls.group}>
								<div className={cls.groupLabel}>Сегодня</div>
								<div className={cls.groupItems}>
									{groups.today.map((item, idx) => (
										<button
											key={item.id}
											type="button"
											className={cls.item}
											onClick={() => void onItemClick(item)}
										>
											<div className={cls.itemInner}>
												<div className={cls.avatarWrap} aria-hidden>
													<img
														className={cls.avatarImg}
														src={idx % 2 === 0 ? AVATAR_MARTIN : AVATAR_EUGENIA}
														alt=""
														width={40}
														height={40}
													/>
													{mapEventToAvatarIcon(item) === 'required' ? (
														<ExclamationMarkIcon
															className={cls.avatarIconOverlay}
															size={18}
															weight="regular"
														/>
													) : null}
													{mapEventToAvatarIcon(item) === 'stage' ? (
														<CaretDoubleLeftIcon
															className={cls.avatarIconOverlay}
															size={18}
															weight="regular"
														/>
													) : null}
												</div>

												<div className={cls.itemText}>
													<p className={cls.itemTitle}>{item.title}</p>
													<p className={cls.itemBody}>{item.body}</p>
												</div>
												<p className={cls.itemTime}>{formatRelativeRU(item.created_at)}</p>
											</div>
											{idx !== groups.today.length - 1 ? <div className={cls.divider} /> : null}
										</button>
									))}
								</div>
							</div>
						) : null}

						{groups.earlier.length ? (
							<div className={cls.group}>
								<div className={cls.groupLabel}>Ранее</div>
								<div className={cls.groupItems}>
									{groups.earlier.map((item, idx) => (
										<button
											key={item.id}
											type="button"
											className={cls.item}
											onClick={() => void onItemClick(item)}
										>
											<div className={cls.itemInner}>
												<div className={cls.avatarWrap} aria-hidden>
													<img
														className={cls.avatarImg}
														src={idx % 2 === 0 ? AVATAR_MARTIN : AVATAR_EUGENIA}
														alt=""
														width={40}
														height={40}
													/>
													{mapEventToAvatarIcon(item) === 'required' ? (
														<ExclamationMarkIcon
															className={cls.avatarIconOverlay}
															size={18}
															weight="regular"
														/>
													) : null}
													{mapEventToAvatarIcon(item) === 'stage' ? (
														<CaretDoubleLeftIcon
															className={cls.avatarIconOverlay}
															size={18}
															weight="regular"
														/>
													) : null}
												</div>

												<div className={cls.itemText}>
													<p className={cls.itemTitle}>{item.title}</p>
													<p className={cls.itemBody}>{item.body}</p>
												</div>
												<p className={cls.itemTime}>{formatRelativeRU(item.created_at)}</p>
											</div>
											{idx !== groups.earlier.length - 1 ? <div className={cls.divider} /> : null}
										</button>
									))}
								</div>
							</div>
						) : null}

						{!groups.today.length && !groups.earlier.length ? (
							<div className={cls.empty}>Нет уведомлений</div>
						) : null}
					</div>
				) : null}
			</div>

			{/* В Figma справа внутри карточки есть небольшая пиктограмма "открыть документ".
				Здесь она не обязательна, т.к. переход делается по клику на сам пункт уведомления. */}
			<div className={cls.hiddenForLayout} aria-hidden>
				<ArrowCircleUpRightIcon size={18} weight="regular" />
			</div>
		</div>
	)
}

