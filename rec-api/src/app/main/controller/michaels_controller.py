from flask_restplus import Namespace
from app.main.controller.controller import Controller
from app.main.service import michaels_service as michaels_service
import app.main.util.externalized_messages as messages
import app.main.util.controller_args as controller_args

api = Namespace("michaels", description="Michaels.com recommendation api")


@api.route("/recommended_for_you", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="user_id", description=messages.descriptions["user_id"], type=int)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["recommend_for_you_args"]["error_message"]
    )
)
class RecommendForYou(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["recommend_for_you_args"],
        service=michaels_service.get_michaels_recommended_for_you,
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
        controller_args.michaels_args["similar_items_args"]["error_message"]
    )
)
class SimilarItems(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["similar_items_args"],
        service=michaels_service.get_michaels_similar_items,
    ):
        Controller.__init__(self, args_dict, service)


# @api.route("/similar_ad_items", methods=["GET"])
# @api.param(
#     name="ad_candidate_count",
#     description=messages.descriptions["number_of_recommended_ad_item_5"],
#     type=int,
# )
# @api.param(name="item_id", description=messages.descriptions["item_id"])
# @api.doc(
#     responses=messages.generate_api_responses(
#         controller_args.michaels_args["similar_ad_items_args"]["error_message"]
#     )
# )
# class SimilarAdItems(Controller):
#     def __init__(
#         self,
#         api,
#         args_dict=controller_args.michaels_args["similar_ad_items_args"],
#         service=michaels_service.get_michaels_similar_ad_items,
#     ):
#         Controller.__init__(self, args_dict, service)


@api.route("/purchased_and_viewed_together", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="view_weight", description=messages.descriptions["view_weight"])
@api.param(name="item_id", description=messages.descriptions["item_id"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["purchased_and_viewed_together_args"][
            "error_message"
        ]
    )
)
class PurchasedAndViewedTogether(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["purchased_and_viewed_together_args"],
        service=michaels_service.get_michaels_purchased_and_viewed_together,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/purchased_together", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="item_id", description=messages.descriptions["item_id"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["purchased_together_args"]["error_message"]
    )
)
class PurchasedTogether(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["purchased_together_args"],
        service=michaels_service.get_michaels_purchased_together,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/viewed_together", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="item_id", description=messages.descriptions["item_id"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["viewed_together_args"]["error_message"]
    )
)
class ViewedTogether(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["viewed_together_args"],
        service=michaels_service.get_michaels_viewed_together,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/add_user_defined_trending_now", methods=["PUT"])
@api.param(name="rec_item_ids", description=messages.descriptions["rec_item_ids"])
@api.param(name="category_path", description=messages.descriptions["category_path"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["put_user_defined_trending_now_args"][
            "error_message"
        ],
        example_value=messages.example_format["new_user_defined_trending_now"],
    )
)
class AddUserDefTrendingNow(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["put_user_defined_trending_now_args"],
        service=michaels_service.put_michaels_user_defined_trending_now,
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
        controller_args.michaels_args["trending_now_args"]["error_message"]
    )
)
class UserDefTrendingNow(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["trending_now_args"],
        service=michaels_service.get_michaels_user_defined_trending_now,
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
        controller_args.michaels_args["trending_now_args"]["error_message"]
    )
)
class TrendingNowModel(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["trending_now_args"],
        service=michaels_service.get_michaels_trending_now_model,
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
        controller_args.michaels_args["trending_now_args"]["error_message"]
    )
)
class TrendingNow(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["trending_now_args"],
        service=michaels_service.get_michaels_trending_now,
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
        controller_args.michaels_args["trending_now_all_args"]["error_message"]
    )
)
class TrendingNowAll(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["trending_now_all_args"],
        service=michaels_service.get_michaels_trending_now_all_category,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/featured_category", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="user_id", description=messages.descriptions["user_id"], type=int)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["featured_category_args"]["error_message"]
    )
)
class FeaturedCategory(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["featured_category_args"],
        service=michaels_service.get_michaels_featured_category,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/buy_it_again", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="user_id", description=messages.descriptions["user_id"], type=int)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["buy_it_again_args"]["error_message"]
    )
)
class BuyItAgain(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["buy_it_again_args"],
        service=michaels_service.get_michaels_buy_it_again,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/buy_it_again_mpg", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="user_id", description=messages.descriptions["user_id"], type=int)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["buy_it_again_args"]["error_message"]
    )
)
class BuyItAgainMPG(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["buy_it_again_args"],
        service=michaels_service.get_michaels_buy_it_again_mpg,
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
        controller_args.michaels_args["rec_for_you_search_args"]["error_message"]
    )
)
class RecForYouSearch(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["rec_for_you_search_args"],
        service=michaels_service.get_michaels_rec_for_you_search,
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
        controller_args.michaels_args["people_also_buy_args"]["error_message"]
    )
)
class PeopleAlsoBuy(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["people_also_buy_args"],
        service=michaels_service.get_michaels_people_also_buy,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/people_also_view", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="item_id", description=messages.descriptions["item_id"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["people_also_view_args"]["error_message"]
    )
)
class PeopleAlsoView(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["people_also_view_args"],
        service=michaels_service.get_michaels_people_also_view,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/seasonal_top_picks", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["seasonal_top_picks_args"]["error_message"]
    )
)
class SeasonalTopPicks(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["seasonal_top_picks_args"],
        service=michaels_service.get_michaels_seasonal_top_picks,
    ):
        Controller.__init__(self, args_dict, service)


