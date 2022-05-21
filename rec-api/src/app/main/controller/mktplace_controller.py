from flask_restplus import Namespace
from app.main.controller.controller import Controller
from app.main.service import mktplace_service as mktplace_service
import app.main.util.externalized_messages as messages
import app.main.util.controller_args as controller_args

api = Namespace("mktplace", description="Marketplace recommendation api")


@api.route("/recommended_for_you", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="user_id", description=messages.descriptions["user_id"], type=int)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["recommend_for_you_args"]["error_message"]
    )
)
class RecommendForYou(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["recommend_for_you_args"],
        service=mktplace_service.get_mktplace_recommended_for_you,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/similar_items", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_non_ad_item_5"],
    type=int,
)
@api.param(
    name="ad_candidate_count",
    description=messages.descriptions["number_of_recommended_ad_item_5"],
    type=int,
)
@api.param(name="item_id", description=messages.descriptions["item_id"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["similar_items_args"]["error_message"]
    )
)
class SimilarItems(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["similar_items_args"],
        service=mktplace_service.get_mktplace_similar_items,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/popular_item_by_store", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="store_id", description=messages.descriptions["store_id"], type=int)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["popular_item_by_store_args"]["error_message"]
    )
)
class PopularItemByStore(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["popular_item_by_store_args"],
        service=mktplace_service.get_mktplace_popular_item_by_store,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/popular_item", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["popular_item_args"]["error_message"]
    )
)
class PopularItem(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["popular_item_args"],
        service=mktplace_service.get_mktplace_popular_item,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/search_term_categories", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
)
@api.param(name="search_term", description=messages.descriptions["search_term"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["search_term_categories_args"]["error_message"],
        example_value=messages.example_format["search_term_cagetories"],
    )
)
class SearchTermCategories(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["search_term_categories_args"],
        service=mktplace_service.get_search_term_categories,
    ):
        Controller.__init__(self, args_dict, service)


# @api.route("/add_similar_items_for_new_product", methods=["PUT"])
# @api.param(
#     name="sku_number", description=messages.descriptions["new_product_sku_number"]
# )
# @api.doc(
#     responses=messages.generate_api_responses(
#         controller_args.mktplace_args["put_mktplace_similar_items_args"][
#             "error_message"
#         ],
#         example_value=messages.example_format["new_product_similar_items"],
#     )
# )
# class AddSimilarItemsForNewProduct(Controller):
#     def __init__(
#         self,
#         api,
#         args_dict=controller_args.mktplace_args["put_mktplace_similar_items_args"],
#         service=mktplace_service.put_mktplace_similar_items,
#     ):
#         Controller.__init__(self, args_dict, service)


# @api.route("/recently_viewed", methods=["GET"])
# @api.param(
#     name="candidate_count",
#     description=messages.descriptions["number_of_recommended_item_5"],
#     type=int,
# )
# @api.param(name="user_id", description=messages.descriptions["user_id"], type=int)
# @api.doc(
#     responses=messages.generate_api_responses(
#         controller_args.mktplace_args["recently_viewed_args"]["error_message"]
#     )
# )
# class RecentlyViewed(Controller):
#     def __init__(
#         self,
#         api,
#         args_dict=controller_args.mktplace_args["recently_viewed_args"],
#         service=mktplace_service.get_mktplace_recently_viewed,
#     ):
#         Controller.__init__(self, args_dict, service)


@api.route("/recently_viewed_streaming", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="user_id", description=messages.descriptions["user_id"], type=str)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["recently_viewed_streaming_args"]["error_message"]
    )
)
class RecentlyViewedStreaming(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["recently_viewed_streaming_args"],
        service=mktplace_service.get_mktplace_recently_viewed_streaming,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/search_people_also_buy", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="items_scores", description=messages.descriptions["items_scores"])
@api.param(name="items_id_list", description=messages.descriptions["items_id_list"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["search_people_also_buy_args"]["error_message"]
    )
)
class SearchPeopleAlsoBuy(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["search_people_also_buy_args"],
        service=mktplace_service.get_mktplace_search_people_also_buy,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/rec_for_you_search", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_search_term_5"],
    type=int,
)
@api.param(name="user_id", description=messages.descriptions["user_id"], type=int)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["rec_for_you_search_args"]["error_message"]
    )
)
class RecForYouSearch(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["rec_for_you_search_args"],
        service=mktplace_service.get_mktplace_rec_for_you_search,
    ):
        Controller.__init__(self, args_dict, service)


