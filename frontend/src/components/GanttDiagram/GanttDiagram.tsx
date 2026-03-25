import type { FC } from 'react';
import { useMemo } from 'react';
import cls from './GanttDiagram.module.scss';
import { KanbanDocumentStatusBadge } from '@components/KanbanDocumentStatusBadge/KanbanDocumentStatusBadge';
import type { CabinetStagesStageIndex, V1StageWithReviewerAndDocsGetResponse } from '@shared/types/api';

/** Заголовки и цвета колонок как в Kanban макете (по индексу с бэка). */
const STAGE_COLUMN_META = [
	{ title: 'предварительная проверка', color: '#C1A947' },
	{ title: 'экспертная оценка', color: '#385ABE' },
	{ title: 'согласование', color: '#D28248' },
	{ title: 'утвержден', color: '#449A7D' },
] as const;

const stageColumnDisplay = (stageIndex: number, apiTitle: string): { title: string; color: string } => {
	const meta = STAGE_COLUMN_META[stageIndex];
	if (meta) return { title: meta.title, color: meta.color };
	const fallbackColor = STAGE_COLUMN_META[stageIndex % STAGE_COLUMN_META.length]?.color ?? '#1283FA';
	return { title: apiTitle, color: fallbackColor };
};

const formatDateShort = (iso: string): string => {
	try {
		return new Date(iso).toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' });
	} catch {
		return iso;
	}
};

const formatDateShortTs = (ts: number): string => {
	try {
		return new Date(ts).toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' });
	} catch {
		return String(ts);
	}
};

