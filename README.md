
## Техническое задание

Необходимо реализовать скрипт на python с использованием aiohttp/selenium для парсинга карточек товаров категории LEGO с сайта магазина Деский Мир

Скрипт должен удовлетворять следующим требованиям:
- Реализован асинхронный подход
- Предусмотрена блокировка ip адреса (использование и ротация по прокси)
- Скорость парсинга - до 500к в день (20к в час)
- Подключить базу данных, в которой будут храниться:
	- Прокси
	- Карточки товаров

 ### Реализовать максимально оптимальный алгоритм

## По желанию 
реализовать архитектуру ботфермы:
- Основной сервер, который запускает ботов. На fastapi/flask, занимается распределением ботов и созданием новых, а также менеджментом прокси
- Серверы - воркеры, которые занимаются непосредственно парсингом детмира 
