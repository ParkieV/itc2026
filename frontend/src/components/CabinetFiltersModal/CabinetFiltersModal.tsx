import type { CSSProperties, FC, MouseEvent as ReactMouseEvent } from 'react';
import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { XIcon } from '@phosphor-icons/react';

import cls from './CabinetFiltersModal.module.scss';

import type {
	CabinetDocStatusFilter,
	CabinetStageRoleFilter,
	CabinetStagesFilters,
	CabinetStagesStageIndex,
} from '@shared/types/api';

import {
	AsteriskIcon,
	CircleNotchIcon,
	CowboyHatIcon,
	ExclamationMarkIcon,
	GraphIcon,
	HandshakeIcon,
	SpinnerGapIcon,
	CheckIcon,
	ChecksIcon,
	NetworkXIcon,
	ShieldStarIcon,
	TrainIcon,
} from '@phosphor-icons/react';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type PhosphorIcon = FC<any>;

const ROLE_TOGGLES: Array<{
	key: 'author' | 'coauthor' | 'reviewer';
	label: string;
	Icon: PhosphorIcon;
}> = [
	{ key: 'author', label: 'Автор', Icon: HandshakeIcon },
	{ key: 'coauthor', label: 'Соавтор', Icon: HandshakeIcon },
	{ key: 'reviewer', label: 'Эксперт', Icon: CowboyHatIcon },
];

const STAGE_INDEXES: Array<{
	index: CabinetStagesStageIndex;
	label: string;
	dotColor: string;
}> = [
	{ index: 0, label: 'предварительная проверка', dotColor: '#C1A947' },
	{ index: 1, label: 'экспертная оценка', dotColor: '#385ABE' },
	{ index: 2, label: 'доработка', dotColor: '#D28248' },
	{ index: 3, label: 'утверждено', dotColor: '#449A7D' },
];

const DOC_STATUS_TOGGLES: Array<{
	key: CabinetDocStatusFilter;
	label: string;
	Icon: PhosphorIcon;
	activeStyle: {
		bg: string;
		color: string;
	};
}> = [
	{
		key: 'action_required',
		label: 'требуются правки',
		Icon: ExclamationMarkIcon as typeof SpinnerGapIcon,
		activeStyle: { bg: '#ae402f', color: '#fff' },
	},
	{
		key: 'new_comment',
		label: 'новые комментарии',
		Icon: CircleNotchIcon as typeof SpinnerGapIcon,
		activeStyle: { bg: '#344da0', color: '#fff' },
	},
	{
		key: 'viewed',
		label: 'просмотрено',
		Icon: ChecksIcon as typeof SpinnerGapIcon,
		activeStyle: { bg: '#0c6382', color: '#fff' },
	},
	{
		key: 'not_viewed',
		label: 'не просмотрено',
		Icon: SpinnerGapIcon as typeof SpinnerGapIcon,
		activeStyle: { bg: 'rgba(34, 43, 51, 0.05)', color: '#222b33' },
	},
	{
		key: 'waiting',
		label: 'требуется действие',
		Icon: AsteriskIcon as typeof SpinnerGapIcon,
		activeStyle: { bg: 'rgba(34, 43, 51, 0.05)', color: '#222b33' },
	},
	{
		key: 'sent',
		label: 'отправлено',
		Icon: CheckIcon as typeof SpinnerGapIcon,
		activeStyle: { bg: '#3b7488', color: '#fff' },
	},
];

const CATEGORY_TOGGLES: Array<{
	key: string;
	label: string;
	Icon: PhosphorIcon;
}> = [
	{ key: 'Транспорт', label: 'Транспорт', Icon: TrainIcon },
	{
		key: 'Цифровая инфраструктура',
		label: 'Цифровая инфраструктура',
		Icon: GraphIcon,
	},
	{ key: 'Безопасность', label: 'Безопасность', Icon: ShieldStarIcon },
	{
		key: 'Данные и интеграции',
		label: 'Данные и интеграции',
		Icon: NetworkXIcon,
	},
	{
		key: 'Инженерные системы',
		label: 'Инженерные системы',
		Icon: NetworkXIcon,
	},
];

function cn(...parts: Array<string | false | null | undefined>): string {
	return parts.filter(Boolean).join(' ');
}

function toggleInArray<T>(arr: T[], value: T): T[] {
	return arr.includes(value) ? arr.filter((x) => x !== value) : [...arr, value];
}

export interface CabinetFiltersModalProps {
	open: boolean;
	onClose: () => void;
	onApply: (filters: CabinetStagesFilters) => void;
	/** Применённые фильтры (чтобы модалка могла показывать актуальное состояние) */
	filters: CabinetStagesFilters;
	/** Кол-во документов для текста на кнопке */
	documentsCount: number;
}

