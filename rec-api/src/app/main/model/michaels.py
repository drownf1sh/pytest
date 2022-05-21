from app.main.database.mongodb import db


class ItemSimilarity(db.Document):
    """
    Define data object for mik_similar_items collection
    """

    # Meta variables.
    meta = {"collection": "mik_similar_items"}

    # Document variables.
    item_id = db.StringField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PurchaseBundle(db.Document):
    """
    Define data object for mik_purchased_together collection
    """

    # Meta variables.
    meta = {"collection": "mik_purchased_together"}

    # Document variables.
    item_id = db.StringField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class ViewedTogether(db.Document):
    """
    Define data object for mik_viewed_together collection
    """

    # Meta variables.
    meta = {"collection": "mik_viewed_together"}

    # Document variables.
    item_id = db.StringField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class UserDefTrendingNow(db.Document):
    """
    Define data object for mik_user_defined_trending_now collection
    """

    # Meta variables.
    meta = {"collection": "mik_user_defined_trending_now"}

    # Document variables.
    category_path = db.StringField(required=True)
    recommendations = db.ListField()


class TrendingNowModel(db.Document):
    """
    Define data object for mik_trending_now collection
    """

    # Meta variables.
    meta = {"collection": "mik_trending_now"}

    # Document variables.
    category_path = db.StringField(required=True)
    recommendations = db.ListField()


