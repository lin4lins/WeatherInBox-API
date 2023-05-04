from celery import shared_task

from api.models import Subscription


@shared_task()
def task_execute(task_params):
    sub = Subscription.objects.get(pk=task_params["sub_id"])
    print(f'{sub.user_id=}')
    return sub.city.name
