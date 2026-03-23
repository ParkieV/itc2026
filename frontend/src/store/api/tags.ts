export const API_TAG_TYPES = ['User', 'Cards', 'Item'] as const

export type ApiTagType = (typeof API_TAG_TYPES)[number]
