export const EXPERT_NOTE_CUSTOM_KEY = 'itc_note_v1'

/** Числовой `comment_id` с бэка (POST/PATCH комментария). */
export const SERVER_COMMENT_ID_KEY = 'itc_server_comment_id'

export interface ExpertNoteFields {
	observation: string
	proposedRevision: string
	rationale: string
}

export function formatExpertNoteBody(fields: ExpertNoteFields): string {
	const obs = fields.observation.trim()
	const prop = fields.proposedRevision.trim()
	const rat = fields.rationale.trim()
	const parts: string[] = []
	parts.push(`Замечание/предложение:\n${obs}`)
	if (prop.length > 0) {
		parts.push(`\n\nПредлагаемая редакция:\n${prop}`)
	}
	if (rat.length > 0) {
		parts.push(`\n\nОбоснование предлагаемой редакции:\n${rat}`)
	}
	return parts.join('')
}

export function parseExpertNoteFieldsFromAnnotation(annot: {
	getCustomData?: (key: string) => string
	Contents?: string
	getContents?: () => string
}): ExpertNoteFields {
	try {
		const raw = annot.getCustomData?.(EXPERT_NOTE_CUSTOM_KEY)
		if (raw) {
			const parsed = JSON.parse(raw) as Partial<ExpertNoteFields>
			return {
				observation: String(parsed.observation ?? ''),
				proposedRevision: String(parsed.proposedRevision ?? ''),
				rationale: String(parsed.rationale ?? ''),
			}
		}
	} catch {
		// fall through
	}
	const contents =
		typeof annot.getContents === 'function'
			? String(annot.getContents() ?? '')
			: String(annot.Contents ?? '')

	const pickSection = (label: string): string => {
		const re = new RegExp(
			`${label}\\s*:\\s*([\\s\\S]*?)(?=\\n\\n[А-Яа-яЁё/ —-]+:\\s*|\\s*$)`,
			'i'
		)
		const m = re.exec(contents)
		return m?.[1]?.trim() ?? ''
	}

	const observation = pickSection('Замечание/предложение')
	const proposedRevision = pickSection('Предлагаемая редакция')
	const rationale = pickSection('Обоснование предлагаемой редакции')

	if (observation || proposedRevision || rationale) {
		return { observation, proposedRevision, rationale }
	}

	return { observation: contents.trim(), proposedRevision: '', rationale: '' }
}
