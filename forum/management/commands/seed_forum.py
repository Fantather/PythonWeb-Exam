import logging
from typing import Dict, Any, List

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from forum.models import Community, Topic, Post
from forum.services import CommunityService, TopicService, PostService
from core.helpers import generate_unique_slug

User = get_user_model()
logger = logging.getLogger(__name__)



# --- СТРУКТУРЫ ДАННЫХ ДЛЯ СИДИРОВАНИЯ ---
SEED_USERS = [
    {
        "username": "Confessor_Makarov",
        "email": "priest@ecclesiarchy.local",
        "password": "for_emperor_40k",
        "is_staff": True,
        "is_superuser": True,
        "avatar": "/users/seed/catto.png"
    },
    {
        "username": "Guardsman_Kael",
        "email": "kael@cadiastands.local",
        "password": "standard_pass_123",
    },
    {
        "username": "Tech_Adept_Zeta",
        "email": "zeta@mars.local",
        "password": "standard_pass_123",
    },
    {
        "username": "Hive_Scum_99",
        "email": "scum@necromunda.local",
        "password": "standard_pass_123",
    },
    {
        "username": "Inquisitor_Varn",      # Это инквизитор, я выдал ему право заходить в админку
        "email": "varn@ordohereticus.local",
        "password": "purge_the_unclean",
        "is_staff": True,  
        "avatar": "/users/seed/inquisition_rosette.png"
    },
    {
        "username": "Arbites_Lex",
        "email": "enforcer.lex@arbites.local",
        "password": "standard_pass_123",
    },
    {
        "username": "Scribe_Tarkus",
        "email": "tarkus.442@administratum.local",
        "password": "standard_pass_123",
    },
    {
        "username": "Trader_Von_Valancius",
        "email": "captain@voidship.local",
        "password": "standard_pass_123",
    },
    {
        "username": "Chapter_Serf_Otho",
        "email": "armory@astartes.local",
        "password": "standard_pass_123",
    },
    {
        "username": "Ganger_Kroll",
        "email": "kroll@underhive.local",
        "password": "standard_pass_123",
    }
]


SEED_COMMUNITIES = [
    {
        "title": "Adeptus Ministorum (Официально)",
        "slug_base": "Adeptus Ministorum",
        "description": "Официальные указы, проповеди и новости сектора.",
        "owner": "Confessor_Makarov",
        "subscribers": ["Guardsman_Kael", "Tech_Adept_Zeta", "Hive_Scum_99", "Inquisitor_Varn"],
    },
    {
        "title": "Adeptus Mechanicus",
        "slug_base": "Adeptus Mechanicus",
        "description": "Обсуждение обслуживания техники, СПО и оружия.",
        "owner": "Tech_Adept_Zeta",
        "subscribers": ["Guardsman_Kael", "Hive_Scum_99"],
    },
    {
        "title": "Нижний Улей",
        "slug_base": "Underhive",
        "description": "Свободное общение граждан Империума. Модерируется Арбитрес.",
        "owner": "Hive_Scum_99",
        "subscribers": ["Guardsman_Kael", "Tech_Adept_Zeta", "Hive_Scum_99"],
    },
    {
        "title": "Кошкин дом",
        "slug_base": "Koshkin Dom",
        "description": "Котики?.",
        "owner": "Hive_Scum_99",
        "subscribers": ["Guardsman_Kael", "Tech_Adept_Zeta", "Hive_Scum_99"],
        "icon": "/icons/seed/yoshi.png"
    }
]