# @api.route("/recently_viewed", methods=["GET"])
# @api.param(
#     name="candidate_count",
#     description=messages.descriptions["number_of_recommended_item_5"],
#     type=int,
# )
# @api.param(name="user_id", description=messages.descriptions["user_id"], type=int)
# @api.doc(
#     responses=messages.generate_api_responses(
#         controller_args.michaels_args["recently_viewed_args"]["error_message"]
#     )
# )
# class RecentlyViewed(Controller):
#     def __init__(
#         self,
#         api,
#         args_dict=controller_args.michaels_args["recently_viewed_args"],
#         service=michaels_service.get_michaels_recently_viewed,
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
        controller_args.michaels_args["recently_viewed_streaming_args"]["error_message"]
    )
)
class RecentlyViewedStreaming(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["recently_viewed_streaming_args"],
        service=michaels_service.get_michaels_recently_viewed_streaming,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/project_use_this", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_projects_5"],
    type=int,
)
@api.param(name="item_id", description=messages.descriptions["item_id"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["project_use_this_args"]["error_message"]
    )
)
class ProjectUseThis(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["project_use_this_args"],
        service=michaels_service.get_michaels_project_use_this,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/project_inspiration", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_projects_5"],
    type=int,
)
@api.param(name="user_id", description=messages.descriptions["user_id"], type=int)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["project_inspiration_args"]["error_message"]
    )
)
class ProjectInspiration(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["project_inspiration_args"],
        service=michaels_service.get_michaels_project_inspiration,
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
        controller_args.michaels_args["trending_project_args"]["error_message"]
    )
)
class TrendingProject(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["trending_project_args"],
        service=michaels_service.get_michaels_trending_project,
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
        controller_args.michaels_args["popular_item_args"]["error_message"]
    )
)
class PopularItem(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["popular_item_args"],
        service=michaels_service.get_michaels_popular_item,
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
        controller_args.michaels_args["similar_projects_args"]["error_message"]
    )
)
class SimilarProjects(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["similar_projects_args"],
        service=michaels_service.get_michaels_similar_projects,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/similar_items_for_bundle", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="items_id_list", description=messages.descriptions["items_id_list"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["similar_items_for_bundle_args"]["error_message"]
    )
)
class SimilarItemsForBundle(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["similar_items_for_bundle_args"],
        service=michaels_service.get_michaels_similar_items_for_bundle,
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
        controller_args.michaels_args["similar_events_args"]["error_message"]
    )
)
class SimilarEvents(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["similar_events_args"],
        service=michaels_service.get_michaels_similar_events,
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
        controller_args.michaels_args["popular_event_args"]["error_message"]
    )
)
class PopularEvent(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["popular_event_args"],
        service=michaels_service.get_michaels_popular_event,
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
        controller_args.michaels_args["event_for_you_args"]["error_message"]
    )
)
class EventForYou(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["event_for_you_args"],
        service=michaels_service.get_michaels_event_for_you,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/popular_category", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_categories_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["popular_category_args"]["error_message"]
    )
)
class PopularCategory(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["popular_category_args"],
        service=michaels_service.get_michaels_popular_category,
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
        controller_args.michaels_args["popular_project_args"]["error_message"]
    )
)
class PopularProject(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["popular_project_args"],
        service=michaels_service.get_michaels_popular_project,
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
        controller_args.michaels_args["search_people_also_buy_args"]["error_message"]
    )
)
class SearchPeopleAlsoBuy(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["search_people_also_buy_args"],
        service=michaels_service.get_michaels_search_people_also_buy,
    ):
        Controller.__init__(self, args_dict, service)


