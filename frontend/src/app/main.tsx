import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import '@styles/tailwind.css';
import '@styles/global.scss';
import '@styles/variables.scss';
import { MainPage } from '@pages/MainPage/MainPage';
import { PdfViewerPage } from '@pages/PdfViewerPage/PdfViewerPage';
import { store } from '@store/store';
import ThemeProvider from './providers/ThemeProvider';
import { KanbanPage } from '@pages/KanbanPage/KanbanPage';

const routes = createBrowserRouter([
	{
		path: '/',
		element: <MainPage />
	},
	{
		path: '/pdf/:documentId',
		element: <PdfViewerPage />
	},
	{
		path: '/kanban',
		element: <KanbanPage />
	}
]);
createRoot(document.getElementById('root')!).render(
	<Provider store={store}>
		<ThemeProvider>
			<RouterProvider router={routes} />
		</ThemeProvider>
	</Provider>
);