search_rerank_model = api.model(
    "SearchRerank",
    {
        "items_id_list": controller_args.mktplace_args["search_rerank_args"][
            "items_id_list"
        ],
        "order_history_list": controller_args.mktplace_args["search_rerank_args"][
            "order_history_list"
        ],
        "order_history_weights": controller_args.mktplace_args["search_rerank_args"][
            "order_history_weights"
        ],
    },
)


@api.route("/search_rerank", methods=["POST"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["search_rerank_args"]["error_message"]
    )
)
@api.expect(search_rerank_model, validate=True)
class SearchRerank(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["search_rerank_args"],
        service=mktplace_service.post_mktplace_search_rerank,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/add_user_defined_trending_now", methods=["PUT"])
@api.param(name="rec_item_ids", description=messages.descriptions["rec_item_ids"])
@api.param(name="category_path", description=messages.descriptions["category_path"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["put_user_defined_trending_now_args"][
            "error_message"
        ],
        example_value=messages.example_format["new_user_defined_trending_now"],
    )
)
class AddUserDefTrendingNow(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["put_user_defined_trending_now_args"],
        service=mktplace_service.put_mktplace_user_defined_trending_now,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/user_defined_trending_now", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="category_path", description=messages.descriptions["category_path"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["trending_now_args"]["error_message"]
    )
)
class UserDefTrendingNow(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["trending_now_args"],
        service=mktplace_service.get_mktplace_user_defined_trending_now,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/trending_now_model", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="category_path", description=messages.descriptions["category_path"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["trending_now_args"]["error_message"]
    )
)
class TrendingNowModel(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["trending_now_args"],
        service=mktplace_service.get_mktplace_trending_now_model,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/trending_now", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="category_path", description=messages.descriptions["category_path"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["trending_now_args"]["error_message"]
    )
)
class TrendingNow(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["trending_now_args"],
        service=mktplace_service.get_mktplace_trending_now,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/popular_event", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_events_5"],
    type=int,
)
@api.param(name="event_type", description=messages.descriptions["event_type"], type=str)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["popular_event_args"]["error_message"]
    )
)
class PopularEvent(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["popular_event_args"],
        service=mktplace_service.get_mktplace_popular_event,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/popular_project", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_projects_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["popular_project_args"]["error_message"]
    )
)
class PopularProject(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["popular_project_args"],
        service=mktplace_service.get_mktplace_popular_project,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/trending_project", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_projects_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["trending_project_args"]["error_message"]
    )
)
class TrendingProject(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["trending_project_args"],
        service=mktplace_service.get_mktplace_trending_project,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/trending_now_all_category", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["trending_now_all_args"]["error_message"]
    )
)
class TrendingNowAll(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["trending_now_all_args"],
        service=mktplace_service.get_mktplace_trending_now_all_category,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/you_may_also_buy", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="user_id", description=messages.descriptions["user_id"], type=str)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["you_may_also_buy_args"]["error_message"]
    )
)
class YouMayAlsoBuy(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["you_may_also_buy_args"],
        service=mktplace_service.get_mktplace_you_may_also_buy,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/popular_search_keyword", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_search_term_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["popular_search_keyword_args"]["error_message"]
    )
)
class PopularSearchKeyword(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["popular_search_keyword_args"],
        service=mktplace_service.get_mktplace_popular_search_keyword,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/shop_near_you", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_shops_5"],
    type=int,
)
@api.param(name="zip_code", description=messages.descriptions["zip_code"], type=str)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["shop_near_you_args"]["error_message"]
    )
)
class ShopNearYou(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["shop_near_you_args"],
        service=mktplace_service.get_mktplace_shop_near_you,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/top_picks", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="user_id", description=messages.descriptions["user_id"], type=str)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["top_picks_args"]["error_message"]
    )
)
class TopPicks(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["top_picks_args"],
        service=mktplace_service.get_mktplace_top_picks,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/event_for_you", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_events_5"],
    type=int,
)
@api.param(name="event_type", description=messages.descriptions["event_type"], type=str)
@api.param(name="user_id", description=messages.descriptions["user_id"], type=int)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["event_for_you_args"]["error_message"]
    )
)
class EventForYou(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["event_for_you_args"],
        service=mktplace_service.get_mktplace_event_for_you,
    ):
        Controller.__init__(self, args_dict, service)


