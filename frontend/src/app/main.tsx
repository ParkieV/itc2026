import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import '@/styles/global.scss';
import '@/styles/variables.scss';
import { MainPage } from '@/pages/MainPage/MainPage';
import { store } from '@/store/store';
import ThemeProvider from './providers/ThemeProvider';

const routes = createBrowserRouter([
	{
		path: '/',
		element: <MainPage />
	},
]);
createRoot(document.getElementById('root')!).render(
	<Provider store={store}>
		<ThemeProvider>
			<RouterProvider router={routes} />
		</ThemeProvider>
	</Provider>
);
