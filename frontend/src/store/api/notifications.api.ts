import { api } from '@store/api/api'

import type {
	V1CabinetNotificationsUnreadGetResponse,
} from '@shared/types/api'

export const notificationsApi = api.injectEndpoints({
	endpoints: (builder) => ({
		listCabinetUnreadNotifications: builder.query<
			V1CabinetNotificationsUnreadGetResponse,
			void
		>({
			query: () => '/cabinet/notifications/unread',
			providesTags: ['Notifications'],
		}),

		markCabinetNotificationRead: builder.mutation<void, number>({
			query: (notificationId) => ({
				method: 'POST',
				url: `/cabinet/notifications/${notificationId}/read`,
			}),
			invalidatesTags: ['Notifications'],
		}),
	}),
})

export const {
	useListCabinetUnreadNotificationsQuery,
	useMarkCabinetNotificationReadMutation,
} = notificationsApi

