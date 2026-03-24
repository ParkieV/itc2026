export const API_TAG_TYPES = ['User', 'Documents', 'Comments'] as const

export type ApiTagType = (typeof API_TAG_TYPES)[number]