# @api.route("/purchased_together_bundle", methods=["GET"])
# @api.param(
#     name="candidate_count",
#     description=messages.descriptions["number_of_recommended_item_5"],
#     type=int,
# )
# @api.param(name="items_id_list", description=messages.descriptions["items_id_list"])
# @api.doc(
#     responses=messages.generate_api_responses(
#         controller_args.mktplace_args["purchased_together_bundle_args"]["error_message"]
#     )
# )
# class PurchasedTogetherBundle(Controller):
#     def __init__(
#         self,
#         api,
#         args_dict=controller_args.mktplace_args["purchased_together_bundle_args"],
#         service=mktplace_service.get_mktplace_purchased_together_bundle,
#     ):
#         Controller.__init__(self, args_dict, service)


@api.route("/popular_products_in_projects", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["popular_products_in_projects"]["error_message"]
    )
)
class PopularProductsInProjects(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["popular_products_in_projects"],
        service=mktplace_service.get_mktplace_popular_products_in_projects,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/yesterday_popular_item", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["yesterday_popular_item_args"]["error_message"]
    )
)
class YesterdayPopularItem(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["yesterday_popular_item_args"],
        service=mktplace_service.get_mktplace_yesterday_popular_item,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/new_projects", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["new_projects"]["error_message"]
    )
)
class NewProjects(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["new_projects"],
        service=mktplace_service.get_mktplace_new_projects,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/favorite_item", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["favorite_item_args"]["error_message"]
    )
)
class FavoriteItem(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["favorite_item_args"],
        service=mktplace_service.get_mktplace_favorite_item,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/upcoming_event", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="event_type", description=messages.descriptions["event_type"], type=str)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["upcoming_event"]["error_message"]
    )
)
class UpcomingEvent(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["upcoming_event"],
        service=mktplace_service.get_mktplace_upcoming_event,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/trending_event", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_events_5"],
    type=int,
)
@api.param(name="event_type", description=messages.descriptions["event_type"], type=str)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["trending_event_args"]["error_message"]
    )
)
class TrendingEvent(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["trending_event_args"],
        service=mktplace_service.get_mktplace_trending_event,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/popular_visited_events", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="event_type", description=messages.descriptions["event_type"], type=str)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["popular_visited_events_args"]["error_message"]
    )
)
class PopularVisitedEvents(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["popular_visited_events_args"],
        service=mktplace_service.get_mktplace_popular_visited_events,
    ):
        Controller.__init__(self, args_dict, service)


# @api.route("/streaming_trending_now_list", methods=["GET"])
# @api.param(
#     name="candidate_count",
#     description=messages.descriptions["number_of_recommended_events_5"],
#     type=int,
# )
# @api.doc(
#     responses=messages.generate_api_responses(
#         controller_args.michaels_args["streaming_trending_now_list_args"][
#             "error_message"
#         ]
#     )
# )
# class StreamingTrendingNowList(Controller):
#     def __init__(
#         self,
#         api,
#         args_dict=controller_args.mktplace_args["streaming_trending_now_list_args"],
#         service=mktplace_service.get_mktplace_streaming_trending_now_list,
#     ):
#         Controller.__init__(self, args_dict, service)


