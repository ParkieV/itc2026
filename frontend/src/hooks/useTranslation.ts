import en from '@translations/en.json';
import ru from '@translations/ru.json';
import cookie from 'js-cookie';

const translations = { en, ru } as const;
type Lang = keyof typeof translations;

const useTranslation = () => {
	const raw = cookie.get('language') || 'ru';
	const language: Lang = raw === 'en' ? 'en' : 'ru';
	const languages = ['ru', 'en'] as const;

	const translate = (key: string): unknown => {
		const keys = key.split('.');
		return keys.reduce<unknown>((obj, k) => {
			if (obj !== null && typeof obj === 'object' && k in obj) {
				return (obj as Record<string, unknown>)[k];
			}
			return undefined;
		}, translations[language] as unknown);
	};

	const setLanguage = (language: 'ru' | 'en') => {
		cookie.set('language', language);
	};

	const toggleLanguage = () => {
		const newLanguage = language === 'ru' ? 'en' : 'ru';
		setLanguage(newLanguage);
	};

	return { t: translate, language, languages, setLanguage, toggleLanguage };
};

export default useTranslation;
