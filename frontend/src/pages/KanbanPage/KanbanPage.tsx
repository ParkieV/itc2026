import { DragEvent, FC, ReactElement, useCallback, useMemo, useState } from 'react';
import type { FetchBaseQueryError } from '@reduxjs/toolkit/query';
import { Link } from 'react-router-dom';
import { Avatar, toast } from '@heroui/react';
import { useSelector } from 'react-redux';
import cls from './KanbanPage.module.scss';
import { CreateDocumentModal } from '@components/CreateDocumentModal/CreateDocumentModal';
import { CabinetFiltersModal } from '@components/CabinetFiltersModal/CabinetFiltersModal';
import { KanbanDocumentStatusBadge } from '@components/KanbanDocumentStatusBadge/KanbanDocumentStatusBadge';
import { GanttDiagram } from '@components/GanttDiagram/GanttDiagram';
import {
	useDownloadCabinetReviewsPdfMutation,
	useListCabinetStagesQuery,
	useMoveCabinetDocumentMutation,
} from '@store/api/cabinet.api';
import type { RootState } from '@store/store';
import type {
	CabinetStagesFilters,
	DocumentGetResponse,
	V1StageWithReviewerAndDocsGetResponse,
	V1StagesListQueryParams,
} from '@shared/types/api';
import {
	ArrowCircleUpRightIcon,
	UserCircleIcon,
	CalendarBlankIcon,
	PencilLineIcon,
	PlusIcon,
	DownloadSimpleIcon,
	FadersHorizontalIcon,
	SlideshowIcon,
	GradientIcon,
} from '@phosphor-icons/react';

/** Заголовки и цвета колонок как в макете (по индексу с бэка); дальше — title из API. */
const STAGE_COLUMN_META = [
	{ title: 'предварительная проверка', color: '#C1A947' },
	{ title: 'экспертная оценка', color: '#385ABE' },
	{ title: 'согласование', color: '#D28248' },
	{ title: 'утвержден', color: '#449A7D' },
] as const;

const stageColumnDisplay = (
	stageIndex: number,
	apiTitle: string
): { title: string; color: string } => {
	const meta = STAGE_COLUMN_META[stageIndex];
	if (meta) {
		return { title: meta.title, color: meta.color };
	}
	const color = STAGE_COLUMN_META[stageIndex % STAGE_COLUMN_META.length]?.color ?? '#1283FA';
	return { title: apiTitle, color };
};

const formatStageDateLong = (iso: string): string => {
	try {
		return new Date(iso).toLocaleDateString('ru-RU', {
			day: 'numeric',
			month: 'long',
			year: 'numeric',
		});
	} catch {
		return iso;
	}
};

const daysSince = (iso: string): number => {
	const t = new Date(iso).getTime();
	if (Number.isNaN(t)) {
		return 0;
	}
	return Math.max(0, Math.floor((Date.now() - t) / 86_400_000));
};

const daysWordRu = (n: number): string => {
	const m10 = n % 10;
	const m100 = n % 100;
	if (m10 === 1 && m100 !== 11) {
		return 'день';
	}
	if (m10 >= 2 && m10 <= 4 && (m100 < 10 || m100 >= 20)) {
		return 'дня';
	}
	return 'дней';
};

const findDocStageId = (
	columns: V1StageWithReviewerAndDocsGetResponse[],
	docId: number
): number | undefined => {
	for (const col of columns) {
		if (col.docs?.some((d) => d.doc_id === docId)) {
			return col.stage.stage_id;
		}
	}
	return undefined;
};

const getInitials = (name: string): string =>
	name
		.split(' ')
		.filter(Boolean)
		.map((part) => part[0])
		.join('')
		.slice(0, 2)
		.toUpperCase();

const withOpacity = (color: string, opacity: number): string => {
	const normalizedOpacity = Math.max(0, Math.min(1, opacity));
	const alphaHex = Math.round(normalizedOpacity * 255)
		.toString(16)
		.padStart(2, '0');

	if (/^#[\da-f]{6}$/i.test(color)) {
		return `${color}${alphaHex}`;
	}

	if (/^#[\da-f]{3}$/i.test(color)) {
		const r = color[1];
		const g = color[2];
		const b = color[3];
		return `#${r}${r}${g}${g}${b}${b}${alphaHex}`;
	}

	return color;
};

const authorsLabel = (doc: DocumentGetResponse): string =>
	doc.authors?.length ? doc.authors.map((a) => a.fio).join(', ') : '—';

function isFetchBaseQueryError(error: unknown): error is FetchBaseQueryError {
	return typeof error === 'object' && error !== null && 'status' in error;
}

