from flask_restplus import Namespace
from app.main.controller.controller import Controller
from app.main.service import b2b_ent_service as b2b_ent_service
import app.main.util.externalized_messages as messages
import app.main.util.controller_args as controller_args

api = Namespace("b2b_ent", description="B2B Enterprise recommendation api")


@api.route("/recommended_for_you", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="user_id", description=messages.descriptions["user_id"], type=int)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.b2b_args["recommend_for_you_args"]["error_message"]
    )
)
class RecommendForYou(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["recommend_for_you_args"],
        service=b2b_ent_service.get_b2b_ent_recommended_for_you,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/add_user_defined_trending_now", methods=["PUT"])
@api.param(name="rec_item_ids", description=messages.descriptions["rec_item_ids"])
@api.param(name="category_path", description=messages.descriptions["category_path"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.b2b_args["put_user_defined_trending_now_args"]["error_message"],
        example_value=messages.example_format["new_user_defined_trending_now"],
    )
)
class AddUserDefTrendingNow(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["put_user_defined_trending_now_args"],
        service=b2b_ent_service.put_b2b_ent_user_defined_trending_now,
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
        controller_args.b2b_args["trending_now_args"]["error_message"]
    )
)
class UserDefTrendingNow(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["trending_now_args"],
        service=b2b_ent_service.get_b2b_ent_user_defined_trending_now,
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
        controller_args.b2b_args["trending_now_args"]["error_message"]
    )
)
class TrendingNowModel(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["trending_now_args"],
        service=b2b_ent_service.get_b2b_ent_trending_now_model,
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
        controller_args.b2b_args["trending_now_args"]["error_message"]
    )
)
class TrendingNow(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["trending_now_args"],
        service=b2b_ent_service.get_b2b_ent_trending_now,
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
        controller_args.b2b_args["b2b_ent_trending_now_all_args"]["error_message"]
    )
)
class TrendingNowAll(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["b2b_ent_trending_now_all_args"],
        service=b2b_ent_service.get_b2b_ent_trending_now_all_category,
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
        controller_args.b2b_args["purchased_together_args"]["error_message"]
    )
)
class PurchasedTogether(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["purchased_together_args"],
        service=b2b_ent_service.get_b2b_ent_purchased_together,
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
        controller_args.b2b_args["similar_items_args"]["error_message"]
    )
)
class SimilarItems(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["similar_items_args"],
        service=b2b_ent_service.get_b2b_ent_similar_items,
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
        controller_args.b2b_args["featured_category_args"]["error_message"]
    )
)
class FeaturedCategory(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["featured_category_args"],
        service=b2b_ent_service.get_b2b_ent_featured_category,
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
        controller_args.b2b_args["buy_it_again_args"]["error_message"]
    )
)
class BuyItAgain(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["buy_it_again_args"],
        service=b2b_ent_service.get_b2b_ent_buy_it_again,
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
        controller_args.b2b_args["buy_it_again_args"]["error_message"]
    )
)
class BuyItAgainMPG(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["buy_it_again_args"],
        service=b2b_ent_service.get_b2b_ent_buy_it_again_mpg,
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
        controller_args.b2b_args["rec_for_you_search_args"]["error_message"]
    )
)
class RecForYouSearch(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["rec_for_you_search_args"],
        service=b2b_ent_service.get_b2b_ent_rec_for_you_search,
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
        controller_args.b2b_args["people_also_buy_args"]["error_message"]
    )
)
class PeopleAlsoBuy(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["people_also_buy_args"],
        service=b2b_ent_service.get_b2b_ent_people_also_buy,
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
        controller_args.b2b_args["seasonal_top_picks_args"]["error_message"]
    )
)
class SeasonalTopPicks(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["seasonal_top_picks_args"],
        service=b2b_ent_service.get_b2b_ent_seasonal_top_picks,
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
#         controller_args.b2b_args["recently_viewed_args"]["error_message"]
#     )
# )
# class RecentlyViewed(Controller):
#     def __init__(
#         self,
#         api,
#         args_dict=controller_args.b2b_args["recently_viewed_args"],
#         service=b2b_ent_service.get_b2b_ent_recently_viewed,
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
        controller_args.b2b_args["recently_viewed_streaming_args"]["error_message"]
    )
)
class RecentlyViewedStreaming(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["recently_viewed_streaming_args"],
        service=b2b_ent_service.get_b2b_ent_recently_viewed_streaming,
    ):
        Controller.__init__(self, args_dict, service)


