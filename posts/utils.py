from accounts import models as account_models


def add_points(user, activity_name):
    """
    Method is used for the add points on their activity
    :param user:
    :param activity_name:
    :return: None
    """
    try:
        activity = account_models.ActivityPoints.objects.create(
            activity_name=activity_name,
            points=account_models.Points.objects.get(activity_name=activity_name).points,
            user=user
        )
        activity.save()
    except:
        pass