@api.route("/popular_first_layer_category", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["popular_first_layer_category_args"][
            "error_message"
        ]
    )
)
class PopularFirstLayerCategory(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["popular_first_layer_category_args"],
        service=mktplace_service.get_mktplace_popular_first_layer_category,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/people_also_buy", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="item_id", description=messages.descriptions["item_id"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["people_also_buy_args"]["error_message"]
    )
)
class PeopleAlsoBuy(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["people_also_buy_args"],
        service=mktplace_service.get_mktplace_people_also_buy,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/popular_visited_projects", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["popular_visited_projects_args"]["error_message"]
    )
)
class PopularVisitedProjects(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["popular_visited_projects_args"],
        service=mktplace_service.get_mktplace_popular_visited_projects,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/popular_visited_items", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["popular_visited_items_args"]["error_message"]
    )
)
class PopularVisitedItems(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["popular_visited_items_args"],
        service=mktplace_service.get_mktplace_popular_visited_items,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/shopping_cart_bundle", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="items_id_list", description=messages.descriptions["items_id_list"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["shopping_cart_bundle_args"]["error_message"]
    )
)
class ShoppingCartBundle(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["shopping_cart_bundle_args"],
        service=mktplace_service.get_mktplace_shopping_cart_bundle,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/popular_products_in_events", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["popular_products_in_events"]["error_message"]
    )
)
class PopularProductsInEvents(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["popular_products_in_events"],
        service=mktplace_service.get_mktplace_popular_products_in_events,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/similar_projects", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_projects_5"],
    type=int,
)
@api.param(name="external_id", description=messages.descriptions["external_id"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["similar_projects_args"]["error_message"]
    )
)
class SimilarProjects(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["similar_projects_args"],
        service=mktplace_service.get_mktplace_similar_projects,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/related_categories_by_category", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="category_path", description=messages.descriptions["category_path"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["related_categories_by_category_args"][
            "error_message"
        ]
    )
)
class RelatedCategoriesByCategory(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["related_categories_by_category_args"],
        service=mktplace_service.get_mktplace_related_categories_by_category,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/popular_item_by_category", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="category_path", description=messages.descriptions["category_path"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["popular_item_by_category_args"]["error_message"]
    )
)
class PopularItemByCategory(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["popular_item_by_category_args"],
        service=mktplace_service.get_mktplace_popular_item_by_category,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/similar_events", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_events_5"],
    type=int,
)
@api.param(name="event_type", description=messages.descriptions["event_type"], type=str)
@api.param(name="event_id", description=messages.descriptions["event_id"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["similar_events_args"]["error_message"]
    )
)
class SimilarEvents(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["similar_events_args"],
        service=mktplace_service.get_mktplace_similar_events,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/similar_items_by_popularity", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="item_id", description=messages.descriptions["item_id"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["similar_items_by_popularity_args"][
            "error_message"
        ]
    )
)
class SimilarItemsByPopularity(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["similar_items_by_popularity_args"],
        service=mktplace_service.get_mktplace_similar_items_by_popularity,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/related_queries_by_query", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="query_keyword", description=messages.descriptions["query_keyword"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["related_queries_by_query_args"]["error_message"]
    )
)
class RelatedQueriesByQuery(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["related_queries_by_query_args"],
        service=mktplace_service.get_mktplace_related_queries_by_query,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/related_queries_by_category", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="category_path", description=messages.descriptions["category_path"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["related_queries_by_category_args"][
            "error_message"
        ]
    )
)
class RelatedQueriesByCategory(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["related_queries_by_category_args"],
        service=mktplace_service.get_mktplace_related_queries_by_category,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/related_categories_by_query", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="query_keyword", description=messages.descriptions["query_keyword"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["related_categories_by_query_args"][
            "error_message"
        ]
    )
)
class RelatedCategoriesByQuery(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["related_categories_by_query_args"],
        service=mktplace_service.get_mktplace_related_categories_by_query,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/picks_from_experts", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(
    name="category_count",
    description=messages.descriptions["number_of_recommended_categories_5"],
    type=int,
)
@api.param(name="user_id", description=messages.descriptions["user_id"], type=int)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.mktplace_args["picks_from_experts_args"]["error_message"]
    )
)
class PicksfromExperts(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.mktplace_args["picks_from_experts_args"],
        service=mktplace_service.get_mktplace_picks_from_experts,
    ):
        Controller.__init__(self, args_dict, service)