@api.route("/project_use_this", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.param(name="item_id", description=messages.descriptions["item_id"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.b2b_args["project_use_this_args"]["error_message"]
    )
)
class ProjectUseThis(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["project_use_this_args"],
        service=b2b_ent_service.get_b2b_ent_project_use_this,
    ):
        Controller.__init__(self, args_dict, service)


# @api.route("/project_inspiration", methods=["GET"])
# @api.param(
#     name="candidate_count",
#     description=messages.descriptions["number_of_recommended_item_5"],
#     type=int,
# )
# @api.param(name="user_id", description=messages.descriptions["user_id"], type=int)
# @api.doc(
#     responses=messages.generate_api_responses(
#         controller_args.b2b_args["project_inspiration_args"]["error_message"]
#     )
# )
# class ProjectInspiration(Controller):
#     def __init__(
#         self,
#         api,
#         args_dict=controller_args.b2b_args["project_inspiration_args"],
#         service=b2b_ent_service.get_b2b_ent_project_inspiration,
#     ):
#         Controller.__init__(self, args_dict, service)


@api.route("/popular_item", methods=["GET"])
@api.param(
    name="candidate_count",
    description=messages.descriptions["number_of_recommended_item_5"],
    type=int,
)
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.b2b_args["popular_item_args"]["error_message"]
    )
)
class PopularItem(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["popular_item_args"],
        service=b2b_ent_service.get_b2b_ent_popular_item,
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
        controller_args.b2b_args["ent_search_people_also_buy_args"]["error_message"]
    )
)
class SearchPeopleAlsoBuy(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["ent_search_people_also_buy_args"],
        service=b2b_ent_service.get_b2b_ent_search_people_also_buy,
    ):
        Controller.__init__(self, args_dict, service)


search_rerank_model = api.model(
    "SearchRerank",
    {
        "items_id_list": controller_args.b2b_args["search_rerank_args"][
            "items_id_list"
        ],
        "order_history_list": controller_args.b2b_args["search_rerank_args"][
            "order_history_list"
        ],
        "order_history_weights": controller_args.b2b_args["search_rerank_args"][
            "order_history_weights"
        ],
    },
)


@api.route("/search_rerank", methods=["POST"])
@api.doc(
    responses=messages.generate_api_responses(
        controller_args.b2b_args["search_rerank_args"]["error_message"]
    )
)
@api.expect(search_rerank_model, validate=True)
class SearchRerank(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["search_rerank_args"],
        service=b2b_ent_service.post_b2b_ent_search_rerank,
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
        controller_args.b2b_args["you_may_also_buy_args"]["error_message"]
    )
)
class YouMayAlsoBuy(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["you_may_also_buy_args"],
        service=b2b_ent_service.get_b2b_ent_you_may_also_buy,
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
        controller_args.b2b_args["popular_search_keyword_args"]["error_message"]
    )
)
class PopularSearchKeyword(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["popular_search_keyword_args"],
        service=b2b_ent_service.get_b2b_ent_popular_search_keyword,
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
        controller_args.b2b_args["b2b_ent_purchased_together_bundle_args"][
            "error_message"
        ]
    )
)
class PurchasedTogetherBundle(Controller):
    def __init__(
        self,
        api,
        args_dict=controller_args.b2b_args["b2b_ent_purchased_together_bundle_args"],
        service=b2b_ent_service.get_b2b_ent_purchased_together_bundle,
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
#         controller_args.b2b_args["b2b_ent_streaming_trending_now_list_args"][
#             "error_message"
#         ]
#     )
# )
# class StreamingTrendingNowList(Controller):
#     def __init__(
#         self,
#         api,
#         args_dict=controller_args.b2b_args["b2b_ent_streaming_trending_now_list_args"],
#         service=b2b_ent_service.get_b2b_ent_streaming_trending_now_list,
#     ):
#         Controller.__init__(self, args_dict, service)