export const CabinetFiltersModal: FC<CabinetFiltersModalProps> = ({
	open,
	onClose,
	onApply,
	filters,
	documentsCount,
}) => {
	const resolvedCountText = documentsCount >= 1000 ? '1000+ документов' : `${documentsCount} документов`;

	// Внутри модалки держим "черновик", чтобы изменения применялись только по кнопке.
	const [draft, setDraft] = useState<CabinetStagesFilters>(filters);

	// Синхронизируем черновик при открытии/изменении применённых фильтров.
	useEffect(() => {
		if (!open) return;
		setDraft(filters);
	}, [open, filters]);

	useEffect(() => {
		if (!open) return;
		const prevOverflow = document.body.style.overflow;
		document.body.style.overflow = 'hidden';

		const onKeyDown = (e: globalThis.KeyboardEvent): void => {
			if (e.key === 'Escape') onClose();
		};
		document.addEventListener('keydown', onKeyDown);
		return () => {
			document.body.style.overflow = prevOverflow;
			document.removeEventListener('keydown', onKeyDown);
		};
	}, [open, onClose]);

	const onOverlayMouseDown = (e: ReactMouseEvent<HTMLDivElement>): void => {
		if (e.target === e.currentTarget) onClose();
	};

	if (!open) return null;

	return createPortal(
		<div className={cls.overlay} role="presentation" onMouseDown={onOverlayMouseDown}>
			<div
				className={cls.dialog}
				role="dialog"
				aria-modal="true"
				aria-label="Фильтры"
				onMouseDown={(e) => e.stopPropagation()}
			>
				<div className={cls.header}>
					<p className={cls.title}>фильтры</p>
					<button type="button" className={cls.closeBtn} aria-label="Закрыть" onClick={onClose}>
						<XIcon size={22} weight="regular" />
					</button>
				</div>

				<div className={cls.content}>
					<section className={cls.section}>
						<p className={cls.sectionTitle}>моя роль</p>
						<div className={cls.chipsGrid}>
							{ROLE_TOGGLES.map(({ key, label, Icon }) => {
								const isActive = draft.myRole.includes(key as CabinetStageRoleFilter);
								return (
									<button
										key={key}
										type="button"
										className={cn(cls.chip, isActive && cls.chipActiveAccent)}
										onClick={() => {
											setDraft((prev) => ({
												...prev,
												myRole: toggleInArray(prev.myRole, key as CabinetStageRoleFilter),
											}));
										}}
									>
										<Icon size={24} weight="regular" className={cls.chipIcon} />
										<span className={cls.chipLabel}>{label}</span>
									</button>
								);
							})}
						</div>
					</section>

					<section className={cls.section}>
						<p className={cls.sectionTitle}>стадия проверки</p>
						<div className={cls.chipsGrid}>
							{STAGE_INDEXES.map(({ index, label, dotColor }) => {
								const isActive = draft.stageVerification.includes(index);
								return (
									<button
										key={index}
										type="button"
										className={cn(cls.chip, isActive && cls.chipActiveStage)}
										onClick={() => {
											setDraft((prev) => ({
												...prev,
												stageVerification: toggleInArray(prev.stageVerification, index),
											}));
										}}
									>
										<span
											className={cls.stageDot}
											style={{
												background: isActive ? dotColor : 'rgba(34, 43, 51, 0.2)',
											}}
										/>
										<span className={cls.chipLabel}>{label}</span>
									</button>
								);
							})}
						</div>
					</section>

					{/* <section className={cls.section}>
						<p className={cls.sectionTitle}>промежуточный этап</p>
						<div className={cls.chipsGrid}>
							{DOC_STATUS_TOGGLES.map(({ key, label, Icon, activeStyle }) => {
								const isActive = draft.docStatuses.includes(key);

								return (
									<button
										key={key}
										type="button"
										className={cn(cls.chip, isActive && cls.chipActiveIntermediate)}
										onClick={() => {
											setDraft((prev) => ({
												...prev,
												docStatuses: toggleInArray(prev.docStatuses, key),
											}));
										}}
										style={
											isActive
												? ({
														background: activeStyle.bg,
														borderColor: 'rgba(27, 28, 30, 0.15)',
														color: activeStyle.color,
													} as CSSProperties)
												: undefined
										}
									>
										<Icon
											size={20}
											weight="regular"
											className={cls.chipIcon}
											style={{ color: isActive ? activeStyle.color : undefined }}
										/>
										<span className={cls.chipLabel}>{label}</span>
									</button>
								);
							})}
						</div>
					</section> */}

					{/* <section className={cls.section}>
						<p className={cls.sectionTitle}>категория</p>
						<div className={cls.chipsGrid}>
							{CATEGORY_TOGGLES.map(({ key, label, Icon }) => {
								const isActive = draft.categories.includes(key);
								return (
									<button
										key={key}
										type="button"
										className={cn(cls.chip, isActive && cls.chipActiveAccent)}
										onClick={() => {
											setDraft((prev) => ({
												...prev,
												categories: toggleInArray(prev.categories, key),
											}));
										}}
									>
										<Icon size={20} weight="regular" className={cls.chipIcon} />
										<span className={cls.chipLabel}>{label}</span>
									</button>
								);
							})}
						</div>
					</section> */}
				</div>

				<div className={cls.footer}>
					<button
						type="button"
						className={cls.applyBtn}
						onClick={() => onApply(draft)}
					>
						показать {resolvedCountText}
					</button>
					<button
						type="button"
						className={cls.clearBtn}
						onClick={() => {
							const cleared: CabinetStagesFilters = {
								myRole: [],
								stageVerification: [],
								docStatuses: [],
								categories: [],
							};
							setDraft(cleared);
							onApply(cleared);
						}}
					>
						очистить всё
					</button>
				</div>
			</div>
		</div>,
		document.body
	);
};

