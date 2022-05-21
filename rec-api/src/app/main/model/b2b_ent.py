from app.main.database.mongodb import db


class ItemSimilarity(db.Document):
    """
    Define data object for b2b_similar_items collection
    """

    # Meta variables.
    meta = {"collection": "b2b_similar_items"}

    # Document variables.
    item_id = db.StringField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PurchaseBundle(db.Document):
    """
    Define data object for b2b_ent_purchased_together collection
    """

    # Meta variables.
    meta = {"collection": "b2b_ent_purchased_together"}

    # Document variables.
    item_id = db.StringField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class UserDefTrendingNow(db.Document):
    """
    Define data object for b2b_ent_user_defined_trending_now collection
    """

    # Meta variables.
    meta = {"collection": "b2b_ent_user_defined_trending_now"}

    # Document variables.
    category_path = db.StringField(required=True)
    recommendations = db.ListField()


class TrendingNowModel(db.Document):
    """
    Define data object for b2b_ent_trending_now collection
    """

    # Meta variables.
    meta = {"collection": "b2b_ent_trending_now"}

    # Document variables.
    category_path = db.StringField(required=True)
    recommendations = db.ListField()


class UserRecommend(db.Document):
    """
    Define data object for b2b_ent_recommended_for_you collection
    """

    # Meta variables.
    meta = {"collection": "b2b_ent_recommended_for_you"}

    # Document variables.
    user_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class FeaturedCategory(db.Document):
    """
    Define data object for b2b_ent_featured_category collection
    """

    # Meta variables.
    meta = {"collection": "b2b_ent_featured_category"}

    # Document variables.
    user_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class BuyItAgain(db.Document):
    """
    Define data object for b2b_ent_buy_it_again_atd collection
    """

    # Meta variables.
    meta = {"collection": "b2b_ent_buy_it_again_atd"}

    # Document variables.
    user_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class BuyItAgainMPG(db.Document):
    """
    Define data object for b2b_ent_buy_it_again_mpg collection
    """

    # Meta variables.
    meta = {"collection": "b2b_ent_buy_it_again_mpg"}

    # Document variables.
    user_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class RecForYouSearch(db.Document):
    """
    Define data object for b2b_ent_rec_for_you_search collection
    """

    # Meta variables.
    meta = {"collection": "b2b_ent_rec_for_you_search"}

    # Document variables.
    user_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PeopleAlsoBuy(db.Document):
    """
    Define data object for b2b_ent_people_also_buy collection
    """

    # Meta variables.
    meta = {"collection": "b2b_ent_people_also_buy"}

    # Document variables.
    item_id = db.StringField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class SeasonalTopPicks(db.Document):
    """
    Define data object for b2b_ent_seasonal_top_picks collection
    """

    # Meta variables.
    meta = {"collection": "b2b_ent_seasonal_top_picks"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class ProjectUseThis(db.Document):
    """
    Define data object for b2b_ent_project_use_this collection
    """

    # Meta variables.
    meta = {"collection": "b2b_ent_project_use_this"}

    # Document variables.
    item_id = db.StringField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class ProjectInspiration(db.Document):
    """
    Define data object for b2b_ent_project_inspiration collection
    """

    # Meta variables.
    meta = {"collection": "b2b_ent_project_inspiration"}

    # Document variables.
    user_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PopularItem(db.Document):
    """
    Define data object for b2b_ent_popular_item collection
    """

    # Meta variables.
    meta = {"collection": "b2b_ent_popular_item"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class YouMayAlsoBuy(db.Document):
    """
    Define data object for b2b_ent_you_may_also_buy collection
    """

    # Meta variables.
    meta = {"collection": "b2b_ent_you_may_also_buy"}

    # Document variables.
    user_id = db.StringField(required=True)
    recommendations = db.ListField()


class PopularSearchKeyword(db.Document):
    """
    Define data object for b2b_popular_search_keyword collection
    """

    # Meta variables.
    meta = {"collection": "b2b_popular_search_keyword"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()
