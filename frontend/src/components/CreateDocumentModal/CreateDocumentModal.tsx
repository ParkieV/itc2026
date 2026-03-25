import type { FetchBaseQueryError } from '@reduxjs/toolkit/query';
import {
	type ChangeEvent,
	type FC,
	type MouseEvent,
	type ReactElement,
	useCallback,
	useEffect,
	useId,
	useMemo,
	useRef,
	useState,
} from 'react';
import { createPortal } from 'react-dom';
import { useSelector } from 'react-redux';
import { XIcon, PlusIcon, EyeIcon, MagnifyingGlassIcon } from '@phosphor-icons/react';

import { useCreateCabinetDocumentFileMutation } from '@store/api/documents.api';
import type { RootState } from '@store/store';
import type { V1CabinetMeGetResponse } from '@shared/types/api';

import cls from './CreateDocumentModal.module.scss';
import {
	AVATAR_SEARCH_1,
	AVATAR_SEARCH_2,
	AVATAR_SEARCH_3,
	AVATAR_VICTOR_CHIP,
	DOC_PREVIEW_PLACEHOLDER,
	SUCCESS_GLOW,
	SUCCESS_ILLUSTRATION,
} from './assets';

export interface Coauthor {
	id: string;
	/** Числовой id пользователя в бэкенде (поле authors) */
	userId: number;
	name: string;
	email?: string;
	avatarUrl: string;
}

const SEARCH_CANDIDATES: Coauthor[] = [
	{
		id: 'vasilyev-viktor',
		userId: 101,
		name: 'Васильев Виктор',
		email: 'petr@gmail.com',
		avatarUrl: AVATAR_SEARCH_1,
	},
	{
		id: 'vasilyeva-anna',
		userId: 102,
		name: 'Васильева Анна',
		email: 'petr@gmail.com',
		avatarUrl: AVATAR_SEARCH_2,
	},
	{
		id: 'vasilyevtsev',
		userId: 103,
		name: 'Васильевцев Пётр',
		email: 'petr@gmail.com',
		avatarUrl: AVATAR_SEARCH_3,
	},
];

function isFetchBaseQueryError(error: unknown): error is FetchBaseQueryError {
	return typeof error === 'object' && error !== null && 'status' in error;
}

function getUploadErrorMessage(error: unknown): string {
	if (isFetchBaseQueryError(error)) {
		const { data, status } = error;
		if (data && typeof data === 'object' && 'detail' in data) {
			const detail = (data as { detail: unknown }).detail;
			if (typeof detail === 'string' && detail.trim()) {
				return detail;
			}
			if (Array.isArray(detail)) {
				return detail
					.map((item) =>
						item && typeof item === 'object' && 'msg' in item
							? String((item as { msg: unknown }).msg)
							: String(item)
					)
					.join(', ');
			}
		}
		if (status === 400 || status === 403 || status === 404) {
			return 'Не удалось загрузить файл. Проверьте данные и права доступа.';
		}
	}
	return 'Ошибка сети или сервера. Попробуйте ещё раз.';
}

function coauthorFromMe(profile: V1CabinetMeGetResponse): Coauthor {
	return {
		id: `me-${profile.user_id}`,
		userId: profile.user_id,
		name: profile.fio,
		email: profile.login,
		avatarUrl: AVATAR_SEARCH_1,
	};
}

export interface CreateDocumentModalProps {
	isOpen: boolean;
	onClose: () => void;
}