search_rerank_model = api.model(
    "SearchRerank",
    {
        "items_id_list": controller_args.michaels_args["search_rerank_args"][
            "items_id_list"
        ],
        "order_history_list": controller_args.michaels_args["search_rerank_args"][
            "order_history_list"
        ],
        "order_history_weights": controller_args.michaels_args["search_rerank_args"][
            "order_history_weights"
        ],
    },
)


@api.route("/search_rerank", methods=["POST"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["search_rerank_args"]["error_message"]
    )
)
@api.expect(search_rerank_model, validate=True)
class SearchRerank(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["search_rerank_args"],
        service=michaels_service.post_michaels_search_rerank,
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
        controller_args.michaels_args["picks_from_experts_args"]["error_message"]
    )
)
class PicksfromExperts(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["picks_from_experts_args"],
        service=michaels_service.get_michaels_picks_from_experts,
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
        controller_args.michaels_args["you_may_also_buy_args"]["error_message"]
    )
)
class YouMayAlsoBuy(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["you_may_also_buy_args"],
        service=michaels_service.get_michaels_you_may_also_buy,
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
        controller_args.michaels_args["popular_search_keyword_args"]["error_message"]
    )
)
class PopularSearchKeyword(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["popular_search_keyword_args"],
        service=michaels_service.get_michaels_popular_search_keyword,
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
        controller_args.michaels_args["popular_item_by_store_args"]["error_message"]
    )
)
class PopularItemByStore(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["popular_item_by_store_args"],
        service=michaels_service.get_michaels_popular_item_by_store,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/purchased_together_bundle", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="items_id_list", description=messages.descriptions["items_id_list"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["purchased_together_bundle_args"]["error_message"]
    )
)
class PurchasedTogetherBundle(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["purchased_together_bundle_args"],
        service=michaels_service.get_michaels_purchased_together_bundle,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/favorite_item_for_you", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="user_id", description=messages.descriptions["user_id"], type=str)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["favorite_item_for_you_args"]["error_message"]
    )
)
class FavoriteItemForYou(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["favorite_item_for_you_args"],
        service=michaels_service.get_michaels_favorite_item_for_you,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/popular_products_in_projects", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["popular_products_in_projects"]["error_message"]
    )
)
class PopularProductsInProjects(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["popular_products_in_projects"],
        service=michaels_service.get_michaels_popular_products_in_projects,
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
        controller_args.michaels_args["top_picks_args"]["error_message"]
    )
)
class TopPicks(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["top_picks_args"],
        service=michaels_service.get_michaels_top_picks,
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
        controller_args.michaels_args["yesterday_popular_item_args"]["error_message"]
    )
)
class YesterdayPopularItem(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["yesterday_popular_item_args"],
        service=michaels_service.get_michaels_yesterday_popular_item,
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
        controller_args.michaels_args["new_projects"]["error_message"]
    )
)
class NewProjects(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["new_projects"],
        service=michaels_service.get_michaels_new_projects,
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
        controller_args.michaels_args["upcoming_event"]["error_message"]
    )
)
class UpcomingEvent(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["upcoming_event"],
        service=michaels_service.get_michaels_upcoming_event,
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
        controller_args.michaels_args["trending_event_args"]["error_message"]
    )
)
class TrendingEvent(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["trending_event_args"],
        service=michaels_service.get_michaels_trending_event,
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
        controller_args.michaels_args["popular_item_by_category_args"]["error_message"]
    )
)
class PopularItemByCategory(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["popular_item_by_category_args"],
        service=michaels_service.get_michaels_popular_item_by_category,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/popular_clearance_category", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["popular_clearance_category_args"][
            "error_message"
        ]
    )
)
class PopularClearanceCategory(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["popular_clearance_category_args"],
        service=michaels_service.get_michaels_popular_clearance_category,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/popular_clearance_item", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_events_5"],
    type=int,
)
@api.param(name="user_id", description=messages.descriptions["user_id"], type=str)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["popular_clearance_item_args"]["error_message"]
    )
)
class PopularClearanceItem(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["popular_clearance_item_args"],
        service=michaels_service.get_michaels_popular_clearance_item,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/popular_sale_category", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["popular_sale_category_args"]["error_message"]
    )
)
class PopularSaleCategory(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["popular_sale_category_args"],
        service=michaels_service.get_michaels_popular_sale_category,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/popular_sale_item", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_events_5"],
    type=int,
)
@api.param(name="user_id", description=messages.descriptions["user_id"], type=str)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["popular_sale_item_args"]["error_message"]
    )
)
class PopularSaleItem(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["popular_sale_item_args"],
        service=michaels_service.get_michaels_popular_sale_item,
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
        controller_args.michaels_args["popular_visited_events_args"]["error_message"]
    )
)
class PopularVisitedEvents(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["popular_visited_events_args"],
        service=michaels_service.get_michaels_popular_visited_events,
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
#         args_dict=controller_args.michaels_args["streaming_trending_now_list_args"],
#         service=michaels_service.get_michaels_streaming_trending_now_list,
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
        controller_args.michaels_args["popular_first_layer_category_args"][
            "error_message"
        ]
    )
)
class PopularFirstLayerCategory(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["popular_first_layer_category_args"],
        service=michaels_service.get_michaels_popular_first_layer_category,
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
        controller_args.michaels_args["popular_visited_projects_args"]["error_message"]
    )
)
class PopularVisitedProjects(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["popular_visited_projects_args"],
        service=michaels_service.get_michaels_popular_visited_projects,
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
        controller_args.michaels_args["popular_visited_items_args"]["error_message"]
    )
)
class PopularVisitedItems(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["popular_visited_items_args"],
        service=michaels_service.get_michaels_popular_visited_items,
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
        controller_args.michaels_args["shopping_cart_bundle_args"]["error_message"]
    )
)
class ShoppingCartBundle(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["shopping_cart_bundle_args"],
        service=michaels_service.get_michaels_shopping_cart_bundle,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/similar_items_in_same_store", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="item_id", description=messages.descriptions["item_id"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.michaels_args["similar_items_in_same_store_args"][
            "error_message"
        ]
    )
)
class SimilarItemsInSameStore(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["similar_items_in_same_store_args"],
        service=michaels_service.get_michaels_similar_items_in_same_store,
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
        controller_args.michaels_args["popular_products_in_events"]["error_message"]
    )
)
class PopularProductsInEvents(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["popular_products_in_events"],
        service=michaels_service.get_michaels_popular_products_in_events,
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
        controller_args.michaels_args["related_categories_by_category_args"][
            "error_message"
        ]
    )
)
class RelatedCategoriesByCategory(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["related_categories_by_category_args"],
        service=michaels_service.get_michaels_related_categories_by_category,
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
        controller_args.michaels_args["similar_items_by_popularity_args"][
            "error_message"
        ]
    )
)
class SimilarItemsByPopularity(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["similar_items_by_popularity_args"],
        service=michaels_service.get_michaels_similar_items_by_popularity,
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
        controller_args.michaels_args["related_queries_by_query_args"]["error_message"]
    )
)
class RelatedQueriesByQuery(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["related_queries_by_query_args"],
        service=michaels_service.get_michaels_related_queries_by_query,
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
        controller_args.michaels_args["related_queries_by_category_args"][
            "error_message"
        ]
    )
)
class RelatedQueriesByCategory(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["related_queries_by_category_args"],
        service=michaels_service.get_michaels_related_queries_by_category,
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
        controller_args.michaels_args["related_categories_by_query_args"][
            "error_message"
        ]
    )
)
class RelatedCategoriesByQuery(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.michaels_args["related_categories_by_query_args"],
        service=michaels_service.get_michaels_related_categories_by_query,
    ):
        Controller.__init__(self, args_dict, service)
