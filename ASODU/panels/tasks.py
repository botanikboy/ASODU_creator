from celery import shared_task


@shared_task
def add(x, y):
    print('task in proccess')
    return x + y
