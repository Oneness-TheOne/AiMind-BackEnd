from datetime import datetime


def serialize_post(post):
    if post is None:
        return None
    return {
        "id": post.id,
        "text": post.text,
        "userIdx": post.userIdx,
        "name": post.name,
        "userid": post.userid,
        "url": post.url,
        "createdAt": _format_dt(post.createdAt),
        "updatedAt": _format_dt(post.updatedAt),
    }


def serialize_posts(posts):
    return [serialize_post(post) for post in posts]


def _format_dt(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value
