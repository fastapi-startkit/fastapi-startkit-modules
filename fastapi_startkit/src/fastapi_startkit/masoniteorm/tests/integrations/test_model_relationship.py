# TODO:
# from fastapi_startkit.masoniteorm.relationships import HasMany
#
# One To One/Has One
# One To Many/ Has many
# One to Many/Inverse (Belongs to)
# Many To Many (belongTomany)
# One To One (Polymorphic)morphTo, MorphOne
# One To Many (Polymorphic), morphMany
# Many To Many (Polymorphic), morphToMany
#
# Expected syntax
#
# ```
# class User:
#     posts: List[Post] = HasMany()
#
# ````
# do query
#
# user = User.find(1)
# user.posts().where('active', 1).get()
