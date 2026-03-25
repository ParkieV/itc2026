/* eslint-disable @typescript-eslint/no-explicit-any */
import { FC, useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import WebViewer from '@pdftron/webviewer';

import type {
	CommentStatus,
	ReviewStatus,
	V1CabinetDocumentCommentResponse,
	V1CabinetDocumentGetDocumentResponse,
	V1CabinetMeGetResponse,
} from '@shared/types/api';

import { cabinetApi, useSetCabinetReviewStatusMutation } from '@store/api/cabinet.api';
import { store } from '@store/store';

import { ExpertNoteModal } from './ExpertNoteModal';
import {
	EXPERT_NOTE_CUSTOM_KEY,
	ExpertNoteFields,
	SERVER_COMMENT_ID_KEY,
	formatExpertNoteBody,
	parseExpertNoteFieldsFromAnnotation,
} from './expertNoteFormat';
import cls from './PdfViewerPage.module.scss';

type ViewerHandle = Awaited<ReturnType<typeof WebViewer>>;

export type ViewerRole = 'expert' | 'developer';

/** Статусы комментария в WebViewer (PDF review): только Accepted, Rejected (= declined), None. */
const ALLOWED_ANNOTATION_REVIEW_STATES = new Set(['', 'None', 'Accepted', 'Rejected']);

const NOTE_STATE_FLYOUT_OPTIONS_TO_DISABLE = [
	'noteStateFlyoutCancelledOption',
	'noteStateFlyoutCompletedOption',
	'noteStateFlyoutMarkedOption',
	'noteStateFlyoutUnmarkedOption',
] as const;

interface ExpertModalState {
	annotId: string;
	initial: ExpertNoteFields;
}

export const PdfViewerPage: FC = () => {
	const { documentId: routeDocumentId } = useParams<{ documentId: string }>();

	const docIdNum =
		routeDocumentId != null && routeDocumentId !== ''
			? Number.parseInt(routeDocumentId, 10)
			: Number.NaN;
	const isValidDocId = Number.isFinite(docIdNum) && docIdNum > 0;

	const cabinetStageIdRef = useRef<number | null>(null);
	const lastSyncedStatusRef = useRef<Map<number, CommentStatus>>(new Map());
	const pendingDeveloperReplyPostsRef = useRef<Set<string>>(new Set());

	const viewerRef = useRef<HTMLDivElement | null>(null);
	const instanceRef = useRef<ViewerHandle | null>(null);
	const expertDraftAnnotIdRef = useRef<string | null>(null);
	const viewerRoleRef = useRef<ViewerRole>('expert');

	const [expertModal, setExpertModal] = useState<ExpertModalState | null>(null);
	const [loadError, setLoadError] = useState<string | null>(null);
	const [viewerRole, setViewerRole] = useState<ViewerRole | null>(null);
	const [docMeta, setDocMeta] = useState<V1CabinetDocumentGetDocumentResponse | null>(null);
	const [meProfile, setMeProfile] = useState<V1CabinetMeGetResponse | null>(null);
	const [myReviewStatus, setMyReviewStatus] = useState<ReviewStatus | null>(null);

	const [setCabinetReviewStatus, { isLoading: isReviewStatusLoading }] =
		useSetCabinetReviewStatusMutation();

	useEffect(() => {
		document.documentElement.classList.add('pdf-viewer-route');
		return () => {
			document.documentElement.classList.remove('pdf-viewer-route');
		};
	}, []);

	const formatDate = (v: unknown): string => {
		if (v === null || v === undefined) {
			return '—';
		}
		let ms: number | null = null;
		if (typeof v === 'number' && Number.isFinite(v)) {
			// Heuristic: seconds vs ms
			ms = v > 1e12 ? v : v * 1000;
		} else if (typeof v === 'string') {
			const n = Number(v);
			if (Number.isFinite(n) && v.trim().length > 0) {
				ms = n > 1e12 ? n : n * 1000;
			} else {
				const d = new Date(v);
				if (!Number.isNaN(d.getTime())) {
					return d.toLocaleDateString('ru-RU');
				}
			}
		}
		if (ms === null) {
			return '—';
		}
		const d = new Date(ms);
		if (Number.isNaN(d.getTime())) {
			return '—';
		}
		return d.toLocaleDateString('ru-RU');
	};

	useEffect(() => {
		if (!isValidDocId || !viewerRef.current) {
			return;
		}
		let mounted = true;
		let persistDebounce: ReturnType<typeof setTimeout> | null = null;
		let removeVisibility: (() => void) | null = null;
		let pdfObjectUrl: string | null = null;

		setLoadError(null);
		setViewerRole(null);
		setDocMeta(null);
		setMeProfile(null);
		setMyReviewStatus(null);

		const setup = async (): Promise<void> => {
			let pdfUrl: string;
			let serverComments: V1CabinetDocumentCommentResponse[];
			let resolvedViewerRole: ViewerRole;
			try {
				const [pdf, cabinetDoc, me] = await Promise.all([
					store
						.dispatch(
							cabinetApi.endpoints.getCabinetDocumentPdf.initiate(docIdNum, {
								forceRefetch: true,
							})
						)
						.unwrap(),
					store
						.dispatch(cabinetApi.endpoints.getCabinetDocument.initiate(docIdNum))
						.unwrap(),
					store.dispatch(cabinetApi.endpoints.getCabinetMe.initiate()).unwrap(),
				]);
				pdfUrl = pdf;
				cabinetStageIdRef.current = cabinetDoc.document.stage_id;
				serverComments = cabinetDoc.comments ?? [];
				if (mounted) {
					setDocMeta(cabinetDoc.document);
					setMeProfile(me);
					const myReview =
						cabinetDoc.reviews?.find((r) => r.user_id === me.user_id) ?? null;
					setMyReviewStatus(myReview?.status ?? null);
				}
				resolvedViewerRole = cabinetDoc.document.authors.includes(me.user_id)
					? 'developer'
					: 'expert';
				viewerRoleRef.current = resolvedViewerRole;
				if (mounted) {
					setViewerRole(resolvedViewerRole);
				}

				// Эксперт при входе на страницу документа должен отметить review как "просмотренный".
				if (resolvedViewerRole === 'expert') {
					try {
						await store
							.dispatch(
								cabinetApi.endpoints.viewCabinetReviews.initiate({
									docId: docIdNum,
									stageId: cabinetDoc.document.stage_id,
								})
							)
							.unwrap();
					} catch {
						// Не блокируем открытие просмотрщика при проблемах с отметкой просмотра.
					}
				}
			} catch {
				if (mounted) {
					setLoadError(
						'Не удалось загрузить документ с сервера. Проверьте сеть и доступ.'
					);
				}
				return;
			}

			if (!mounted) {
				return;
			}

			pdfObjectUrl = pdfUrl;
			if (!mounted) {
				URL.revokeObjectURL(pdfObjectUrl);
				pdfObjectUrl = null;
				return;
			}

			try {
				const instance = await WebViewer(
					{
						path: '/webviewer',
						css: '/pdf-webviewer-custom.css',
					},
					viewerRef.current as HTMLDivElement
				);
				if (!mounted) {
					URL.revokeObjectURL(pdfObjectUrl);
					pdfObjectUrl = null;
					return;
				}
				instanceRef.current = instance;
				const ui = instance.UI as any;
				const core = instance.Core as any;
				const { documentViewer } = core;
				const annotManager = documentViewer.getAnnotationManager();

				const deleteAnnotationById = (id: string): void => {
					const target = annotManager
						.getAnnotationsList()
						.find((a: any) => String(a.Id) === id);
					if (!target) {
						return;
					}
					annotManager.deleteAnnotations([target], { force: true });
				};

				const setTextSelectMode = (): void => {
					const textSelectTool =
						documentViewer.getTool('TextSelect') ??
						documentViewer.getToolModeMap()?.TextSelect;
					if (textSelectTool) {
						documentViewer.setToolMode(textSelectTool);
					}
				};

				const setDefaultToolForRole = (): void => {
					if (resolvedViewerRole === 'developer') {
						const panTool =
							documentViewer.getTool('Pan') ?? documentViewer.getToolModeMap()?.Pan;
						if (panTool) {
							documentViewer.setToolMode(panTool);
						}
						return;
					}
					setTextSelectMode();
				};

				await ui.setLanguage('ru');
				if (resolvedViewerRole === 'expert') {
					ui.enableFeatures([ui.Feature.TextSelection]);
				} else {
					ui.disableFeatures([ui.Feature.TextSelection]);
				}

				if (
					resolvedViewerRole === 'expert' &&
					typeof ui.disableReplyForAnnotations === 'function'
				) {
					ui.disableReplyForAnnotations(() => true);
				}

				// Keep only text selection/comment flow in custom right panel.
				ui.disableElements([
					'selectToolButton',
					'toolbarGroup-Insert',
					'toolbarGroup-Shapes',
					'toolbarGroup-Edit',
					'toolbarGroup-Forms',
					'toolbarGroup-Measure',
					'toolbarGroup-FillAndSign',
					'shapeToolsButton',
					'freeTextToolGroupButton',
					'signatureToolGroupButton',
					'eraserToolButton',
					'freeHandToolGroupButton',
					'settingsButton',
					'underlineToolGroupButton',
					'squigglyToolGroupButton',
					'strikeoutToolGroupButton',
					'linkButton',
					...NOTE_STATE_FLYOUT_OPTIONS_TO_DISABLE,
				]);
				ui.disableTools([
					'AnnotationCreateRectangle',
					'AnnotationCreateEllipse',
					'AnnotationCreateLine',
					'AnnotationCreateArrow',
					'AnnotationCreatePolygon',
					'AnnotationCreatePolyline',
					'AnnotationCreateFreeText',
					'AnnotationCreateSticky',
					'AnnotationCreateStamp',
					'AnnotationCreateFreeHand',
					'AnnotationCreateCallout',
					'AnnotationCreateSignature',
					'AnnotationCreateTextUnderline',
					'AnnotationCreateTextSquiggly',
					'AnnotationCreateTextStrikeout',
					'AnnotationCreateLink',
				]);
				ui.openElements(['notesPanel']);
				setDefaultToolForRole();

				const isAllowedPdfReviewState = (stateRaw: string): boolean => {
					const t = stateRaw.trim().toLowerCase();
					return (
						t === '' ||
						t === 'none' ||
						t === 'accepted' ||
						t === 'rejected' ||
						ALLOWED_ANNOTATION_REVIEW_STATES.has(stateRaw.trim())
					);
				};

				const normalizeAnnotReviewState = (annot: any): void => {
					const stateRaw =
						typeof annot?.getState === 'function'
							? String(annot.getState() ?? '').trim()
							: String(annot?.State ?? '').trim();
					const modelRaw =
						typeof annot?.getStateModel === 'function'
							? String(annot.getStateModel() ?? '').trim()
							: String(annot?.StateModel ?? '').trim();
					try {
						if (modelRaw === 'Marked') {
							if (typeof annot.setStateModel === 'function') {
								annot.setStateModel('Review');
							}
							annotManager.updateAnnotationState(annot, 'None');
							return;
						}
						if (stateRaw && !isAllowedPdfReviewState(stateRaw)) {
							annotManager.updateAnnotationState(annot, 'None');
						}
					} catch {
						// игнорируем типы аннотаций без review state
					}
				};

				const getAnnotContents = (annot: any): string => {
					if (typeof annot?.getContents === 'function') {
						return String(annot.getContents() ?? '');
					}
					return String(annot?.Contents ?? '');
				};

				const getAnnotStatus = (annot: any): string => {
					if (typeof annot?.getState === 'function') {
						const state = String(annot.getState() ?? '').trim();
						if (state) {
							return state;
						}
					}
					const fromProp = String(annot?.State ?? '').trim();
					if (fromProp) {
						return fromProp;
					}
					if (typeof annot?.getStatus === 'function') {
						return String(annot.getStatus() ?? '');
					}
					return String(annot?.Status ?? '');
				};

				const persistWebViewerData = async (): Promise<void> => {
					try {
						// дублируем синк статуса: часть сценариев WebViewer не даёт полный список в modify
						syncCommentStatusToServer(annotManager.getAnnotationsList());

						// Developer: при ответе на комментарий отправляем POST с `developer_response` и обязательным `reply_to`.
						if (viewerRoleRef.current === 'developer') {
							const all = annotManager.getAnnotationsList();
							for (const annot of all) {
								if (!isReplyAnnotation(annot)) {
									continue;
								}
								if (annot.getCustomData?.(SERVER_COMMENT_ID_KEY)) {
									continue;
								}
								const responseText = getAnnotContents(annot).trim();
								if (!responseText) {
									continue;
								}
								const parentAnnotIdRaw = annot?.InReplyTo;
								if (!parentAnnotIdRaw) {
									continue;
								}
								const parentAnnot = all.find(
									(a: any) => String(a.Id) === String(parentAnnotIdRaw)
								);
								const parentCommentIdRaw =
									parentAnnot?.getCustomData?.(SERVER_COMMENT_ID_KEY);
								if (!parentCommentIdRaw) {
									continue;
								}
								const replyToCommentId = Number.parseInt(
									String(parentCommentIdRaw),
									10
								);
								if (!Number.isFinite(replyToCommentId)) {
									continue;
								}

								const annotKey = String(annot.Id);
								if (pendingDeveloperReplyPostsRef.current.has(annotKey)) {
									continue;
								}
								pendingDeveloperReplyPostsRef.current.add(annotKey);

								const stageId = cabinetStageIdRef.current;
								if (!stageId) {
									pendingDeveloperReplyPostsRef.current.delete(annotKey);
									continue;
								}
								try {
									const xfdf = await annotManager.exportAnnotations({
										annotList: [annot],
										links: false,
										widgets: false,
										fields: false,
									});
									await store
										.dispatch(
											cabinetApi.endpoints.createCabinetDocumentComment.initiate(
												{
													docId: docIdNum,
													body: {
														stage_id: stageId,
														developer_response: responseText,
														reply_to: replyToCommentId,
														xfdf,
													},
												}
											)
										)
										.unwrap();

									const refreshed = await store
										.dispatch(
											cabinetApi.endpoints.getCabinetDocument.initiate(
												docIdNum,
												{
													forceRefetch: true,
												}
											)
										)
										.unwrap();

									const xfdfNorm = xfdf.trim();
									const match = refreshed.comments.find(
										(c) => c.xfdf.trim() === xfdfNorm
									);
									if (match) {
										try {
											annot.setCustomData(
												SERVER_COMMENT_ID_KEY,
												String(match.comment_id)
											);
											if (
												typeof match.author?.fio === 'string' &&
												match.author.fio.trim().length > 0
											) {
												annot.Author = match.author.fio.trim();
											}
											annotManager.updateAnnotation(annot);
										} catch {
											// ignore
										}
										if (match.status === 'accepted') {
											lastSyncedStatusRef.current.set(
												match.comment_id,
												'accepted'
											);
										} else if (match.status === 'declined') {
											lastSyncedStatusRef.current.set(
												match.comment_id,
												'declined'
											);
										}
									}
								} catch {
									// ignore network errors; next persist attempt can retry
								} finally {
									pendingDeveloperReplyPostsRef.current.delete(annotKey);
								}
							}
						}
					} catch {
						// не ломаем просмотр из-за ошибок синка
					}
				};

				const schedulePersist = (): void => {
					if (persistDebounce !== null) {
						clearTimeout(persistDebounce);
					}
					persistDebounce = setTimeout(() => {
						persistDebounce = null;
						void persistWebViewerData();
					}, 350);
				};

				const isReplyAnnotation = (annot: any): boolean => {
					if (annot?.InReplyTo) {
						return true;
					}
					if (typeof annot?.isReply === 'function') {
						return annot.isReply();
					}
					return false;
				};

				const openExpertDraft = (annot: any): void => {
					if (!mounted || resolvedViewerRole !== 'expert') {
						return;
					}
					const id = String(annot.Id);
					const prevId = expertDraftAnnotIdRef.current;
					if (prevId && prevId !== id) {
						deleteAnnotationById(prevId);
					}
					expertDraftAnnotIdRef.current = id;
					const initial = parseExpertNoteFieldsFromAnnotation(annot);
					setExpertModal({ annotId: id, initial });
					void ui.closeElements(['notesPanel']);
				};

				const mapPdfReviewStateToApiStatus = (annot: any): CommentStatus | null => {
					const st = getAnnotStatus(annot).trim().toLowerCase();
					if (st === 'accepted') {
						return 'accepted';
					}
					if (st === 'rejected') {
						return 'declined';
					}
					return null;
				};

				const syncCommentStatusToServer = (annotations: any[]): void => {
					for (const annot of annotations) {
						const idRaw =
							typeof annot?.getCustomData === 'function'
								? annot.getCustomData(SERVER_COMMENT_ID_KEY)
								: undefined;
						if (!idRaw) {
							continue;
						}
						const commentId = Number.parseInt(String(idRaw), 10);
						if (!Number.isFinite(commentId)) {
							continue;
						}
						const apiStatus = mapPdfReviewStateToApiStatus(annot);
						if (!apiStatus) {
							continue;
						}
						if (lastSyncedStatusRef.current.get(commentId) === apiStatus) {
							continue;
						}
						void store
							.dispatch(
								cabinetApi.endpoints.patchCabinetDocumentComment.initiate({
									docId: docIdNum,
									commentId,
									body: { status: apiStatus },
								})
							)
							.unwrap()
							.then(() => {
								lastSyncedStatusRef.current.set(commentId, apiStatus);
							})
							.catch(() => {
								// оставляем без уведомления — повторит при следующем изменении
							});
					}
				};

				documentViewer.addEventListener('documentLoaded', async () => {
					const existingAnnotations = annotManager.getAnnotationsList();
					if (existingAnnotations.length > 0) {
						annotManager.deleteAnnotations(existingAnnotations, {
							imported: true,
							force: true,
						});
					}
					lastSyncedStatusRef.current = new Map();

					const serverWithXfdf = serverComments.filter(
						(c) => typeof c.xfdf === 'string' && c.xfdf.trim().length > 0
					);

					for (const c of serverWithXfdf) {
						const beforeIds = new Set(
							annotManager.getAnnotationsList().map((a: any) => String(a.Id))
						);
						try {
							await annotManager.importAnnotations(c.xfdf);
						} catch {
							continue;
						}
						const added = annotManager
							.getAnnotationsList()
							.filter((a: any) => !beforeIds.has(String(a.Id)));
						for (const a of added) {
							try {
								a.setCustomData(SERVER_COMMENT_ID_KEY, String(c.comment_id));

								// Чтобы в панели комментариев WebViewer отображал автора, а не "Guest".
								if (
									typeof c.author?.fio === 'string' &&
									c.author.fio.trim().length > 0
								) {
									a.Author = c.author.fio.trim();
								}
							} catch {
								// ignore
							}
							try {
								annotManager.updateAnnotation(a);
							} catch {
								// ignore
							}
							if (c.status === 'accepted') {
								lastSyncedStatusRef.current.set(c.comment_id, 'accepted');
							} else if (c.status === 'declined') {
								lastSyncedStatusRef.current.set(c.comment_id, 'declined');
							}
						}
					}
					for (const annot of annotManager.getAnnotationsList()) {
						normalizeAnnotReviewState(annot);
					}
					setDefaultToolForRole();
					await persistWebViewerData();
				});

				annotManager.addEventListener(
					'annotationChanged',
					(annotations: any[], action: string, info?: { imported?: boolean }) => {
						if (info?.imported) {
							return;
						}
						const act = String(action).toLowerCase();
						if (act === 'modify') {
							for (const annot of annotations) {
								normalizeAnnotReviewState(annot);
							}
							// WebViewer часто передаёт пустой/усечённый список при смене статуса из панели (в т.ч. role=developer)
							syncCommentStatusToServer(annotManager.getAnnotationsList());
						}
						const isAdd = act === 'add';

						if (isAdd) {
							let hadNonReply = false;
							for (const annot of annotations) {
								if (isReplyAnnotation(annot)) {
									continue;
								}
								hadNonReply = true;
								if (resolvedViewerRole === 'developer') {
									annotManager.deleteAnnotations([annot], { force: true });
								} else if (resolvedViewerRole === 'expert') {
									openExpertDraft(annot);
								}
							}
							// Не пишем XFDF с «голой» подсветкой (эксперт до модалки / разработчик — снятие чужого add)
							if (
								hadNonReply &&
								(resolvedViewerRole === 'expert' ||
									resolvedViewerRole === 'developer')
							) {
								return;
							}
						}

						schedulePersist();
					}
				);

				const flushOnHide = (): void => {
					if (document.visibilityState === 'hidden') {
						if (persistDebounce !== null) {
							clearTimeout(persistDebounce);
							persistDebounce = null;
						}
						void persistWebViewerData();
					}
				};
				document.addEventListener('visibilitychange', flushOnHide);
				removeVisibility = () => {
					document.removeEventListener('visibilitychange', flushOnHide);
				};

				await ui.loadDocument(pdfObjectUrl, {
					extension: 'pdf',
					loadAnnotations: false,
				});
			} catch {
				if (pdfObjectUrl) {
					URL.revokeObjectURL(pdfObjectUrl);
					pdfObjectUrl = null;
				}
				if (mounted) {
					setLoadError('Не удалось открыть PDF в просмотрщике.');
				}
			}
		};

		void setup();

		return () => {
			mounted = false;
			cabinetStageIdRef.current = null;
			viewerRoleRef.current = 'expert';
			setExpertModal(null);
			expertDraftAnnotIdRef.current = null;
			if (persistDebounce !== null) {
				clearTimeout(persistDebounce);
				persistDebounce = null;
			}
			removeVisibility?.();
			instanceRef.current = null;
			if (pdfObjectUrl) {
				URL.revokeObjectURL(pdfObjectUrl);
				pdfObjectUrl = null;
			}
		};
	}, [isValidDocId, docIdNum]);

	if (!isValidDocId) {
		return (
			<div className={cls.layout}>
				<p className={cls.errorMessage}>Некорректный идентификатор документа.</p>
			</div>
		);
	}

	if (loadError) {
		return (
			<div className={cls.layout}>
				<p className={cls.errorMessage}>{loadError}</p>
			</div>
		);
	}

	const handleReviewDecision = async (status: ReviewStatus): Promise<void> => {
		if (!docMeta) {
			console.log('docMeta not found');
			return;
		}
		// Кнопки approve/decline по макету доступны автору (viewerRole=developer).
		if (viewerRole === 'developer') {
			console.log('viewerRole not developer');
			return;
		}
		if (isReviewStatusLoading) {
			console.log('isReviewStatusLoading');
			return;
		}
		try {
			await setCabinetReviewStatus({
				docId: docIdNum,
				stageId: docMeta.stage_id,
				status,
			}).unwrap();
			setMyReviewStatus(status);
		} catch {
			// Ошибки не прерываем: пользователь может попробовать ещё раз.
		}
	};

	const handleReturnToReview = async (): Promise<void> => {
		if (!docMeta) {
			return;
		}

		// Оптимистично возвращаем UI в исходное состояние.
		setMyReviewStatus(null);

		try {
			// В контракте `status` типа `ReviewStatus`, но на бэке возврат к рассмотрению
			// может поддерживаться через `null`. Если бэк не примет — просто оставим UI-выбор.
			await store
				.dispatch(
					cabinetApi.endpoints.setCabinetReviewStatus.initiate({
						docId: docIdNum,
						stageId: docMeta.stage_id,
						status: null as unknown as ReviewStatus,
					}) as any
				)
				.unwrap();

			const refreshed = await store
				.dispatch(
					cabinetApi.endpoints.getCabinetDocument.initiate(docIdNum, {
						forceRefetch: true,
					})
				)
				.unwrap();

			if (meProfile?.user_id != null) {
				const nextMyReview =
					refreshed.reviews?.find((r) => r.user_id === meProfile.user_id) ?? null;
				setMyReviewStatus(nextMyReview?.status ?? null);
			}
		} catch {
			// не ломаем UI
		}
	};

	const syncNewExpertCommentToServer = async (
		annotManagerInstance: any,
		annot: any,
		fields: ExpertNoteFields
	): Promise<void> => {
		if (annot.getCustomData?.(SERVER_COMMENT_ID_KEY)) {
			return;
		}
		const stageId = cabinetStageIdRef.current;
		if (!stageId) {
			return;
		}
		const xfdf = await annotManagerInstance.exportAnnotations({
			annotList: [annot],
			links: false,
			widgets: false,
			fields: false,
		});
		try {
			await store
				.dispatch(
					cabinetApi.endpoints.createCabinetDocumentComment.initiate({
						docId: docIdNum,
						body: {
							stage_id: stageId,
							remark: fields.observation.trim() || null,
							proposal: fields.proposedRevision.trim() || null,
							justification: fields.rationale.trim() || null,
							xfdf,
							reply_to: null,
						},
					})
				)
				.unwrap();
			const refreshed = await store
				.dispatch(
					cabinetApi.endpoints.getCabinetDocument.initiate(docIdNum, {
						forceRefetch: true,
					})
				)
				.unwrap();
			const xfdfNorm = xfdf.trim();
			const match = refreshed.comments.find((c) => c.xfdf.trim() === xfdfNorm);
			if (match) {
				try {
					annot.setCustomData(SERVER_COMMENT_ID_KEY, String(match.comment_id));
					if (
						typeof match.author?.fio === 'string' &&
						match.author.fio.trim().length > 0
					) {
						annot.Author = match.author.fio.trim();
					}
					annotManagerInstance.updateAnnotation(annot);
				} catch {
					// ignore
				}
				if (match.status === 'accepted') {
					lastSyncedStatusRef.current.set(match.comment_id, 'accepted');
				} else if (match.status === 'declined') {
					lastSyncedStatusRef.current.set(match.comment_id, 'declined');
				}
			}
		} catch {
			// ошибка сети / 4xx
		}
	};

	const handleExpertSave = (fields: ExpertNoteFields): void => {
		const inst = instanceRef.current as any;
		if (!inst) {
			setExpertModal(null);
			expertDraftAnnotIdRef.current = null;
			return;
		}
		const modal = expertModal;
		if (!modal) {
			return;
		}
		const annotManager = inst.Core.documentViewer.getAnnotationManager();
		const annot = annotManager
			.getAnnotationsList()
			.find((a: any) => String(a.Id) === modal.annotId);
		if (annot) {
			const body = formatExpertNoteBody(fields);
			annot.setContents(body);
			try {
				annot.setCustomData(EXPERT_NOTE_CUSTOM_KEY, JSON.stringify(fields));
			} catch {
				// игнорируем fail custom data
			}
			annotManager.updateAnnotation(annot);
			if (viewerRoleRef.current === 'expert') {
				void syncNewExpertCommentToServer(annotManager, annot, fields);
			}
		}
		expertDraftAnnotIdRef.current = null;
		setExpertModal(null);
		const ui = inst.UI as any;
		void ui?.openElements?.(['notesPanel']);
	};

	const handleExpertCancel = (): void => {
		const inst = instanceRef.current as any;
		const modal = expertModal;
		if (inst && modal) {
			const annotManager = inst.Core.documentViewer.getAnnotationManager();
			const annot = annotManager
				.getAnnotationsList()
				.find((a: any) => String(a.Id) === modal.annotId);
			if (annot) {
				annotManager.deleteAnnotations([annot], { force: true });
			}
		}
		expertDraftAnnotIdRef.current = null;
		setExpertModal(null);
		const ui = inst?.UI as any;
		void ui?.openElements?.(['notesPanel']);
	};

	return (
		<div className={cls.layout}>
			{docMeta && (
				<div className={cls.leftPanel} aria-hidden={false}>
					<div className={cls.leftSummaryCard}>
						<p className={cls.leftSummaryTitle}>{docMeta.title}</p>
						<p className={cls.leftSummaryDesc}>{docMeta.description}</p>
					</div>
					<div className={cls.leftDetailsCard}>
						<div className={cls.leftDetailsGrid}>
							<div className={cls.leftField}>
								<div className={cls.leftLabel}>ID документа</div>
								<div className={cls.leftValue}>{`DOC-${docIdNum}`}</div>
							</div>
							<div className={cls.leftField}>
								<div className={cls.leftLabel}>Статус</div>
								<div className={cls.leftValue}>{docMeta.status ?? '—'}</div>
							</div>
							<div className={cls.leftField}>
								<div className={cls.leftLabel}>Автор</div>
								<div className={cls.leftAuthorPill}>
									<span className={cls.leftAuthorAvatar} aria-hidden>
										{meProfile?.fio?.slice(0, 1) ?? '—'}
									</span>
									<span className={cls.leftAuthorName}>
										{meProfile?.fio ??
											(docMeta.authors.length
												? `#${docMeta.authors.join(', ')}`
												: '—')}
									</span>
								</div>
							</div>

							<div className={cls.leftField}>
								<div className={cls.leftLabel}>Тип документа</div>
								<div className={cls.leftValue}>—</div>
							</div>
							<div className={cls.leftField}>
								<div className={cls.leftLabel}>Категория</div>
								<div className={cls.leftValue}>—</div>
							</div>
							<div className={cls.leftFieldWide}>
								<div className={cls.leftLabel}>Экспертная группа</div>
								<div className={cls.leftExpertGroup}>
									{docMeta.authors.length ? (
										docMeta.authors.slice(0, 6).map((id) => (
											<span key={id} className={cls.leftExpertChip}>
												#{id}
											</span>
										))
									) : (
										<span className={cls.leftValue}>—</span>
									)}
								</div>
							</div>
							<div className={cls.leftFieldWide}>
								<div className={cls.leftLabel}>Ответственный комитет</div>
								<div className={cls.leftValue}>—</div>
							</div>
						</div>
					</div>
				</div>
			)}

			{docMeta && (
				<div className={cls.bottomPanel}>
					<div className={cls.bottomDates}>
						<div className={cls.dateItem}>
							<div className={cls.dateLabel}>Создан</div>
							<div className={cls.dateValue}>{formatDate(docMeta.created_at)}</div>
						</div>
						<div className={cls.dateItem}>
							<div className={cls.dateLabel}>Начало рецензирования</div>
							<div className={cls.dateValue}>{formatDate(docMeta.modified_at)}</div>
						</div>
						<div className={cls.dateItem}>
							<div className={cls.dateLabel}>Дедлайн комментариев</div>
							<div className={cls.dateValue}>{formatDate(docMeta.modified_at)}</div>
						</div>
						<div className={cls.dateItem}>
							<div className={cls.dateLabel}>Планируемое утверждение</div>
							<div className={cls.dateValue}>{formatDate(docMeta.modified_at)}</div>
						</div>
					</div>

					{viewerRole === 'expert' &&
					(myReviewStatus === 'accepted' || myReviewStatus === 'declined') ? (
						<div className={cls.bottomActions}>
							<button
								type="button"
								className={cls.returnToReviewBtn}
								disabled={isReviewStatusLoading}
								onClick={() => void handleReturnToReview()}
							>
								вернуться к рассмотрению{' '}
								<span className={cls.returnToReviewIcon}>⟳</span>
							</button>
							<div className={cls.decisionBtn} role="status" aria-live="polite">
								{myReviewStatus === 'accepted'
									? 'документ принят'
									: 'документ отклонен'}{' '}
								<span className={cls.decisionIcon}>✓</span>
							</div>
						</div>
					) : viewerRole === 'expert' ? (
						<div className={cls.bottomActions}>
							<button
								type="button"
								className={cls.declineBtn}
								disabled={isReviewStatusLoading}
								onClick={() => void handleReviewDecision('declined')}
							>
								отклонить <span className={cls.declineIcon}>×</span>
							</button>
							<button
								type="button"
								className={cls.approveBtn}
								disabled={isReviewStatusLoading}
								onClick={() => void handleReviewDecision('accepted')}
							>
								принять <span className={cls.approveIcon}>✓</span>
							</button>
						</div>
					) : null}
				</div>
			)}

			{viewerRole === 'expert' && (
				<ExpertNoteModal
					open={expertModal !== null}
					initial={
						expertModal?.initial ?? {
							observation: '',
							proposedRevision: '',
							rationale: '',
						}
					}
					onSave={handleExpertSave}
					onCancel={handleExpertCancel}
				/>
			)}
			<div ref={viewerRef} className={cls.viewer} />
		</div>
	);
};
