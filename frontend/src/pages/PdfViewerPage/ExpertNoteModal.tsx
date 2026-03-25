import { FC, FormEvent, useEffect, useId, useState } from 'react'

import type { ExpertNoteFields } from './expertNoteFormat'

import cls from './ExpertNoteModal.module.scss'

export interface ExpertNoteModalProps {
	open: boolean
	initial: ExpertNoteFields
	onSave: (fields: ExpertNoteFields) => void
	onCancel: () => void
}

export const ExpertNoteModal: FC<ExpertNoteModalProps> = ({
	open,
	initial,
	onSave,
	onCancel,
}) => {
	const titleId = useId()
	const [observation, setObservation] = useState(initial.observation)
	const [proposedRevision, setProposedRevision] = useState(initial.proposedRevision)
	const [rationale, setRationale] = useState(initial.rationale)

	useEffect(() => {
		if (open) {
			setObservation(initial.observation)
			setProposedRevision(initial.proposedRevision)
			setRationale(initial.rationale)
		}
	}, [open, initial.observation, initial.proposedRevision, initial.rationale])

	if (!open) {
		return null
	}

	const canSave = observation.trim().length > 0

	const handleSubmit = (e: FormEvent): void => {
		e.preventDefault()
		if (!canSave) {
			return
		}
		onSave({
			observation: observation.trim(),
			proposedRevision: proposedRevision.trim(),
			rationale: rationale.trim(),
		})
	}

	return (
		<div className={cls.overlay} role="presentation">
			<div className={cls.dialog} role="dialog" aria-modal="true" aria-labelledby={titleId}>
				<h2 id={titleId} className={cls.title}>
					Комментарий эксперта
				</h2>
				<form className={cls.form} onSubmit={handleSubmit}>
					<label className={cls.label}>
						<span className={cls.labelText}>Замечание/предложение</span>
						<textarea
							className={cls.textarea}
							value={observation}
							onChange={(ev) => setObservation(ev.target.value)}
							rows={4}
							required
						/>
					</label>
					<label className={cls.label}>
						<span className={cls.labelText}>Предлагаемая редакция (необязательно)</span>
						<textarea
							className={cls.textarea}
							value={proposedRevision}
							onChange={(ev) => setProposedRevision(ev.target.value)}
							rows={3}
						/>
					</label>
					<label className={cls.label}>
						<span className={cls.labelText}>Обоснование предлагаемой редакции (необязательно)</span>
						<textarea
							className={cls.textarea}
							value={rationale}
							onChange={(ev) => setRationale(ev.target.value)}
							rows={3}
						/>
					</label>
					<div className={cls.actions}>
						<button type="button" className={cls.btnSecondary} onClick={onCancel}>
							Отмена
						</button>
						<button type="submit" className={cls.btnPrimary} disabled={!canSave}>
							Сохранить
						</button>
					</div>
				</form>
			</div>
		</div>
	)
}