function getMoveDocErrorMessage(error: unknown): string {
	if (isFetchBaseQueryError(error)) {
		const { data, status } = error;
		if (data && typeof data === 'object' && 'detail' in data) {
			const detail = (data as { detail: unknown }).detail;
			if (typeof detail === 'string' && detail.trim()) {
				return detail;
			}
			if (Array.isArray(detail)) {
				return detail
					.map((item) => {
						if (item && typeof item === 'object' && 'msg' in item) {
							return String((item as { msg: unknown }).msg);
						}
						return String(item);
					})
					.join(', ');
			}
		}

		if (status === 400 || status === 403 || status === 404) {
			return 'Некорректный переход. Проверьте права доступа и стадию документа.';
		}
	}

	return 'Ошибка сети или сервера. Попробуйте ещё раз.';
}

const toSafeFileName = (name: string): string =>
	name
		.replace(/[\\/:*?"<>|]/g, '_')
		.replace(/\s+/g, ' ')
		.trim()
		.slice(0, 120);

export const KanbanPage: FC = () => {
	const token = useSelector((s: RootState) => s.auth.token);
	const [moveDoc, { error: moveDocError }] = useMoveCabinetDocumentMutation();
	const [downloadCabinetReviewsPdf, { isLoading: isDownloadingCabinetReviewsPdf }] =
		useDownloadCabinetReviewsPdfMutation();
	const [draggedDocId, setDraggedDocId] = useState<number | null>(null);
	const [activeDropStageId, setActiveDropStageId] = useState<number | null>(null);
	const [isCreateDocOpen, setIsCreateDocOpen] = useState(false);
	const [isFiltersOpen, setIsFiltersOpen] = useState(false);
	const [appliedFilters, setAppliedFilters] = useState<CabinetStagesFilters>({
		myRole: [],
		stageVerification: [],
		docStatuses: [],
		categories: [],
	});

	const [activeTab, setActiveTab] = useState<'kanban' | 'gantt'>('kanban');

	const listStagesQueryParams = useMemo((): V1StagesListQueryParams | undefined => {
		const roles: Array<'author' | 'reviewer'> = [];
		if (
			appliedFilters.myRole.includes('author') ||
			appliedFilters.myRole.includes('coauthor')
		) {
			roles.push('author');
		}
		if (appliedFilters.myRole.includes('reviewer')) {
			roles.push('reviewer');
		}

		const params: V1StagesListQueryParams = {};
		if (roles.length) params.roles = roles;
		if (appliedFilters.docStatuses.length) params.doc_statuses = appliedFilters.docStatuses;
		if (appliedFilters.categories.length) params.categories = appliedFilters.categories;

		return Object.keys(params).length ? params : undefined;
	}, [appliedFilters]);

	const {
		data: stages = [],
		isLoading,
		isError,
	} = useListCabinetStagesQuery(listStagesQueryParams, { skip: !token });

	const stagesForBoardDocsCount = useMemo(() => {
		const allowed = appliedFilters.stageVerification.length
			? new Set(appliedFilters.stageVerification)
			: null;
		let sum = 0;
		for (const [idx, col] of stages.entries()) {
			if (allowed && !allowed.has(idx as 0 | 1 | 2 | 3)) continue;
			sum += col.docs?.length ?? 0;
		}
		return sum;
	}, [appliedFilters.stageVerification, stages]);

	const onDragStart = (docId: number) => (): void => {
		setDraggedDocId(docId);
	};

	const onDragEnd = (): void => {
		setDraggedDocId(null);
		setActiveDropStageId(null);
	};

	const onDragOverStage =
		(stageId: number) =>
		(event: DragEvent<HTMLDivElement>): void => {
			event.preventDefault();
			if (activeDropStageId !== stageId) {
				setActiveDropStageId(stageId);
			}
		};

	const onDropToStage = useCallback(
		(targetStageId: number) =>
			async (event: DragEvent<HTMLDivElement>): Promise<void> => {
				event.preventDefault();
				setActiveDropStageId(null);
				if (draggedDocId == null) {
					return;
				}
				const from = findDocStageId(stages, draggedDocId);
				if (from === targetStageId) {
					setDraggedDocId(null);
					return;
				}
				try {
					await moveDoc({
						doc_id: draggedDocId,
						stage_id: targetStageId,
					}).unwrap();
				} catch (moveDocError) {
					toast('Не удалось переместить документ', {
						variant: 'accent',
						description: getMoveDocErrorMessage(moveDocError),
					});
				} finally {
					setDraggedDocId(null);
				}
			},
		[draggedDocId, moveDoc, stages]
	);

	const boardContent = () => {
		if (!token) {
			return (
				<p className={cls.boardHint}>
					Войдите в аккаунт, чтобы загрузить этапы и документы.
				</p>
			);
		}
		if (isLoading) {
			return <p className={cls.boardHint}>Загрузка этапов…</p>;
		}
		if (isError) {
			return (
				<p className={cls.boardHint}>
					Не удалось загрузить этапы. Попробуйте обновить страницу.
				</p>
			);
		}
		const allowedStageSet = appliedFilters.stageVerification.length
			? new Set(appliedFilters.stageVerification)
			: null;

		const hasVisibleStages = allowedStageSet
			? stages.some((_, idx) => allowedStageSet.has(idx as 0 | 1 | 2 | 3))
			: Boolean(stages.length);

		if (!hasVisibleStages) {
			return <p className={cls.boardHint}>Нет этапов для отображения.</p>;
		}

		return stages
			.map((column, stageIndex) => {
				if (allowedStageSet && !allowedStageSet.has(stageIndex as 0 | 1 | 2 | 3)) {
					return null;
				}

				const stageId = column.stage.stage_id;
				const { title: stageTitle, color } = stageColumnDisplay(
					stageIndex,
					column.stage.title
				);
				const docs = column.docs ?? [];
				const reviewers = column.reviewers ?? [];

				return (
					<section
						key={stageId}
						className={`${cls.stage} ${activeDropStageId === stageId ? cls.stageActive : ''}`}
						onDragOver={onDragOverStage(stageId)}
						onDrop={onDropToStage(stageId)}
						onDragLeave={() => setActiveDropStageId(null)}
					>
						<div className={cls.stageHeader}>
							<div>
								<div className={cls.stageTitleRow}>
									<span
										className={cls.stageDot}
										style={{
											color,
											backgroundColor: color,
										}}
									/>
									<h2 className={cls.stageTitle}>{stageTitle}</h2>
									<span className={cls.stageCount}>{docs.length}</span>
								</div>
							</div>
							<div className={cls.avatarStack}>
								{reviewers.slice(0, 4).map((user, index) => (
									<Avatar
										key={user.user_id}
										className={`${cls.avatarItem} ${index === 0 ? '' : cls.avatarItemOffset}`}
										style={{ zIndex: reviewers.length - index }}
										size="sm"
									>
										<Avatar.Fallback>{getInitials(user.fio)}</Avatar.Fallback>
									</Avatar>
								))}
								{reviewers.length > 4 && (
									<Avatar className={`${cls.avatarItemOffset} w-12`} size="sm">
										<Avatar.Fallback className="text-xs justify-end pr-3">
											+{reviewers.length - 4}
										</Avatar.Fallback>
									</Avatar>
								)}
							</div>
						</div>

						<div className={cls.taskList}>
							{docs.map((doc) => {
								const days = daysSince(doc.modified_at);
								return (
									<article
										key={doc.doc_id}
										className={`${cls.taskCard} ${draggedDocId === doc.doc_id ? cls.taskDragging : ''}`}
										draggable
										onDragStart={onDragStart(doc.doc_id)}
										onDragEnd={onDragEnd}
									>
										<div className={cls.taskCardInner}>
											<div className={cls.taskCardTop}>
												<div className={cls.taskCardBadgesRow}>
													<div
														className={cls.taskBadgeDuration}
														style={{
															backgroundColor: withOpacity(
																color,
																0.1
															),
															color,
														}}
													>
														{days} {daysWordRu(days)} на этапе
													</div>
													<KanbanDocumentStatusBadge
														status={doc.status}
													/>
												</div>
												<h3 className={cls.taskTitle}>{doc.title}</h3>
												<p className={cls.taskDescription}>
													{doc.description}
												</p>
											</div>
											<div className={cls.taskInfoGrid}>
												<div className={cls.taskInfoRow}>
													<span className={cls.taskInfoItemLabel}>
														<UserCircleIcon size={24} />
														автор
													</span>
													<span className={cls.taskInfoValue}>
														{doc.authors.map((user, index) => (
															<Avatar
																key={user.id}
																className={`${cls.avatarItem} ${index === 0 ? '' : cls.avatarItemOffset}`}
																style={{
																	zIndex:
																		reviewers.length - index,
																}}
																size="sm"
															>
																<Avatar.Fallback>
																	{getInitials(user.fio)}
																</Avatar.Fallback>
															</Avatar>
														))}
													</span>
												</div>
												<div className={cls.taskInfoRow}>
													<span className={cls.taskInfoItemLabel}>
														<CalendarBlankIcon size={24} />
														создан
													</span>
													<span className={cls.taskInfoValue}>
														{formatStageDateLong(doc.created_at)}
													</span>
												</div>
												<div className={cls.taskInfoRow}>
													<span className={cls.taskInfoItemLabel}>
														<PencilLineIcon size={24} />
														внесено правок
													</span>
													<span className={cls.taskInfoValue}>
														0{' '}
														<span className={cls.taskInfoValueMuted}>
															(0)
														</span>
													</span>
												</div>
											</div>
										</div>
										<div className={cls.taskDivider} />
										<div className={cls.taskActionsRow}>
											<Link
												className={cls.openButton}
												to={`/pdf/${doc.doc_id}`}
											>
												<ArrowCircleUpRightIcon color="#0b44ff" size={24} />
												открыть документ
											</Link>
											<button
												type="button"
												className={cls.downloadButton}
												disabled={isDownloadingCabinetReviewsPdf}
												onClick={async (e) => {
													e.preventDefault();
													e.stopPropagation();
													try {
														const objectUrl =
															await downloadCabinetReviewsPdf(
																doc.doc_id
															).unwrap();
														const fileName = `${toSafeFileName(doc.title ?? 'сводка') || 'сводка'}.pdf`;
														const a = document.createElement('a');
														a.href = objectUrl;
														a.download = fileName;
														document.body.appendChild(a);
														a.click();
														a.remove();
														window.setTimeout(() => {
															URL.revokeObjectURL(objectUrl);
														}, 10_000);
													} catch (err) {
														toast('Не удалось скачать сводку', {
															variant: 'accent',
															description: 'Попробуйте ещё раз.',
														});
													}
												}}
											>
												<DownloadSimpleIcon size={20} />
												скачать сводку
											</button>
										</div>
									</article>
								);
							})}
						</div>
						<button type="button" className={cls.stageExpandButton}>
							⌄
						</button>
					</section>
				);
			})
			.filter((x): x is ReactElement => x !== null);
	};

	const ganttContent = () => {
		if (!token) {
			return (
				<p className={cls.boardHint}>
					Войдите в аккаунт, чтобы загрузить этапы и документы.
				</p>
			);
		}
		if (isLoading) {
			return <p className={cls.boardHint}>Загрузка этапов…</p>;
		}
		if (isError) {
			return (
				<p className={cls.boardHint}>
					Не удалось загрузить этапы. Попробуйте обновить страницу.
				</p>
			);
		}

		const allowedStageSet = appliedFilters.stageVerification.length
			? new Set(appliedFilters.stageVerification)
			: null;

		const hasVisibleStages = allowedStageSet
			? stages.some((_, idx) => allowedStageSet.has(idx as 0 | 1 | 2 | 3))
			: Boolean(stages.length);

		if (!hasVisibleStages) {
			return <p className={cls.boardHint}>Нет этапов для отображения.</p>;
		}

		return <GanttDiagram stages={stages} allowedStageSet={allowedStageSet} />;
	};

	return (
		<div className={cls.page}>
			<div className={cls.viewTabs}>
				<button
					type="button"
					className={`${cls.viewTab} ${activeTab === 'kanban' ? cls.viewTabActive : ''}`}
					onClick={() => setActiveTab('kanban')}
				>
					<SlideshowIcon size={24}  />
					канбан доска
				</button>
				<button
					type="button"
					className={`${cls.viewTab} ${activeTab === 'gantt' ? cls.viewTabActive : ''}`}
					onClick={() => setActiveTab('gantt')}
				>
					<GradientIcon size={24}/>
					диаграмма ганта
				</button>
			</div>
			{activeTab === 'kanban' ? (
				<div className={cls.board}>{boardContent()}</div>
			) : (
				<div className={cls.ganttBoard}>{ganttContent()}</div>
			)}
			<div className={cls.quickActions}>
				<button
					type="button"
					className={cls.filterBtn}
					onClick={() => setIsFiltersOpen(true)}
				>
					фильтры <FadersHorizontalIcon size={24} />
				</button>
				<button
					type="button"
					className={cls.addDocBtn}
					onClick={() => setIsCreateDocOpen(true)}
				>
					создать новый документ <PlusIcon size={24} />
				</button>
			</div>
			<CreateDocumentModal
				isOpen={isCreateDocOpen}
				onClose={() => setIsCreateDocOpen(false)}
			/>
			<CabinetFiltersModal
				open={isFiltersOpen}
				onClose={() => setIsFiltersOpen(false)}
				onApply={(next) => {
					setAppliedFilters(next);
					setIsFiltersOpen(false);
				}}
				filters={appliedFilters}
				documentsCount={stagesForBoardDocsCount}
			/>
		</div>
	);
};
