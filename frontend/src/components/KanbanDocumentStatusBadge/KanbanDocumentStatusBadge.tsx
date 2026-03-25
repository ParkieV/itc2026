import type { FC } from 'react';
import {
	AsteriskIcon,
	CheckIcon,
	ChecksIcon,
	CircleNotchIcon,
	SpinnerGapIcon,
	ExclamationMarkIcon,
} from '@phosphor-icons/react';
import type { DocumentUserStatus } from '@shared/types/api';
import cls from './KanbanDocumentStatusBadge.module.scss';

/** Ключи стилей бейджа (в т.ч. legacy / макет без аналога в OpenAPI). */
export type KanbanDocumentStatusVariant =
	| 'waiting'
	| 'not_viewed'
	| 'edits_required'
	| 'new_comment'
	| 'action_required'
	| 'sent'
	| 'viewed';

const ICON_SIZE = 16;

type Config = {
	label: string;
	Icon: typeof SpinnerGapIcon;
};

const VARIANT_CONFIG: Record<KanbanDocumentStatusVariant, Config> = {
	waiting: { label: 'ожидание', Icon: SpinnerGapIcon },
	not_viewed: { label: 'не просмотрено', Icon: SpinnerGapIcon },
	edits_required: { label: 'требуются правки', Icon: ExclamationMarkIcon },
	new_comment: { label: 'новые комментарии', Icon: CircleNotchIcon },
	action_required: { label: 'требуется действие', Icon: AsteriskIcon },
	sent: { label: 'отправлено', Icon: CheckIcon },
	viewed: { label: 'просмотрено', Icon: ChecksIcon },
};

const NEUTRAL_VARIANTS: KanbanDocumentStatusVariant[] = ['waiting', 'not_viewed'];

const DOCUMENT_USER_STATUS_TO_UI: Record<DocumentUserStatus, KanbanDocumentStatusVariant> = {
	new_comment: 'new_comment',
	not_viewed: 'not_viewed',
	viewed: 'viewed',
	edits_required: 'edits_required',
	action_required: 'action_required',
	sent: 'sent',
};

const isDocumentUserStatus = (s: string): s is DocumentUserStatus =>
	(s as DocumentUserStatus) in DOCUMENT_USER_STATUS_TO_UI;

/**
 * OpenAPI `DocumentUserStatus` → вариант бейджа.
 * `null` / `undefined` — по контракту бейдж не показываем.
 */
const mapDocumentUserStatusToBadgeVariant = (
	status: DocumentUserStatus | string | null | undefined
): KanbanDocumentStatusVariant | null => {
	if (status === null || status === undefined) {
		return null;
	}
	if (typeof status === 'string' && isDocumentUserStatus(status)) {
		return DOCUMENT_USER_STATUS_TO_UI[status];
	}

	return 'waiting';
};

export interface KanbanDocumentStatusBadgeProps {
	/** `docs[].status` из GET /v1/cabinet/stages (OpenAPI DocumentUserStatus | null). */
	status?: DocumentUserStatus | string | null;
	className?: string;
}

export const KanbanDocumentStatusBadge: FC<KanbanDocumentStatusBadgeProps> = ({
	status,
	className,
}) => {
	const resolved = mapDocumentUserStatusToBadgeVariant(status);
	if (resolved === null) {
		return null;
	}

	const { label, Icon } = VARIANT_CONFIG[resolved];
	const isNeutral = NEUTRAL_VARIANTS.includes(resolved);
	const iconColor = isNeutral ? '#222b33' : '#ffffff';

	return (
		<span
			className={`${cls.statusBadge} ${cls[`status_${resolved}`]}${className ? ` ${className}` : ''}`}
		>
			<Icon className={cls.statusIcon} size={ICON_SIZE} weight="regular" color={iconColor} />
			{label}
		</span>
	);
};
