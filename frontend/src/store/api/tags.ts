export const API_TAG_TYPES = ['User', 'Documents', 'Comments', 'Stages'] as const

export type ApiTagType = (typeof API_TAG_TYPES)[number]