# Структура топиков поддерживает неограниченную вложенность комментариев через ключ 'replies'
SEED_TOPICS = [
    {
        "community_title": "Adeptus Ministorum (Официально)",
        "author": "Confessor_Makarov",
        "title": "Helldivers x Warhammer 40k coming soon",
        "content": "Коллаборация между Warhammer 40k и Helldivers",
        "images": "posts/images/seed/helldivers-x-warhammer-40k-coming.webp",
        "replies": [
            {
                "author": "Guardsman_Kael",
                "content": "Кадия стоит! Мой полк готов к развертыванию. Ожидаем транспортные корабли.",
                "replies": [
                    {
                        "author": "Hive_Scum_99",
                        "content": "А двойной паек трупного крахмала будут выдавать записавшимся?"
                    }
                ]
            }
        ]
    },
    {
        "community_title": "Adeptus Mechanicus",
        "author": "Tech_Adept_Zeta",
        "title": "Где достать священную мазь для лазгана (Паттерн Кантран)?",
        "content": "Дух машины моего лазгана гневается. Стандартные литании не помогают, линза перегревается после третьего выстрела.",
        "images": None,
        "replies": [
            {
                "author": "Guardsman_Kael",
                "content": "Обратись к квартирмейстеру роты. И проверь печать чистоты на батарее, иногда проблема в несанкционированных модификациях."
            }
        ]
    },
    {
        "community_title": "Нижний Улей",
        "author": "Hive_Scum_99",
        "title": "Странные тени в секторе 4",
        "content": "Вчера видел многорукую тень возле гидропонных ферм. Местные пропадают. Прикладываю размытый снимок с ауспекса.",
        "images": "posts/images/seed/mehanicus-mech.jpg",
        "replies": [
            {
                "author": "Tech_Adept_Zeta",
                "content": "Ересь! Немедленно доложите локальному отделению Адептус Арбитрес. Подобные пикт-снимки не должны распространяться в открытой ноосфере."
            },
        ]
    },
    {
        "community_title": "Кошкин дом",
        "author": "Tech_Adept_Zeta",
        "title": "Котики в Империуме",
        "content": "Вы тут вархамерите, а я котиков положу",
        "images": ["posts/images/seed/cattoritoditto.png", "posts/images/seed/catto.png"],
        "replies": [
            {
                "author": "Guardsman_Kael",
                "content": "Ересь! Но мило."
            },
            {
                "author": "Hive_Scum_99",
                "content": "Только броня и восхваление императора!"
            },
            {
                "author": "Guardsman_Kael",
                "content": "Какая милота в империуме?!?!?!",
                "replies": [
                    {
                        "author": "Hive_Scum_99",
                        "content": "Ужас! Снимайте эти изображения с экранов, пока не поздно!"
                    },
                    {
                        "author": "Hive_Scum_99",
                        "content": "Котики..."
                    },
                ]
            }
        ]
    },
    {
        "community_title": "Adeptus Ministorum (Официально)",
        "author": "Inquisitor_Varn",
        "title": "О 20-ти примархах",
        "content": """
        И тогда Император создал девятерых примархов, дабы встали они против девятерых дьяволов из внешнего ада, и одержали они победу великую, но теперь спят крепким сном, и проснутся, если Ужас вернется
        
        Лоялисты
            Феррус Манус — был убит Фулгримом в поединке во время атаки Империума на Истваан V.
            Сангвиний — отказался присоединиться к Хорусу во время битвы за Терру и был им убит.
            Лев Эль'Джонсон — вернулся на свой родной мир, Калибан, лишь для того, чтобы обнаружить предательство Лютера, его друга и заместителя. Лев возглавил верных Тёмных Ангелов в атаке на предателей, но исчез, когда варп-шторм уничтожил планету. Пробудился в начале 42-го тысячелетия, после чего Смотрящие-во-тьме вывели примарха на планету Камарат.
            Джагатай Хан — пропал во время преследования тёмных эльдар в Паутине после их нападения на Мундус Планус, ходят слухи, что он до сих пор находится там, затерявшись в её запутанных переходах.
            Леман Русс — пропал в Оке Ужаса. Среди Космических Волков ходит легенда, что Леман Русс отправился на поиски средства для излечения Императора. Его последними словами перед исчезновением стало обещание вернуться в Час Волка (последней битве).
            Рогал Дорн — пропал во время абордажа крейсера Хаоса во время Чёрного крестового похода. Рука, оставшаяся от него, хранится в самом охраняемом и святом из храмов ордена Имперских Кулаков.
            Робаут Жиллиман — был сражён ядовитым клинком демон-принца Фулгрима. Его тело в полном спокойствии хранилось в стазис-поле в сердце Храма Исправления на Макрагге. Ходили слухи, что он всё ещё жив и что его раны медленно излечиваются, несмотря на то, что это невозможно внутри стазис-поля. В конце 41-го тысячелетия примарх был возрождён совместными усилиями Адептус Механикус и эльдар-последователей новорождённого бога смерти Иннеада. На данный момент является лордом-командующим, фактическим правителем Империума Человечества.
            Вулкан — пропал. С тех пор пост, который занимают магистры ордена Саламандр считается не более чем регентским, так как они верят, что однажды Вулкан вернётся и возглавит их в великом походе против Хаоса.
            Корвус Коракс — после Ереси Хоруса, терзаемый виной и стыдом из-за неудавшейся попытки быстро возродить свой легион, потерявший множество воинов в резне на Истваане V, Коракс заперся в своём убежище в Башне Ворона. Ровно через год он покинул её, измождённый и мрачный, взял небольшой корабль и со словами «больше никогда» направился в Око Ужаса.
        
        Предатели
            Хорус Луперкаль — был убит Императором Человечества, а его душа, предположительно, уничтожена сильной псайкерской атакой. Его труп впоследствии был полностью уничтожен Абаддоном Разорителем, который сменил Хоруса в роли предводителя космодесанта Хаоса.
            Магнус Красный — обращён в демон-принца Тзинча.
            Ангрон — обращён в демон-принца Кхорна.
            Мортарион — обращён в демон-принца Нургла.
            Фулгрим — обращён в демон-принца Слаанеш.
            Лоргар Аврелиан — обращён в демон-принца Хаоса Неделимого.
            Пертурабо — обращён в демон-принца Хаоса Неделимого.
            Конрад Кёрз — убит ассасином храма Каллидус М'Шен. Говорят, что он сам позволил ей прибыть в его дворец на Тсагуальсе, так как в пути она не столкнулась с охраной на пути к его тронному залу. Встретившись со смертью, он произнёс слова: «Я знал, что ты придёшь, убийца. Я знал о том, что ты идёшь, даже тогда, когда твой корабль только входил в Восточную Окраину. Хочешь спросить, почему же я тебя не убил? Потому что твоя миссия и то, что ты собираешься сделать, подтверждают слова, сказанные мною давным-давно, и теперь я не сомневаюсь в правильности своих деяний. Тех, кто ошибался, я просто убивал, точно так же, как твой фальшивый Император теперь убьёт меня. Смерть ничто, когда знаешь, что оказался прав».
            Альфарий/Омегон — Альфарий был убит Рогалом Дорном в ходе операции Альфа-Легиона на Церере, судьба Омегона неизвестна.
        
        И два неизвестных примарха, о которых ничего не известно
        """,
        "images": [
            # Лоялисты
            "posts/images/seed/Ferrus Manus.jpg",
            "posts/images/seed/Sanguinius_death.webp",
            "posts/images/seed/Lion_El_Jonson.webp",
            "posts/images/seed/Djagatay_Han.webp",
            "posts/images/seed/Leman_Russ.webp",
            "posts/images/seed/HHL_Rogal_Dorn.webp",
            "posts/images/seed/Guilliman_Coronation.webp",
            "posts/images/seed/Vulkan_Terra.webp",
            "posts/images/seed/Corax_sketch.webp",

            # Предатели
            "posts/images/seed/HHL_Warmaster_Horus.webp",
            "posts/images/seed/Magnus_Breaches_Palace.webp",
            "posts/images/seed/Angron_Daemon_Prince_of_Khorne.webp",
            "posts/images/seed/Mortarion_Prince_of_decomposition.webp",
            "posts/images/seed/Fulgrim_Fallen_Phoenix.webp",
            "posts/images/seed/Lorgar.webp",
            "posts/images/seed/Perturabo.jpg",
            "posts/images/seed/Conrad_Curze_and_Night_Lords.webp",
            "posts/images/seed/Alpharius_Omegon.webp",

            # Забытые примархи (II и XI легионы)
            "posts/images/seed/Forgotten_Primarch_Legion_II.webp",
            "posts/images/seed/Forgotten_Primarch_Legion_XI.webp",
        ],
        "replies": [
            {
                "author": "Scribe_Tarkus",
                "content": "Достопочтенный Инквизитор, мои инфо-свитки выдают ошибку при поиске записей о II и XI легионах. Уровень допуска моей легитимации не позволяет мне обновить архивы. Это аппаратный сбой когитатора или мне следует подать запрос в центральный дата-хранилище Администратума?",
                "replies": [
                    {
                        "author": "Arbites_Lex",
                        "content": "Писец Таркус, не задавай вопросов, ответы на которые могут привести тебя в камеры дознания. Архивы очищены по указу Терры тысячелетия назад. Любые попытки восстановления этих данных классифицируются как мыслепреступление. Возвращайся к своим отчетам."
                    }
                ]
            },
            {
                "author": "Chapter_Serf_Otho",
                "content": "Слава Лорду Жиллиману! И да будут прокляты имена предателей. В залах нашего Ордена мы ежедневно читаем литании ненависти к архи-предателю Хорусу. Но видеть этот список открыто в ноосфере... это испытание нашей веры, милорд?",
                "replies": [
                    {
                        "author": "Inquisitor_Varn",
                        "content": "Именно так, покорный слуга. Знание о враге дозволено здесь лишь для того, чтобы питать вашу праведную ненависть. Невежество может породить слабость, но зрячая и фанатичная вера направляет гнев. Смотрите на эти лики и помните о цене предательства."
                    }
                ]
            },
        ]
    },
]



