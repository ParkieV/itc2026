import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { Toast } from '@heroui/react';
import '@styles/fonts.css';
import '@styles/tailwind.css';
import '@styles/global.scss';
import '@styles/variables.scss';
import { AppShell } from './AppShell';
import { PdfViewerPage } from '@pages/PdfViewerPage/PdfViewerPage';
import { store } from '@store/store';
import { KanbanPage } from '@pages/KanbanPage/KanbanPage';

const routes = createBrowserRouter([
	{
		path: '/',
		element: <AppShell />,
		children: [
			{
				path: '/',
				element: <KanbanPage />
			},
			{
				path: '/pdf/:documentId',
				element: <PdfViewerPage />
			},
		],
	}
]);
createRoot(document.getElementById('root')!).render(
	<Provider store={store}>
		<Toast.Provider />
			<RouterProvider router={routes} />
	</Provider>
);