const formatDateLong = (iso: string): string => {
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

const formatDateLongTs = (ts: number): string => {
	try {
		return new Date(ts).toLocaleDateString('ru-RU', {
			day: 'numeric',
			month: 'long',
			year: 'numeric',
		});
	} catch {
		return String(ts);
	}
};

const toSafeDateTs = (iso: string): number | null => {
	const ts = new Date(iso).getTime();
	return Number.isNaN(ts) ? null : ts;
};

const startOfDay = (ts: number): number => {
	const d = new Date(ts);
	d.setHours(0, 0, 0, 0);
	return d.getTime();
};

const daysBetweenInclusive = (fromDayTs: number, toDayTs: number): number => {
	const msDay = 86_400_000;
	return Math.max(1, Math.floor((toDayTs - fromDayTs) / msDay) + 1);
};

const withOpacity = (color: string, opacity: number): string => {
	const normalizedOpacity = Math.max(0, Math.min(1, opacity));
	const alphaHex = Math.round(normalizedOpacity * 255).toString(16).padStart(2, '0');

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

export interface GanttDiagramProps {
	stages: V1StageWithReviewerAndDocsGetResponse[];
	/** Клиентская фильтрация колонок из UI (индексы 0..3). */
	allowedStageSet: Set<CabinetStagesStageIndex> | null;
}

type TaskRow = {
	docId: number;
	title: string;
	description?: string;
	authors: string[];
	status?: string | null;
	stageIndex: number;
	stageId: number;
	stageTitle: string;
	stageColor: string;
	startIso: string;
	endIso: string;
	startDayTs: number;
	endDayTs: number;
	progressPercent: number;
	dependencies: number[];
};

const hashToSeed = (n: number): number => {
	// Простой детерминированный seed.
	let x = n | 0;
	x = (x ^ 0x6d2b79f5) | 0;
	x = Math.imul(x ^ (x >>> 15), x | 1);
	x ^= x + Math.imul(x ^ (x >>> 7), x | 61);
	return (x ^ (x >>> 14)) >>> 0;
};

const mulberry32 = (seed: number): (() => number) => {
	let a = seed >>> 0;
	return () => {
		a |= 0;
		a = (a + 0x6d2b79f5) | 0;
		let t = Math.imul(a ^ (a >>> 15), 1 | a);
		t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
		return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
	};
};

export const GanttDiagram: FC<GanttDiagramProps> = ({ stages, allowedStageSet }) => {
	const tasks = useMemo<TaskRow[]>(() => {
		const rows: TaskRow[] = [];
		for (const [stageIndex, column] of stages.entries()) {
			if (allowedStageSet && !allowedStageSet.has(stageIndex as CabinetStagesStageIndex)) continue;
			const stageId = column.stage.stage_id;
			const { title: stageTitle, color: stageColor } = stageColumnDisplay(stageIndex, column.stage.title);
			const docs = column.docs ?? [];

			for (const doc of docs) {
				const startTs = toSafeDateTs(doc.created_at) ?? toSafeDateTs(doc.modified_at) ?? Date.now();
				const endTs = toSafeDateTs(doc.modified_at) ?? startTs;

				const startDayTs = startOfDay(Math.min(startTs, endTs));
				const endDayTs = startOfDay(Math.max(startTs, endTs));

				rows.push({
					docId: doc.doc_id,
					title: doc.title,
					description: doc.description,
					authors: doc.authors?.map((a) => a.fio) ?? [],
					status: doc.status ?? null,
					stageIndex,
					stageId,
					stageTitle,
					stageColor,
					startIso: doc.created_at,
					endIso: doc.modified_at,
					startDayTs,
					endDayTs,
					progressPercent: 0, // заполним ниже моковыми данными
					dependencies: [], // заполним ниже моковыми данными
				});
			}
		}
		return rows;
	}, [stages, allowedStageSet]);

	const tasksWithMocks = useMemo<TaskRow[]>(() => {
		const sortedByTimeline = tasks
			.slice()
			.sort((a, b) => a.stageIndex - b.stageIndex || a.startDayTs - b.startDayTs || a.docId - b.docId);

		return sortedByTimeline.map((t, idx) => {
			const seed = hashToSeed(t.docId + t.stageId * 101);
			const rnd = mulberry32(seed);

			// Мок прогресса: плавно растет с временем (чтобы визуально смотрелось логично).
			const timeFactor = sortedByTimeline.length
				? idx / Math.max(1, sortedByTimeline.length - 1)
				: 0;
			const base = 10 + Math.floor(70 * timeFactor);
			const jitter = Math.floor(rnd() * 22) - 8;
			const progressPercent = Math.max(0, Math.min(100, base + jitter));

			// Мок зависимостей: выбираем несколько "предыдущих" документов.
			const depCandidates = sortedByTimeline.slice(0, idx);
			const maxDeps = 3;
			const depCount = Math.min(depCandidates.length, Math.floor(rnd() * (maxDeps + 1)));
			const dependencies: number[] = [];
			for (let d = 0; d < depCount; d++) {
				if (!depCandidates.length) break;
				const pick = depCandidates[Math.floor(rnd() * depCandidates.length)];
				if (pick.docId === t.docId) continue;
				if (dependencies.includes(pick.docId)) continue;
				dependencies.push(pick.docId);
			}

			return {
				...t,
				progressPercent,
				dependencies,
			};
		});
	}, [tasks]);

	const titleById = useMemo(() => {
		const m = new Map<number, string>();
		for (const t of tasksWithMocks) {
			m.set(t.docId, t.title);
		}
		return m;
	}, [tasksWithMocks]);

	const { timeline } = useMemo(() => {
		const msDay = 86_400_000;
		const startCandidates = tasksWithMocks.map((t) => t.startDayTs);
		const endCandidates = tasksWithMocks.map((t) => t.endDayTs);

		const minStart = startCandidates.length ? Math.min(...startCandidates) : null;
		const maxEnd = endCandidates.length ? Math.max(...endCandidates) : null;

		const now = Date.now();
		const fallbackStart = startOfDay(now - 7 * msDay);
		const fallbackEnd = startOfDay(now + 7 * msDay);

		const rawStart = minStart ?? fallbackStart;
		const rawEnd = maxEnd ?? fallbackEnd;

		const paddingDays = 3;
		const paddedStart = rawStart - paddingDays * msDay;
		const paddedEnd = rawEnd + paddingDays * msDay;

		let dayCount = Math.max(7, Math.round((paddedEnd - paddedStart) / msDay) + 1);
		dayCount = Math.min(60, dayCount);

		// Если даты слишком размазаны — сжимаем окно до 60 дней от начала.
		if (dayCount === 60) {
			const maxEndAllowed = paddedStart + (dayCount - 1) * msDay;
			return {
				timeline: {
					startDayTs: paddedStart,
					endDayTs: maxEndAllowed,
					dayCount,
				},
			};
		}

		return {
			timeline: {
				startDayTs: paddedStart,
				endDayTs: paddedEnd,
				dayCount,
			},
		};
	}, [tasksWithMocks]);

	const CELL_PX = 16;
	const MIN_BAR_PX = 56;
	const timelineWidthPx = timeline.dayCount * CELL_PX;

	const ticks = useMemo(() => {
		const result: Array<{ dayIdx: number; label: string }> = [];
		for (let i = 0; i < timeline.dayCount; i++) {
			if (i === 0 || i === timeline.dayCount - 1 || i % 7 === 0) {
				const dayTs = timeline.startDayTs + i * 86_400_000;
				result.push({ dayIdx: i, label: formatDateShortTs(dayTs) });
			}
		}
		return result;
	}, [timeline.dayCount, timeline.startDayTs]);

	const todayIdx = useMemo(() => {
		const msDay = 86_400_000;
		const todayDayTs = startOfDay(Date.now());
		const delta = Math.floor((todayDayTs - timeline.startDayTs) / msDay);
		return delta >= 0 && delta < timeline.dayCount ? delta : null;
	}, [timeline.dayCount, timeline.startDayTs]);

	if (!tasksWithMocks.length) {
		return <p className={cls.ganttHint}>Нет документов для диаграммы Ганта.</p>;
	}

	return (
		<div className={cls.wrapper}>
			<div className={cls.ganttHeader}>
				<div className={cls.ganttHeaderLeft}>
					<h2 className={cls.ganttTitle}>Диаграмма Ганта</h2>
					<div className={cls.ganttRange}>
						{formatDateLongTs(timeline.startDayTs)} - {formatDateLongTs(timeline.endDayTs)}
					</div>
					<div className={cls.ganttLegend}>
						{STAGE_COLUMN_META.map((m, idx) => (
							<span key={m.title} className={cls.legendItem} title={m.title}>
								<span className={cls.legendDot} style={{ backgroundColor: m.color }} />
								<span className={cls.legendLabel}>{m.title}</span>
							</span>
						))}
					</div>
				</div>

				<div className={cls.ganttHeaderTimeline} style={{ width: timelineWidthPx }}>
					<div
						className={cls.ganttHeaderGrid}
						style={{
							backgroundImage:
								'linear-gradient(to right, rgba(34, 43, 51, 0.08) 1px, transparent 1px)',
							backgroundSize: `${CELL_PX}px 100%`,
						}}
					/>
					{ticks.map((t) => (
						<div
							key={t.dayIdx}
							className={cls.ganttTick}
							style={{ left: t.dayIdx * CELL_PX }}
						>
							<span className={cls.ganttTickLabel}>{t.label}</span>
						</div>
					))}
					{todayIdx !== null && (
						<div className={cls.todayLine} style={{ left: todayIdx * CELL_PX }} />
					)}
				</div>
			</div>

			<div className={cls.ganttScroll}>
				<div className={cls.ganttBody} style={{ minWidth: timelineWidthPx + 420 }}>
					{tasksWithMocks
						.slice()
						.sort((a, b) => a.stageIndex - b.stageIndex)
						.map((t) => {
							const msDay = 86_400_000;
							const startIdx = Math.floor((t.startDayTs - timeline.startDayTs) / msDay);
							const endIdxInclusive = Math.floor((t.endDayTs - timeline.startDayTs) / msDay);

							const clampedStartIdx = Math.max(0, Math.min(timeline.dayCount - 1, startIdx));
							const clampedEndExclusive = Math.max(
								clampedStartIdx + 1,
								Math.min(timeline.dayCount, endIdxInclusive + 1)
							);
							let widthPx = (clampedEndExclusive - clampedStartIdx) * CELL_PX;

							const leftPx = clampedStartIdx * CELL_PX;
							if (widthPx < MIN_BAR_PX) {
								widthPx = Math.min(MIN_BAR_PX, timelineWidthPx - leftPx);
							}

							const durationDays = daysBetweenInclusive(t.startDayTs, t.endDayTs);

							return (
								<div key={t.docId} className={cls.ganttRow}>
									<div className={cls.ganttLeft}>
										<h3 className={cls.ganttTaskTitle} title={t.title}>
											{t.title}
										</h3>
										<div className={cls.ganttMetaRow}>
											<span className={cls.ganttStageMeta} title={t.stageTitle}>
												<span
													className={cls.stageDot}
													style={{ backgroundColor: t.stageColor }}
												/>
												{t.stageTitle}
											</span>
											<span className={cls.ganttDuration}>
												{durationDays} дн.
											</span>
										</div>
										<div className={cls.ganttBadgesRow}>
											<KanbanDocumentStatusBadge status={t.status} />
										</div>
										<div className={cls.ganttSmall}>
											<span className={cls.ganttSmallLabel}>создан:</span>{' '}
											{formatDateShort(t.startIso)}; <span className={cls.ganttSmallLabel}>обновлён:</span>{' '}
											{formatDateShort(t.endIso)}
										</div>
										<div className={cls.ganttSmallMuted}>
											авторы: {t.authors.length ? t.authors.join(', ') : '—'}
										</div>
										<div className={cls.ganttSmallMuted}>
											зависимости:{' '}
											{t.dependencies.length
												? t.dependencies
													.map((id) => {
														return titleById.get(id) ?? String(id);
													})
													.join(', ')
												: '—'}
										</div>
										<div className={cls.ganttSmallMuted}>
											прогресс: {t.progressPercent}%
										</div>
									</div>

									<div className={cls.ganttLane} style={{ width: timelineWidthPx }}>
										<div
											className={cls.ganttBar}
											style={{
												left: leftPx,
												width: widthPx,
												backgroundColor: withOpacity(t.stageColor, 0.18),
												borderColor: withOpacity(t.stageColor, 0.65),
											}}
											title={[
												`t: ${t.title}`,
												`этап: ${t.stageTitle}`,
												`период: ${formatDateLong(t.startIso)} - ${formatDateLong(t.endIso)}`,
												t.description ? `описание: ${t.description}` : undefined,
											]
												.filter(Boolean)
												.join('\n')}
										>
											<span className={cls.ganttBarInner} style={{ backgroundColor: t.stageColor }} />
										</div>
									</div>
								</div>
							);
						})}
				</div>
			</div>
		</div>
	);
};

