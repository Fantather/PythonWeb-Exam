import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from forum.models import Community, Topic, Post
from forum.services import CommunityService, TopicService, PostService
from core.helpers import generate_unique_slug

User = get_user_model()
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Команда для инициализации БД начальными данными.
    Запуск: python manage.py seed_forum
    """
    help = "Инициализирует БД базовой структурой сообществ и тестовыми топиками."

    def handle(self, *args, **options) -> None:
        """Точка входа команды управления."""
        if self._is_database_populated():
            self.stdout.write(self.style.WARNING("База данных уже содержит данные форума. Сидирование прервано."))
            return

        try:
            self._generate_seed_data()
            self.stdout.write(self.style.SUCCESS("Сидирование базы данных успешно завершено."))
        except Exception as e:
            logger.error(f"Ошибка при сидировании БД: {str(e)}", exc_info=True)
            self.stdout.write(self.style.ERROR("Произошла ошибка при сидировании. Изменения отменены. Детали в логах."))

    def _is_database_populated(self) -> bool:
        """
        Проверяет наличие записей в основных таблицах.
        Использование .exists() генерирует оптимизированный SQL-запрос `SELECT 1 ... LIMIT 1`.
        """
        return Community.objects.exists() or Topic.objects.exists() or Post.objects.exists()

    @transaction.atomic
    def _generate_seed_data(self) -> None:
        """
        Генерирует тестовые данные с распределением ролей: 
        Администратор (новости) и Пользователи (обсуждения и комментарии).
        """
        # 1. Инициализация учетных записей (Identity Management)
        admin_user, admin_created = User.objects.get_or_create(
            username="Confessor_Makarov",
            defaults={
                "email": "priest@ecclesiarchy.local",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
                "avatar": "/users/seed/catto.png",
            }
        )
        
        if admin_created:
            admin_user.set_password("for_emperor_40k")
            print("Admin user created: Confessor_Makarov")
            print("Avatar Url:", admin_user.avatar.url)
            admin_user.save()

        fan_users = []
        fan_credentials = [
            ("Guardsman_Kael", "kael@cadiastands.local"),
            ("Tech_Adept_Zeta", "zeta@mars.local"),
            ("Hive_Scum_99", "scum@necromunda.local")
        ]

        
        for username, email in fan_credentials:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email, "is_active": True, "is_staff": False}
            )
            if created:
                user.set_password("standard_pass_123")
                user.save()
            fan_users.append(user)
            
        fan_kael, fan_zeta, fan_scum = fan_users

        # 2. Инициализация доменных зон (Сообщества)
        community_news = CommunityService.create_root_community(
            title="Adeptus Ministorum (Официально)",
            slug=generate_unique_slug("Adeptus Ministorum", Community),
            description="Официальные указы, проповеди и новости сектора.",
            owner=admin_user  # Назначение владельца (One-to-Many)

        )
        # Инициализация подписок (Many-to-Many)
        community_news.subscribers.set([fan_kael, fan_zeta, fan_scum])

        community_mechanicus = CommunityService.create_root_community(
            title="Adeptus Mechanicus",
            slug=generate_unique_slug("Adeptus Mechanicus", Community),
            description="Обсуждение обслуживания техники, СПО и оружия.",
            owner=fan_zeta
        )
        community_mechanicus.subscribers.set([fan_kael, fan_scum])

        community_underhive = CommunityService.create_root_community(
            title="Нижний Улей",
            slug=generate_unique_slug("Underhive", Community),
            description="Свободное общение граждан Империума. Модерируется Арбитрес.",
            owner=fan_scum
        )
        community_underhive.subscribers.set(fan_users)

        community_koshkin_dom = CommunityService.create_root_community(
            title="Кошкин дом",
            slug=generate_unique_slug("Koshkin Dom", Community),
            description="Котики?.",
            owner=fan_scum,
            icon="/icons/seed/yoshi.png"
        )
        community_koshkin_dom.subscribers.set(fan_users)
        
        # 3. Генерация топика Администратора (Новости)
        topic_news = TopicService.create_topic_with_post(
            community=community_news,
            author=admin_user,
            title="Helldivers x Warhammer 40k coming soon",
            content="Коллаборация между Warhammer 40k и Helldivers",
            images="posts/images/seed/helldivers-x-warhammer-40k-coming.webp" # <-- ИСПРАВЛЕНО
        )

        root_post_news = Post.objects.get(topic=topic_news, parent__isnull=True)
        
        reply_news_1 = PostService.create_reply(
            topic=topic_news,
            author=fan_kael,
            content="Кадия стоит! Мой полк готов к развертыванию. Ожидаем транспортные корабли.",
            parent=root_post_news
        )

        PostService.create_reply(
            topic=topic_news,
            author=fan_scum,
            content="А двойной паек трупного крахмала будут выдавать записавшимся?",
            parent=reply_news_1
        )

        # 4. Генерация пользовательского контента
        topic_tech = TopicService.create_topic_with_post(
            community=community_mechanicus,
            author=fan_zeta,
            title="Где достать священную мазь для лазгана (Паттерн Кантран)?",
            content="Дух машины моего лазгана гневается. Стандартные литании не помогают, линза перегревается после третьего выстрела.",
            images=None # <-- ИСПРАВЛЕНО
        )

        root_post_tech = Post.objects.get(topic=topic_tech, parent__isnull=True)
        
        PostService.create_reply(
            topic=topic_tech,
            author=fan_kael,
            content="Обратись к квартирмейстеру роты. И проверь печать чистоты на батарее, иногда проблема в несанкционированных модификациях.",
            parent=root_post_tech
        )

        topic_rumors = TopicService.create_topic_with_post(
            community=community_underhive,
            author=fan_scum,
            title="Странные тени в секторе 4",
            content="Вчера видел многорукую тень возле гидропонных ферм. Местные пропадают. Прикладываю размытый снимок с ауспекса.",
            images="posts/images/seed/mehanicus-mech.jpg" # <-- ИСПРАВЛЕНО
        )

        root_post_rumors = Post.objects.get(topic=topic_rumors, parent__isnull=True)

        PostService.create_reply(
            topic=topic_rumors,
            author=fan_zeta,
            content="Ересь! Немедленно доложите локальному отделению Адептус Арбитрес. Подобные пикт-снимки не должны распространяться в открытой ноосфере.",
            parent=root_post_rumors
        )


        #что?
        topic_cat = TopicService.create_topic_with_post(
            community=community_koshkin_dom,
            author=fan_zeta,
            title="Котики в Империуме",
            content="Вы тут вархамерите, а я котиков положу",
            images=["posts/images/seed/cattoritoditto.png", "posts/images/seed/catto.png"] 
        )

        root_post_cat = Post.objects.get(topic=topic_cat, parent__isnull=True)
        PostService.create_reply(
            topic=topic_cat,
            author=fan_kael,
            content="Ересь! Но мило.",
            parent=root_post_cat
        )
        PostService.create_reply(
            topic=topic_cat,
            author=fan_scum,
            content="Только броня и восхваление императора!",
            parent=root_post_cat
        )

        reply_cat_1 = PostService.create_reply(
            topic=topic_cat,
            author=fan_kael,
            content="Какая милота в империуме?!?!?!",
            parent=root_post_cat
        )
        PostService.create_reply(
            topic=topic_cat,
            author=fan_scum,
            content="Ужас! Снимайте эти изображения с экранов, пока не поздно!",
            parent=reply_cat_1
        )

        PostService.create_reply(
            topic=topic_cat,
            author=fan_scum,
            content="Котики...",
            parent=reply_cat_1
        )



