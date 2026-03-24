import { FC } from 'react';
import { Link } from 'react-router-dom';
import cls from './MainPage.module.scss';


export const MainPage: FC = () => {
	
	return (
		<div className={cls.mainpage}>
			<div>
				<h1>PDF comments demo</h1>
				<Link to='/pdf/61285.pdf'>Open first PDF from public/docs</Link>
			</div>
		</div>
	);
};