export const CreateDocumentModal: FC<CreateDocumentModalProps> = ({
	isOpen,
	onClose,
}) => {
	const uid = useId();
	const panelRef = useRef<HTMLDivElement>(null);
	const successOkRef = useRef<HTMLButtonElement>(null);
	const searchPopoverRef = useRef<HTMLDivElement>(null);
	const fileInputRef = useRef<HTMLInputElement>(null);
	const objectUrlRef = useRef<string | null>(null);

	const [submitSuccess, setSubmitSuccess] = useState(false);
	const [submitError, setSubmitError] = useState<string | null>(null);
	const [createdDocId, setCreatedDocId] = useState<number | null>(null);
	const [file, setFile] = useState<File | null>(null);
	const [previewUrl, setPreviewUrl] = useState<string | null>(null);
	const [title, setTitle] = useState('');
	const [description, setDescription] = useState('');
	const [coauthors, setCoauthors] = useState<Coauthor[]>([]);
	const [isSearchOpen, setIsSearchOpen] = useState(false);
	const [searchQuery, setSearchQuery] = useState('Васильев');

	const [createCabinetDocumentFile, { isLoading: isUploading }] =
		useCreateCabinetDocumentFileMutation();

	const meProfile = useSelector((s: RootState) => s.user.profile);

	const applyFile = useCallback((f: File): void => {
		if (objectUrlRef.current) {
			URL.revokeObjectURL(objectUrlRef.current);
		}
		const url = URL.createObjectURL(f);
		objectUrlRef.current = url;
		setFile(f);
		setPreviewUrl(url);
	}, []);

	const hasFile = Boolean(file || previewUrl);
	const titleDescFilled =
		Boolean(title.trim()) && Boolean(description.trim());
	const showPreviewShortcut = hasFile;
	const useBodyTypoForFields = titleDescFilled;

	const filteredSearch = useMemo(() => {
		const base = SEARCH_CANDIDATES.filter(
			(c) => c.userId !== meProfile?.user_id
		);
		const q = searchQuery.trim().toLowerCase();
		if (!q) {
			return base;
		}
		return base.filter(
			(c) =>
				c.name.toLowerCase().includes(q) ||
				(c.email?.toLowerCase().includes(q) ?? false)
		);
	}, [searchQuery, meProfile?.user_id]);

	/** Текущий пользователь всегда в списке (и в UI, и в authors), без ожидания эффекта */
	const resolvedCoauthors = useMemo((): Coauthor[] => {
		if (!meProfile) {
			return coauthors;
		}
		if (coauthors.some((c) => c.userId === meProfile.user_id)) {
			return coauthors;
		}
		return [coauthorFromMe(meProfile), ...coauthors];
	}, [meProfile, coauthors]);

	const canSubmit =
		hasFile &&
		titleDescFilled &&
		Boolean(meProfile) &&
		Boolean(file);

	const resetForm = useCallback((): void => {
		setSubmitSuccess(false);
		setSubmitError(null);
		setCreatedDocId(null);
		if (objectUrlRef.current) {
			URL.revokeObjectURL(objectUrlRef.current);
			objectUrlRef.current = null;
		}
		setFile(null);
		setPreviewUrl(null);
		setTitle('');
		setDescription('');
		setCoauthors([]);
		setIsSearchOpen(false);
		setSearchQuery('Васильев');
	}, []);

	useEffect(() => {
		if (!isOpen) {
			resetForm();
		}
	}, [isOpen, resetForm]);

	useEffect(() => {
		if (!isOpen) {
			return;
		}

		const prev = document.body.style.overflow;
		document.body.style.overflow = 'hidden';
		return () => {
			document.body.style.overflow = prev;
		};
	}, [isOpen]);

	useEffect(() => {
		if (!isOpen) {
			return;
		}

		const handleKey = (e: globalThis.KeyboardEvent): void => {
			if (e.key !== 'Escape') {
				return;
			}
			if (isSearchOpen) {
				setIsSearchOpen(false);
				return;
			}
			onClose();
		};

		document.addEventListener('keydown', handleKey);
		return (): void => document.removeEventListener('keydown', handleKey);
	}, [isOpen, isSearchOpen, onClose]);

	useEffect(() => {
		if (!isOpen) {
			return;
		}

		if (submitSuccess) {
			successOkRef.current?.focus();
			return;
		}

		if (!panelRef.current) {
			return;
		}

		const focusable = panelRef.current.querySelector<HTMLElement>(
			'button, [href], input:not([tabindex="-1"]), select, textarea, [tabindex]:not([tabindex="-1"])'
		);
		focusable?.focus();
	}, [isOpen, submitSuccess]);

	useEffect(() => {
		if (!isSearchOpen) {
			return;
		}

		let removeListener: (() => void) | undefined;
		const rafId = window.requestAnimationFrame(() => {
			const onDocMouseDown = (e: globalThis.MouseEvent): void => {
				const el = searchPopoverRef.current;
				if (el && !el.contains(e.target as Node)) {
					setIsSearchOpen(false);
				}
			};

			document.addEventListener('mousedown', onDocMouseDown);
			removeListener = (): void =>
				document.removeEventListener('mousedown', onDocMouseDown);
		});

		return (): void => {
			window.cancelAnimationFrame(rafId);
			removeListener?.();
		};
	}, [isSearchOpen]);

	const onFileInputChange = (e: ChangeEvent<HTMLInputElement>): void => {
		const f = e.target.files?.[0];
		if (f) {
			applyFile(f);
		}
	};

	const openFilePicker = (): void => {
		fileInputRef.current?.click();
	};

	const clearFile = (): void => {
		if (objectUrlRef.current) {
			URL.revokeObjectURL(objectUrlRef.current);
			objectUrlRef.current = null;
		}
		setFile(null);
		setPreviewUrl(null);
		if (fileInputRef.current) {
			fileInputRef.current.value = '';
		}
	};

	const openPreview = (): void => {
		const url = previewUrl;
		if (url) {
			window.open(url, '_blank', 'noopener,noreferrer');
		}
	};

	const onOverlayMouseDown = (e: MouseEvent<HTMLDivElement>): void => {
		if (e.target === e.currentTarget) {
			onClose();
		}
	};

	const onSubmitDocument = async (): Promise<void> => {
		if (!canSubmit || !file) {
			return;
		}
		setSubmitError(null);
		const fd = new FormData();
		fd.append('title', title.trim());
		fd.append('description', description.trim());
		for (const c of resolvedCoauthors) {
			fd.append('authors', String(c.userId));
		}
		fd.append('file', file, file.name);
		try {
			const data = await createCabinetDocumentFile(fd).unwrap();
			setCreatedDocId(data.document_id);
			setSubmitSuccess(true);
		} catch (err) {
			setSubmitError(getUploadErrorMessage(err));
		}
	};

	const onPickCoauthor = (person: Coauthor): void => {
		if (meProfile && person.userId === meProfile.user_id) {
			return;
		}
		setCoauthors((prev) => {
			if (prev.some((c) => c.id === person.id || c.userId === person.userId)) {
				return prev;
			}
		
			const inserted: Coauthor = {
				id: person.id,
				userId: person.userId,
				name: person.name,
				email: person.email ?? 'petr@gmail.com',
				avatarUrl:
					person.id === 'vasilyev-viktor'
						? AVATAR_VICTOR_CHIP
						: person.avatarUrl,
			};
			return [inserted, ...prev].filter(
				(x): x is Coauthor => x != null
			);
		});
		setIsSearchOpen(false);
	};

	if (!isOpen) {
		return null;
	}

	const previewIsImage = file?.type.startsWith('image/') ?? false;

	const renderPreviewContent = (): ReactElement => {
		if (previewUrl && previewIsImage) {
			return (
				<img
					className={cls.thumbImg}
					src={previewUrl}
					alt=""
					width={187}
					height={256}
				/>
			);
		}
		if (previewUrl && file?.type === 'application/pdf') {
			return (
				<iframe
					className={cls.thumbIframe}
					title="предпросмотр"
					src={previewUrl}
				/>
			);
		}
		return (
			<img
				className={cls.thumbImg}
				src={DOC_PREVIEW_PLACEHOLDER}
				alt=""
				width={187}
				height={256}
			/>
		);
	};

	return createPortal(
		<div
			className={cls.overlay}
			role="presentation"
			onMouseDown={onOverlayMouseDown}
		>
			{submitSuccess ? (
				<div
					ref={panelRef}
					className={cls.successPanel}
					role="dialog"
					aria-modal="true"
					aria-labelledby={`${uid}-success-title`}
					onMouseDown={(e) => e.stopPropagation()}
				>
					<button
						type="button"
						className={cls.successClose}
						aria-label="Закрыть"
						onClick={onClose}
					>
						<XIcon size={28} weight="regular" />
					</button>
					<div className={cls.successBody}>
						<div className={cls.successIllustration}>
							<img
								className={cls.successGlow}
								src={SUCCESS_GLOW}
								alt=""
								width={400}
								height={400}
							/>
							<img
								className={cls.successHero}
								src={SUCCESS_ILLUSTRATION}
								alt=""
								width={680}
								height={427}
							/>
						</div>
						<h2
							id={`${uid}-success-title`}
							className={cls.successTitle}
						>
							передано в рассмотрение
						</h2>
						<div className={cls.successDesc}>
							<p>
								Документ успешно загружен и передан на предварительную
								проверку.
								{createdDocId != null ? (
									<>
										{' '}
										<span className={cls.successDocId}>
											(№ {createdDocId})
										</span>
									</>
								) : null}
							</p>
							<p>
								После проверки он будет направлен экспертам для
								рецензирования.
							</p>
						</div>
					</div>
					<button
						ref={successOkRef}
						type="button"
						className={cls.successOkBtn}
						onClick={onClose}
					>
						понятно
					</button>
				</div>
			) : (
				<div
					ref={panelRef}
					className={cls.panel}
					role="dialog"
					aria-modal="true"
					aria-labelledby={`${uid}-modal-title`}
					onMouseDown={(e) => e.stopPropagation()}
				>
					<input
						ref={fileInputRef}
						id={`${uid}-file`}
						type="file"
						className={cls.srOnly}
						accept=".pdf,.doc,.docx,.txt,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
						tabIndex={-1}
						onChange={onFileInputChange}
					/>

					<div className={cls.body}>
					<div className={cls.header}>
						<h2 id={`${uid}-modal-title`} className={cls.title}>
							создать документ
						</h2>
						<button
							type="button"
							className={cls.closeBtn}
							aria-label="Закрыть"
							onClick={onClose}
						>
							<XIcon size={28} weight="regular" />
						</button>
					</div>

					{!hasFile ? (
						<div
							className={cls.dropzone}
							onDragOver={(e) => e.preventDefault()}
							onDrop={(e) => {
								e.preventDefault();
								const f = e.dataTransfer.files?.[0];
								if (f) {
									applyFile(f);
								}
							}}
						>
							<div className={cls.dropzoneInner}>
								<div className={cls.fileIcons} aria-hidden>
									<div className={`${cls.fileCard} ${cls.fileCardPdf}`}>
										<p className={`${cls.fileLabel} ${cls.fileLabelPdf}`}>
											PDF
										</p>
										<div className={cls.fileBars}>
											<div
												className={`${cls.fileBarShort} ${cls.barPdf}`}
											/>
											<div
												className={`${cls.fileBarFull} ${cls.barPdf}`}
											/>
										</div>
									</div>
									<div className={`${cls.fileCard} ${cls.fileCardDoc}`}>
										<p className={`${cls.fileLabel} ${cls.fileLabelDoc}`}>
											DOC
										</p>
										<div className={cls.fileBars}>
											<div
												className={`${cls.fileBarShort} ${cls.barDoc}`}
											/>
											<div
												className={`${cls.fileBarFull} ${cls.barDoc}`}
											/>
										</div>
									</div>
								</div>
								<div className={cls.dropTextBlock}>
									<p className={cls.dropHeading}>
										Перетащи файл или выбери на компьютере
									</p>
									<p className={cls.dropHint}>
										Форматы: PDF, DOC, DOCX, TXT
									</p>
								</div>
							</div>
							<button
								type="button"
								className={cls.pickFileBtn}
								onClick={openFilePicker}
							>
								выбрать файл
							</button>
						</div>
					) : (
						<div
							className={cls.dropzoneFilled}
							onDragOver={(e) => e.preventDefault()}
							onDrop={(e) => {
								e.preventDefault();
								const f = e.dataTransfer.files?.[0];
								if (f) {
									applyFile(f);
								}
							}}
						>
							<div className={cls.previewThumbWrap}>
								<button
									type="button"
									className={cls.removeFileBtn}
									aria-label="Удалить файл"
									onClick={clearFile}
								>
									<XIcon size={16} weight="regular" />
								</button>
								<div className={cls.thumbFrame}>{renderPreviewContent()}</div>
							</div>
							{showPreviewShortcut ? (
								<button
									type="button"
									className={cls.previewShortcutBtn}
									onClick={openPreview}
								>
									<span>предпросмотр</span>
									<EyeIcon size={20} weight="regular" />
								</button>
							) : null}
						</div>
					)}

					<div className={cls.fields}>
						<input
							type="text"
							className={`${cls.field} ${useBodyTypoForFields ? cls.fieldBody : ''}`}
							placeholder="название"
							autoComplete="off"
							value={title}
							onChange={(e) => setTitle(e.target.value)}
						/>
						<textarea
							className={`${cls.field} ${cls.textarea} ${hasFile ? cls.textareaCompact : ''} ${useBodyTypoForFields ? cls.fieldBody : ''}`}
							placeholder="описание документа"
							value={description}
							onChange={(e) => setDescription(e.target.value)}
						/>
						<div className={cls.coauthors}>
							{resolvedCoauthors.map((person) => (
								<div key={person.id} className={cls.coauthorChip}>
									<img
										className={cls.coavatar}
										src={person.avatarUrl}
										alt=""
										width={44}
										height={44}
									/>
									{person.email ? (
										<div className={cls.chipTexts}>
											<p className={cls.coauthorName}>{person.name}</p>
											<p className={cls.chipEmail}>{person.email}</p>
										</div>
									) : (
										<p className={cls.coauthorName}>{person.name}</p>
									)}
								</div>
							))}
							<button
								type="button"
								className={cls.addCoauthorBtn}
								onClick={() => {
									setSearchQuery('Васильев');
									setIsSearchOpen(true);
								}}
							>
								<span className={cls.addCoauthorInner}>
									<span className={cls.addCoauthorLabel}>
										добавить соавтора
									</span>
									<PlusIcon
										className={cls.addCoauthorIcon}
										size={20}
										weight="regular"
									/>
								</span>
							</button>
						</div>
					</div>
				</div>

					{isSearchOpen ? (
						<div
							ref={searchPopoverRef}
							className={cls.searchPopover}
							role="listbox"
							aria-label="Поиск соавтора"
							onMouseDown={(e) => e.stopPropagation()}
						>
							<div className={cls.searchRow}>
								<MagnifyingGlassIcon
									className={cls.searchIcon}
									size={24}
									weight="regular"
								/>
								<input
									className={cls.searchInput}
									value={searchQuery}
									onChange={(e) => setSearchQuery(e.target.value)}
									aria-label="Поиск"
								/>
								<span className={cls.caret} aria-hidden />
							</div>
							<div className={cls.searchResults}>
								{filteredSearch.map((c) => (
									<button
										key={c.id}
										type="button"
										className={cls.searchResult}
										onClick={() => onPickCoauthor(c)}
									>
										<img
											className={cls.coavatar}
											src={c.avatarUrl}
											alt=""
											width={44}
											height={44}
										/>
										<div className={cls.chipTexts}>
											<p className={cls.coauthorName}>{c.name}</p>
											<p className={cls.chipEmail}>{c.email}</p>
										</div>
									</button>
								))}
							</div>
						</div>
					) : null}

					{submitError ? (
						<p className={cls.submitError} role="alert">
							{submitError}
						</p>
					) : null}

					<button
						type="button"
						className={cls.submitBtn}
						disabled={!canSubmit || isUploading}
						onClick={() => void onSubmitDocument()}
					>
						{isUploading ? 'отправка…' : 'передать в рассмотрение'}
					</button>
				</div>
			)}
		</div>,
		document.body
	);
};
