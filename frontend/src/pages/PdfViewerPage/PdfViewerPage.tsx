/* eslint-disable @typescript-eslint/no-explicit-any */
import { FC, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import WebViewer from '@pdftron/webviewer'

import cls from './PdfViewerPage.module.scss'

type ViewerHandle = Awaited<ReturnType<typeof WebViewer>>

const DEFAULT_DOCUMENT_ID = '61285.pdf'
const getCommentsStorageKey = (documentId: string): string =>
	`pdf-webviewer-comments-v1:${documentId}`

interface WebViewerCommentSnapshot {
	id: string
	pageNumber?: number
	author?: string
	subject?: string
	contents?: string
	status?: string
	modifiedAt?: string
}

interface WebViewerSavedPayload {
	documentId: string
	xfdf: string
	comments: WebViewerCommentSnapshot[]
	savedAt: string
}

export const PdfViewerPage: FC = () => {
	const { documentId: routeDocumentId } = useParams<{ documentId: string }>()
	const documentId = routeDocumentId || DEFAULT_DOCUMENT_ID
	const docPath = `/docs/${documentId}`

	const viewerRef = useRef<HTMLDivElement | null>(null)
	const instanceRef = useRef<ViewerHandle | null>(null)

	useEffect(() => {
		document.documentElement.classList.add('pdf-viewer-route')
		return () => {
			document.documentElement.classList.remove('pdf-viewer-route')
		}
	}, [])

	useEffect(() => {
		if (!viewerRef.current) {
			return
		}
		let mounted = true
		let persistDebounce: ReturnType<typeof setTimeout> | null = null
		let removeVisibility: (() => void) | null = null

		const setup = async (): Promise<void> => {
			const instance = await WebViewer(
				{
					path: '/webviewer',
					css: '/pdf-webviewer-custom.css',
				},
				viewerRef.current as HTMLDivElement
			)
			if (!mounted) {
				return
			}
			instanceRef.current = instance
			const ui = (instance as any).UI
			const core = instance.Core as any
			const { documentViewer } = core
			const annotManager = documentViewer.getAnnotationManager()
			const setTextSelectMode = (): void => {
				const textSelectTool =
					documentViewer.getTool('TextSelect') ??
					documentViewer.getToolModeMap()?.TextSelect
				if (textSelectTool) {
					documentViewer.setToolMode(textSelectTool)
				}
			}

			await ui.setLanguage('ru')
			ui.enableFeatures([ui.Feature.TextSelection])

			// Keep only text selection/comment flow in custom right panel.
			ui.disableElements([
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
				
			])
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
			])
			ui.openElements(['notesPanel'])
			setTextSelectMode()

			const getAnnotContents = (annot: any): string => {
				if (typeof annot?.getContents === 'function') {
					return String(annot.getContents() ?? '')
				}
				return String(annot?.Contents ?? '')
			}

			const getAnnotStatus = (annot: any): string => {
				// «Принято / Отклонено» — это State + StateModel Review, не getStatus()
				if (typeof annot?.getState === 'function') {
					const state = String(annot.getState() ?? '').trim()
					if (state) {
						return state
					}
				}
				const fromProp = String(annot?.State ?? '').trim()
				if (fromProp) {
					return fromProp
				}
				if (typeof annot?.getStatus === 'function') {
					return String(annot.getStatus() ?? '')
				}
				return String(annot?.Status ?? '')
			}

			const persistWebViewerData = async (): Promise<void> => {
				try {
					const xfdf = await annotManager.exportAnnotations({
						links: false,
						widgets: false,
						fields: false,
					})
					const comments = annotManager
						.getAnnotationsList()
						.filter((annot: any) => getAnnotContents(annot).trim().length > 0)
						.map((annot: any) => ({
							id: String(annot.Id),
							pageNumber: annot.PageNumber,
							author: annot.Author,
							subject: annot.Subject,
							contents: getAnnotContents(annot),
							status: getAnnotStatus(annot),
							modifiedAt: annot.DateModified,
						}))
					const payload: WebViewerSavedPayload = {
						documentId,
						xfdf,
						comments,
						savedAt: new Date().toISOString(),
					}
					localStorage.setItem(getCommentsStorageKey(documentId), JSON.stringify(payload))
				} catch {
					// quota / приватный режим — не ломаем просмотр
				}
			}

			const schedulePersist = (): void => {
				if (persistDebounce !== null) {
					clearTimeout(persistDebounce)
				}
				persistDebounce = setTimeout(() => {
					persistDebounce = null
					void persistWebViewerData()
				}, 350)
			}

			documentViewer.addEventListener('documentLoaded', async () => {
				const existingAnnotations = annotManager.getAnnotationsList()
				if (existingAnnotations.length > 0) {
					annotManager.deleteAnnotations(existingAnnotations, {
						imported: true,
						force: true,
					})
				}

				const raw = localStorage.getItem(getCommentsStorageKey(documentId))
				if (raw) {
					try {
						const payload = JSON.parse(raw) as WebViewerSavedPayload
						if (payload?.xfdf) {
							await annotManager.importAnnotations(payload.xfdf)
						}
					} catch {
						localStorage.removeItem(getCommentsStorageKey(documentId))
					}
				}
				setTextSelectMode()
				await persistWebViewerData()
			})

			annotManager.addEventListener(
				'annotationChanged',
				(_annots: unknown, _action: string, info?: { imported?: boolean }) => {
					// Во время importAnnotations export даёт неполный XFDF — не перезаписываем storage
					if (info?.imported) {
						return
					}
					schedulePersist()
				}
			)

			const flushOnHide = (): void => {
				if (document.visibilityState === 'hidden') {
					if (persistDebounce !== null) {
						clearTimeout(persistDebounce)
						persistDebounce = null
					}
					void persistWebViewerData()
				}
			}
			document.addEventListener('visibilitychange', flushOnHide)
			removeVisibility = () => {
				document.removeEventListener('visibilitychange', flushOnHide)
			}

			ui.loadDocument(docPath, {
				loadAnnotations: false,
			})
		}

		void setup()

		return () => {
			mounted = false
			if (persistDebounce !== null) {
				clearTimeout(persistDebounce)
				persistDebounce = null
			}
			removeVisibility?.()
			instanceRef.current = null
		}
	}, [docPath, documentId])

	return (
		<div className={cls.layout}>
			<div ref={viewerRef} className={cls.viewer} />
		</div>
	)
}