class UserRecommend(db.Document):
    """
    Define data object for mik_recommended_for_you collection
    """

    # Meta variables.
    meta = {"collection": "mik_recommended_for_you"}

    # Document variables.
    user_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class FeaturedCategory(db.Document):
    """
    Define data object for mik_featured_category collection
    """

    # Meta variables.
    meta = {"collection": "mik_featured_category"}

    # Document variables.
    user_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class BuyItAgain(db.Document):
    """
    Define data object for mik_buy_it_again_atd collection
    """

    # Meta variables.
    meta = {"collection": "mik_buy_it_again_atd"}

    # Document variables.
    user_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class BuyItAgainMPG(db.Document):
    """
    Define data object for mik_buy_it_again_mpg collection
    """

    # Meta variables.
    meta = {"collection": "mik_buy_it_again_mpg"}

    # Document variables.
    user_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class RecForYouSearch(db.Document):
    """
    Define data object for mik_rec_for_you_search collection
    """

    # Meta variables.
    meta = {"collection": "mik_rec_for_you_search"}

    # Document variables.
    user_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class FavoriteItemForYou(db.Document):
    """
    Define data object for mik_favorite_item_for_you collection
    """

    # Meta variables.
    meta = {"collection": "mik_favorite_item_for_you"}

    # Document variables.
    user_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PeopleAlsoBuy(db.Document):
    """
    Define data object for mik_people_also_buy collection
    """

    # Meta variables.
    meta = {"collection": "mik_people_also_buy"}

    # Document variables.
    item_id = db.StringField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PeopleAlsoView(db.Document):
    """
    Define data object for mik_people_also_view collection
    """

    # Meta variables.
    meta = {"collection": "mik_people_also_view"}

    # Document variables.
    item_id = db.StringField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class SeasonalTopPicks(db.Document):
    """
    Define data object for mik_seasonal_top_picks collection
    """

    # Meta variables.
    meta = {"collection": "mik_seasonal_top_picks"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class ProjectUseThis(db.Document):
    """
    Define data object for mik_project_use_this collection
    """

    # Meta variables.
    meta = {"collection": "mik_project_use_this"}

    # Document variables.
    item_id = db.StringField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class ProjectInspiration(db.Document):
    """
    Define data object for mik_project_inspiration collection
    """

    # Meta variables.
    meta = {"collection": "mik_project_inspiration"}

    # Document variables.
    user_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PopularItem(db.Document):
    """
    Define data object for mik_popular_item collection
    """

    # Meta variables.
    meta = {"collection": "mik_popular_item"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class ProjectSimilarity(db.Document):
    """
    Define data object for mik_similar_projects collection
    """

    # Meta variables.
    meta = {"collection": "mik_similar_projects"}

    # Document variables.
    external_id = db.StringField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class EventForYou(db.Document):
    """
    Define data object for mik_event_for_you collection
    """

    # Meta variables.
    meta = {"collection": "mik_event_for_you"}

    # Document variables.
    user_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class SimilarEvents(db.Document):
    """
    Define data object for mik_similar_events collection
    """

    # Meta variables.
    meta = {"collection": "mik_similar_events"}

    # Document variables.
    event_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PopularEvent(db.Document):
    """
    Define data object for mik_popular_event collection
    """

    # Meta variables.
    meta = {"collection": "mik_popular_event"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PopularCategory(db.Document):
    """
    Define data object for mik_popular_category collection
    """

    # Meta variables.
    meta = {"collection": "mik_popular_category"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PopularProject(db.Document):
    """
    Define data object for mik_popular_project collection
    """

    # Meta variables.
    meta = {"collection": "mik_popular_project"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class FeaturedFirstLayerCategoryByUser(db.Document):
    """
    Define data object for mik_popular_first_layer_category_by_user collection
    """

    # Meta variables.
    meta = {"collection": "mik_popular_first_layer_category_by_user"}

    # Document variables.
    user_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PopularFirstLayerCategory(db.Document):
    """
    Define data object for mik_popular_first_layer_category collection
    """

    # Meta variables.
    meta = {"collection": "mik_popular_first_layer_category"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class YouMayAlsoBuy(db.Document):
    """
    Define data object for mik_you_may_also_buy collection
    """

    # Meta variables.
    meta = {"collection": "mik_you_may_also_buy"}

    # Document variables.
    user_id = db.StringField(required=True)
    recommendations = db.ListField()


class PopularSearchKeyword(db.Document):
    """
    Define data object for mik_popular_search_keyword collection
    """

    # Meta variables.
    meta = {"collection": "mik_popular_search_keyword"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PopularItemByStore(db.Document):
    """
    Define data object for mik_popular_item_by_store collection
    """

    # Meta variables.
    meta = {"collection": "mik_popular_item_by_store"}

    # Document variables.
    store_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PopularProductsInProjects(db.Document):
    """
    Define data object for mik_popular_products_in_projects collection
    """

    # Meta variables.
    meta = {"collection": "mik_popular_products_in_projects"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class YesterdayPopularItem(db.Document):
    """
    Define data object for mik_yesterday_popular_item collection
    """

    # Meta variables.
    meta = {"collection": "mik_yesterday_popular_item"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class NewProjects(db.Document):
    """
    Define data object for mik_new_projects collection
    """

    # Meta variables.
    meta = {"collection": "mik_new_projects"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()


class UpcomingEvent(db.Document):
    """
    Define data object for mik_upcoming_event collection
    """

    # Meta variables.
    meta = {"collection": "mik_upcoming_event"}

    # Document variables.
    timestamp = db.IntField(required=True)
    events_id = db.ListField()
    schedules_id = db.ListField()


class TrendingEvent(db.Document):
    """
    Define data object for mik_trending_event collection
    """

    # Meta variables.
    meta = {"collection": "mik_trending_event"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PopularClearanceCategory(db.Document):
    """
    Define data object for mik_popular_clearance_category collection
    """

    # Meta variables.
    meta = {"collection": "mik_popular_clearance_category"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PopularClearanceItem(db.Document):
    """
    Define data object for mik_popular_clearance_item collection
    """

    # Meta variables.
    meta = {"collection": "mik_popular_clearance_item"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PopularSaleCategory(db.Document):
    """
    Define data object for mik_popular_sale_category collection
    """

    # Meta variables.
    meta = {"collection": "mik_popular_sale_category"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PopularSaleItem(db.Document):
    """
    Define data object for mik popular_sale_item collection
    """

    # Meta variables.
    meta = {"collection": "mik_popular_sale_item"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PopularVisitedEvents(db.Document):
    """
    Define data object for mik_popular_visited_events collection
    """

    # Meta variables.
    meta = {"collection": "mik_popular_visited_events"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class FavoriteItem(db.Document):
    """
    Define data object for mik_favorite_item collection
    """

    # Meta variables.
    meta = {"collection": "mik_favorite_item"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PopularVisitedProjects(db.Document):
    """
    Define data object for mik_popular_visited_projects collection
    """

    # Meta variables.
    meta = {"collection": "mik_popular_visited_projects"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class TrendingProject(db.Document):
    """
    Define data object for mik_trending_project collection
    """

    # Meta variables.
    meta = {"collection": "mik_trending_project"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PopularVisitedItems(db.Document):
    """
    Define data object for mik_popular_visited_items collection
    """

    # Meta variables.
    meta = {"collection": "mik_popular_viewed_item_pyspark"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class SimilarItemsInSameStore(db.Document):
    """
    Define data object for ea_same_store_similar_items collection
    """

    # Meta variables.
    meta = {"collection": "ea_same_store_similar_items"}

    # Document variables.
    item_id = db.StringField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PopularProductsInEvents(db.Document):
    """
    Define data object for mik_popular_products_in_events collection
    """

    # Meta variables.
    meta = {"collection": "mik_popular_products_in_events"}

    # Document variables.
    group_id = db.IntField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class RelatedCategoriesByCategory(db.Document):
    """
    Define data object for mik_related_categories_by_category collection
    """

    # Meta variables.
    meta = {"collection": "mik_related_categories_by_category"}

    # Document variables.
    category_path = db.StringField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class PopularItemByCategory(db.Document):
    """
    Define data object for mik_popular_item_by_category collection
    """

    # Meta variables.
    meta = {"collection": "mik_popular_item_by_category"}

    # Document variables.
    category_path = db.StringField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class RelatedQueriesByQuery(db.Document):
    """
    Define data object for mik_related_queries_by_query collection
    """

    # Meta variables.
    meta = {"collection": "mik_related_queries_by_query"}

    # Document variables.
    query = db.StringField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class RelatedQueriesByCategory(db.Document):
    """
    Define data object for mik_related_queries_by_category collection
    """

    # Meta variables.
    meta = {"collection": "mik_related_queries_by_category"}

    # Document variables.
    category_path = db.StringField(required=True)
    recommendations = db.ListField()
    score = db.ListField()


class RelatedCategoriesByQuery(db.Document):
    """
    Define data object for mik_related_categories_by_query collection
    """

    # Meta variables.
    meta = {"collection": "mik_related_categories_by_query"}

    # Document variables.
    query = db.StringField()
    recommendations = db.ListField()
    score = db.ListField()
