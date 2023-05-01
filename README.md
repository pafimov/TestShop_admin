# TestShop_admin

This is Telegram shop bot with Django admin panel.<br/><br/>
User comands:<br/>
/help - Справка<br/>
/goods - Каталог<br/>
/cart - Корзина<br/>
/order - Оформить заказ<br/>
/cancel - Отмена действия<br/><br/>
Admin comands:<br/>
/add - Добавление нового товара<br/>

In admin panel viewing objects and mailing is possible.<br/>

To run:<br/>
<code>pip install -r requirements.txt</code>

Terminal 1:
<code>python manage.py runserver</code>

Terminal 2:
<code>python manage.py bot</code>

Notice that PostreSQL have to be installed. Configuration of it have to be put in testtask/.env.<br/>
Token of bot has to be put in users_api/management/commands/.env.
