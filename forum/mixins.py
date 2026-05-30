from typing import Any
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model
import logging


logger = logging.getLogger(__name__)
class ViewTrackerMixin:
    view_tracker_model:type[Model] | None = None
    view_tracker_kwarg:str = 'pk'
    session_key_prefix:str = 'viewed'
    kwargs: dict[str, Any]

    def get(self, request, *args, **kwargs):
        """Перехватываем GET-запрос для проверки сессии и начисления просмотра."""

        if self.view_tracker_model is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} требует определения атрибута 'view_tracker_model'."
            )
        
        obj_id = self.kwargs.get(self.view_tracker_kwarg)
        model_name = self.view_tracker_model.__name__.lower()
        session_key = f"{self.session_key_prefix}_{model_name}_{obj_id}"

        #Начисляю просмотры
        if not request.session.get(session_key, False):
            updated_count = self.view_tracker_model.objects.increment_views(obj_id) # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]

            if updated_count > 0:
                request.session[session_key] = True
            else:
                logger.warning(f"Попытка обновить просмотры для несуществующего {model_name} ID: {obj_id}")

        return super().get(request, *args, **kwargs)    # pyright: ignore[reportAttributeAccessIssue]