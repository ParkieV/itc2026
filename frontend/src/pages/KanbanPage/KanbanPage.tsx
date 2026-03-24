import { DragEvent, FC, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Avatar } from '@heroui/react';
import cls from './KanbanPage.module.scss';
import { Header } from '@components/Header/Header';
import {
	ArrowCircleUpRightIcon,
	UserCircleIcon,
	CalendarBlankIcon,
	PencilCircleIcon,
} from '@phosphor-icons/react';

type StageId = 'backlog' | 'analysis' | 'development' | 'review' | 'done';

interface Stage {
	id: StageId;
	title: string;
	assignees: string[];
	color: string;
}

interface DocumentTask {
	id: string;
	title: string;
	description: string;
	author: string;
	createdAt: string;
	daysInStage: number;
	documentId: string;
	stageId: StageId;
}

const STAGES: Stage[] = [
	{
		id: 'backlog',
		title: 'предварительная проверка',
		assignees: ['Иван П.', 'Анна С.', 'Иван Н.', 'Анна Н.', 'Иван С.', 'Анна М.'],
		color: '#b08d1a',
	},
	{
		id: 'analysis',
		title: 'рецензирование',
		assignees: ['Олег М.', 'Анна С.'],
		color: '#6e59c8',
	},
	{
		id: 'development',
		title: 'экспертная оценка',
		assignees: ['Никита Т.', 'Иван П.', 'Лена Д.'],
		color: '#3f66cc',
	},
	{
		id: 'review',
		title: 'согласование',
		assignees: ['Мария К.', 'Олег М.'],
		color: '#c48134',
	},
	{
		id: 'done',
		title: 'утвержден',
		assignees: ['Команда'],
		color: '#5f8e44',
	},
];

const INITIAL_TASKS: DocumentTask[] = [
	{
		id: 'doc-1',
		title: 'ТЗ: Модуль согласования договоров',
		description: 'Описание бизнес-процесса и edge-case сценариев согласования.',
		author: 'Анна С.',
		createdAt: '2026-03-20',
		daysInStage: 3,
		documentId: '61285.pdf',
		stageId: 'analysis',
	},
	{
		id: 'doc-2',
		title: 'Спецификация API для комментариев',
		description: 'Контракты REST API и примеры payload для фронтенда.',
		author: 'Иван П.',
		createdAt: '2026-03-18',
		daysInStage: 5,
		documentId: '61285.pdf',
		stageId: 'development',
	},
	{
		id: 'doc-3',
		title: 'Чек-лист приёмочного тестирования',
		description: 'Критерии качества перед релизом фичи документации.',
		author: 'Мария К.',
		createdAt: '2026-03-22',
		daysInStage: 1,
		documentId: '61285.pdf',
		stageId: 'review',
	},
	{
		id: 'doc-4',
		title: 'Release Notes по спринту',
		description: 'Итоговые изменения, фиксы и ограничения релиза.',
		author: 'Олег М.',
		createdAt: '2026-03-14',
		daysInStage: 2,
		documentId: '61285.pdf',
		stageId: 'done',
	},
	{
		id: 'doc-5',
		title: 'План декомпозиции задач',
		description: 'Разбиение epic на stories и оценка по приоритетам.',
		author: 'Лена Д.',
		createdAt: '2026-03-24',
		daysInStage: 0,
		documentId: '61285.pdf',
		stageId: 'backlog',
	},
];

const getInitials = (name: string): string =>
	name
		.split(' ')
		.filter(Boolean)
		.map((part) => part[0])
		.join('')
		.slice(0, 2)
		.toUpperCase();