# --- ЛОГИКА КОМАНДЫ ---
class Command(BaseCommand):
    help = "Инициализирует БД базовой структурой сообществ и тестовыми топиками."

    def handle(self, *args, **options) -> None:
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
        return Community.objects.exists() or Topic.objects.exists() or Post.objects.exists()

    @transaction.atomic
    def _generate_seed_data(self) -> None:
        self.users_map: Dict[str, Any] = {}
        self.communities_map: Dict[str, Any] = {}

        self._seed_users()
        self._seed_communities()
        self._seed_topics_and_posts()

    def _seed_users(self) -> None:
        """Создает пользователей и сохраняет их в словарь для связей."""
        for user_data in SEED_USERS:
            defaults = {
                "email": user_data["email"],
                "is_active": True,
                "is_staff": user_data.get("is_staff", False),
                "is_superuser": user_data.get("is_superuser", False),
            }
            if "avatar" in user_data:
                defaults["avatar"] = user_data["avatar"]

            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults=defaults
            )
            
            if created:
                user.set_password(user_data["password"])
                user.save()
                
                if user.is_superuser:
                    print(f"Admin user created: {user.username}")
                    if user.avatar:
                        print(f"Avatar Url: {user.avatar.url}")

            self.users_map[user.username] = user

    def _seed_communities(self) -> None:
        """Создает сообщества и устанавливает владельцев и подписчиков."""
        for comm_data in SEED_COMMUNITIES:
            owner = self.users_map[comm_data["owner"]]
            
            community = CommunityService.create_root_community(
                title=comm_data["title"],
                slug=generate_unique_slug(comm_data["slug_base"], Community),
                description=comm_data["description"],
                owner=owner,
                icon=comm_data.get("icon")
            )
            
            subscribers = [self.users_map[uname] for uname in comm_data["subscribers"]]
            community.subscribers.set(subscribers)
            
            self.communities_map[community.title] = community

    def _seed_topics_and_posts(self) -> None:
        """Создает топики и запускает рекурсивное создание комментариев."""
        for topic_data in SEED_TOPICS:
            community = self.communities_map[topic_data["community_title"]]
            author = self.users_map[topic_data["author"]]

            topic = TopicService.create_topic_with_post(
                community=community,
                author=author,
                title=topic_data["title"],
                content=topic_data["content"],
                images=topic_data.get("images")
            )

            root_post = Post.objects.get(topic=topic, parent__isnull=True)
            if "replies" in topic_data:
                self._create_nested_replies(topic, root_post, topic_data["replies"])

    def _create_nested_replies(self, topic: Topic, parent_post: Post, replies: List[Dict[str, Any]]) -> None:
        """Рекурсивно создает ответы на посты любой степени вложенности."""
        for reply_data in replies:
            author = self.users_map[reply_data["author"]]
            
            new_reply = PostService.create_reply(
                topic=topic,
                author=author,
                content=reply_data["content"],
                parent=parent_post
            )

            if "replies" in reply_data:
                self._create_nested_replies(topic, new_reply, reply_data["replies"])