export const KanbanPage: FC = () => {
	const [tasks, setTasks] = useState<DocumentTask[]>(INITIAL_TASKS);
	const [draggedTaskId, setDraggedTaskId] = useState<string | null>(null);
	const [activeDropStage, setActiveDropStage] = useState<StageId | null>(null);

	const tasksByStage = useMemo(() => {
		const grouped: Record<StageId, DocumentTask[]> = {
			backlog: [],
			analysis: [],
			development: [],
			review: [],
			done: [],
		};
		for (const task of tasks) {
			grouped[task.stageId].push(task);
		}
		return grouped;
	}, [tasks]);

	const onDragStart = (taskId: string) => (): void => {
		setDraggedTaskId(taskId);
	};

	const onDragEnd = (): void => {
		setDraggedTaskId(null);
		setActiveDropStage(null);
	};

	const onDragOverStage =
		(stageId: StageId) =>
		(event: DragEvent<HTMLDivElement>): void => {
			event.preventDefault();
			if (activeDropStage !== stageId) {
				setActiveDropStage(stageId);
			}
		};

	const onDropToStage =
		(stageId: StageId) =>
		(event: DragEvent<HTMLDivElement>): void => {
			event.preventDefault();
			setActiveDropStage(null);
			if (!draggedTaskId) {
				return;
			}

			setTasks((prevTasks) =>
				prevTasks.map((task) => {
					if (task.id !== draggedTaskId) {
						return task;
					}
					if (task.stageId === stageId) {
						return task;
					}
					return {
						...task,
						stageId,
						daysInStage: 0,
					};
				})
			);
		};

	return (
		<div className={cls.page}>
			<Header />

			<div className={cls.board}>
				{STAGES.map((stage) => {
					const stageTasks = tasksByStage[stage.id];
					return (
						<section
							key={stage.id}
							className={`${cls.stage} ${activeDropStage === stage.id ? cls.stageActive : ''}`}
							onDragOver={onDragOverStage(stage.id)}
							onDrop={onDropToStage(stage.id)}
							onDragLeave={() => setActiveDropStage(null)}
						>
							<div className={cls.stageHeader}>
								<div>
									<div className={cls.stageTitleRow}>
										<span
											className={cls.stageDot}
											style={{ backgroundColor: stage.color }}
										/>
										<h2 className={cls.stageTitle}>{stage.title}</h2>
										<span className={cls.stageCount}>{stageTasks.length}</span>
									</div>
								</div>
								<div className={cls.avatarStack}>
									{stage.assignees.slice(0, 4).map((user, index) => (
										<Avatar
											key={user}
											className={`${cls.avatarItem} ${index === 0 ? '' : cls.avatarItemOffset}`}
											style={{ zIndex: stage.assignees.length - index }}
											size="sm"
										>
											<Avatar.Image alt={user} src={user} />
											<Avatar.Fallback>
												{user
													.split(' ')
													.map((n) => n[0])
													.join('')}
											</Avatar.Fallback>
										</Avatar>
									))}
									{stage.assignees.length > 4 && (
										<Avatar
											className={`${cls.avatarItemOffset} w-12`}
											size="sm"
										>
											<Avatar.Fallback className="text-xs justify-end pr-3">
												+{stage.assignees.length - 4}
											</Avatar.Fallback>
										</Avatar>
									)}
								</div>
							</div>

							<div className={cls.taskList}>
								{stageTasks.map((task) => (
									<article
										key={task.id}
										className={`${cls.taskCard} ${draggedTaskId === task.id ? cls.taskDragging : ''}`}
										draggable
										onDragStart={onDragStart(task.id)}
										onDragEnd={onDragEnd}
									>
										<div
											className={cls.taskBadge}
											style={{ backgroundColor: stage.color }}
										>
											{task.daysInStage} дня на этапе
										</div>
										<h3 className={cls.taskTitle}>{task.title}</h3>
										<p className={cls.taskDescription}>{task.description}</p>
										<div className={cls.taskInfoGrid}>
											<span className={cls.taskInfoItem}>
												<span className={cls.taskInfoItemLabel}>
													<UserCircleIcon size={24} />
													Автор:
												</span>{' '}
												{task.author}
											</span>
											<span className={cls.taskInfoItem}>
												<span className={cls.taskInfoItemLabel}>
													Создан:
												</span>{' '}
												{task.createdAt}
											</span>
											<span className={cls.taskInfoItem}>
												<span className={cls.taskInfoItemLabel}>
													Внесено правок:
												</span>{' '}
												{task.daysInStage}
											</span>
										</div>
										<div className={cls.taskDivider} />
										<Link
											className={cls.openButton}
											to={`/pdf/${task.documentId}`}
										>
											<ArrowCircleUpRightIcon color="#1283FA" size={24} />
											открыть документ
										</Link>
									</article>
								))}
							</div>
							<button type="button" className={cls.stageExpandButton}>
								⌄
							</button>
						</section>
					);
				})}
			</div>
		</div>
	);
};
