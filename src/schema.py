"""GraphQL schema for Hashnode API."""
import sgqlc.types
import sgqlc.types.datetime
import sgqlc.types.relay

schema = sgqlc.types.Schema()


# Unexport Node/PageInfo, let schema re-declare them
schema -= sgqlc.types.relay.Node
schema -= sgqlc.types.relay.PageInfo


########################################################################
# Scalars and Enumerations
########################################################################
Boolean = sgqlc.types.Boolean
DateTime = sgqlc.types.datetime.DateTime
ID = sgqlc.types.ID
String = sgqlc.types.String
Int = sgqlc.types.Int


class ObjectId(sgqlc.types.Scalar):
    __schema__ = schema


# class SortOrder(sgqlc.types.Enum):
#     __schema__ = schema
#     __choices__ = ("asc", "dsc")


# class TagPostsSort(sgqlc.types.Enum):
#     __schema__ = schema
#     __choices__ = ("popular", "recent", "trending")


# class TimePeriod(sgqlc.types.Enum):
#     __schema__ = schema
#     __choices__ = ("LAST_N_DAYS", "LAST_N_HOURS", "LAST_N_MONTHS", "LAST_N_WEEKS", "LAST_N_YEARS")


# class URL(sgqlc.types.Scalar):
#     __schema__ = schema


class UrlPattern(sgqlc.types.Enum):
    __schema__ = schema
    __choices__ = ("DEFAULT", "SIMPLE")


########################################################################
# Input Objects
########################################################################
# class AbsoluteTimeRange(sgqlc.types.Input):
#     __schema__ = schema
#     __field_names__ = ("from_", "to")
#     from_ = sgqlc.types.Field(DateTime, graphql_name="from")
#     to = sgqlc.types.Field(DateTime, graphql_name="to")


class CoverImageOptionsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "cover_image_url",
        "is_cover_attribution_hidden",
        "cover_image_attribution",
        "cover_image_photographer",
        "stick_cover_to_bottom",
    )
    cover_image_url = sgqlc.types.Field(String, graphql_name="coverImageURL")
    is_cover_attribution_hidden = sgqlc.types.Field(Boolean, graphql_name="isCoverAttributionHidden")
    cover_image_attribution = sgqlc.types.Field(String, graphql_name="coverImageAttribution")
    cover_image_photographer = sgqlc.types.Field(String, graphql_name="coverImagePhotographer")
    stick_cover_to_bottom = sgqlc.types.Field(Boolean, graphql_name="stickCoverToBottom")


class PublicationPostConnectionFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("tags", "tag_slugs", "exclude_pinned_post", "deleted_only")
    tags = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ObjectId)), graphql_name="tags")
    tag_slugs = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="tagSlugs")
    exclude_pinned_post = sgqlc.types.Field(Boolean, graphql_name="excludePinnedPost")
    deleted_only = sgqlc.types.Field(Boolean, graphql_name="deletedOnly")


class PublicationPostsViaPageFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("tags", "tag_slugs", "exclude_pinned_posts")
    tags = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="tags")
    tag_slugs = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="tagSlugs")
    exclude_pinned_posts = sgqlc.types.Field(Boolean, graphql_name="excludePinnedPosts")


class PublishPostInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "title",
        "subtitle",
        "publication_id",
        "content_markdown",
        "published_at",
        "cover_image_options",
        "slug",
        "original_article_url",
        "tags",
        "disable_comments",
        "publish_as",
        "series_id",
        "settings",
        "co_authors",
    )
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="title")
    subtitle = sgqlc.types.Field(String, graphql_name="subtitle")
    publication_id = sgqlc.types.Field(sgqlc.types.non_null(ObjectId), graphql_name="publicationId")
    content_markdown = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="contentMarkdown")
    published_at = sgqlc.types.Field(DateTime, graphql_name="publishedAt")
    cover_image_options = sgqlc.types.Field(CoverImageOptionsInput, graphql_name="coverImageOptions")
    slug = sgqlc.types.Field(String, graphql_name="slug")
    original_article_url = sgqlc.types.Field(String, graphql_name="originalArticleURL")
    tags = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null("PublishPostTagInput")), graphql_name="tags")
    disable_comments = sgqlc.types.Field(Boolean, graphql_name="disableComments")
    publish_as = sgqlc.types.Field(ObjectId, graphql_name="publishAs")
    series_id = sgqlc.types.Field(ObjectId, graphql_name="seriesId")
    settings = sgqlc.types.Field("PublishPostSettingsInput", graphql_name="settings")
    co_authors = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ObjectId)), graphql_name="coAuthors")


class PublishPostSettingsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("scheduled", "enable_table_of_content", "slug_overridden", "delisted")
    scheduled = sgqlc.types.Field(Boolean, graphql_name="scheduled")
    enable_table_of_content = sgqlc.types.Field(Boolean, graphql_name="enableTableOfContent")
    slug_overridden = sgqlc.types.Field(Boolean, graphql_name="slugOverridden")
    delisted = sgqlc.types.Field(Boolean, graphql_name="delisted")


class PublishPostTagInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("id", "slug", "name")
    id = sgqlc.types.Field(ObjectId, graphql_name="id")
    slug = sgqlc.types.Field(String, graphql_name="slug")
    name = sgqlc.types.Field(String, graphql_name="name")


# class RelativeTimeRange(sgqlc.types.Input):
#     __schema__ = schema
#     __field_names__ = ("relative", "n")
#     relative = sgqlc.types.Field(sgqlc.types.non_null(TimePeriod), graphql_name="relative")
#     n = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="n")


class RemovePostInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("id",)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")


class RestorePostInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("id",)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")


class SearchPostsOfPublicationFilter(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("query", "publication_id", "deleted_only", "author_ids", "tag_ids", "time")
    query = sgqlc.types.Field(String, graphql_name="query")
    publication_id = sgqlc.types.Field(sgqlc.types.non_null(ObjectId), graphql_name="publicationId")
    deleted_only = sgqlc.types.Field(Boolean, graphql_name="deletedOnly")
    author_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="authorIds")
    tag_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="tagIds")
    time = sgqlc.types.Field("TimeFilter", graphql_name="time")


# class TagPostConnectionFilter(sgqlc.types.Input):
#     __schema__ = schema
#     __field_names__ = ("sort_by",)
#     sort_by = sgqlc.types.Field(TagPostsSort, graphql_name="sortBy")


# class TimeFilter(sgqlc.types.Input):
#     __schema__ = schema
#     __field_names__ = ("absolute", "relative")
#     absolute = sgqlc.types.Field(AbsoluteTimeRange, graphql_name="absolute")
#     relative = sgqlc.types.Field(RelativeTimeRange, graphql_name="relative")


class UpdatePostInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = (
        "id",
        "title",
        "subtitle",
        "content_markdown",
        "published_at",
        "cover_image_options",
        "slug",
        "original_article_url",
        "tags",
        "publish_as",
        "co_authors",
        "series_id",
        "settings",
        "publication_id",
    )
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    title = sgqlc.types.Field(String, graphql_name="title")
    subtitle = sgqlc.types.Field(String, graphql_name="subtitle")
    content_markdown = sgqlc.types.Field(String, graphql_name="contentMarkdown")
    published_at = sgqlc.types.Field(DateTime, graphql_name="publishedAt")
    cover_image_options = sgqlc.types.Field(CoverImageOptionsInput, graphql_name="coverImageOptions")
    slug = sgqlc.types.Field(String, graphql_name="slug")
    original_article_url = sgqlc.types.Field(String, graphql_name="originalArticleURL")
    tags = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(PublishPostTagInput)), graphql_name="tags")
    publish_as = sgqlc.types.Field(ObjectId, graphql_name="publishAs")
    co_authors = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ObjectId)), graphql_name="coAuthors")
    series_id = sgqlc.types.Field(ObjectId, graphql_name="seriesId")
    settings = sgqlc.types.Field("UpdatePostSettingsInput", graphql_name="settings")
    publication_id = sgqlc.types.Field(ObjectId, graphql_name="publicationId")


class UpdatePostSettingsInput(sgqlc.types.Input):
    __schema__ = schema
    __field_names__ = ("is_table_of_content_enabled", "delisted", "disable_comments", "pin_to_blog")
    is_table_of_content_enabled = sgqlc.types.Field(Boolean, graphql_name="isTableOfContentEnabled")
    delisted = sgqlc.types.Field(Boolean, graphql_name="delisted")
    disable_comments = sgqlc.types.Field(Boolean, graphql_name="disableComments")
    pin_to_blog = sgqlc.types.Field(Boolean, graphql_name="pinToBlog")


########################################################################
# Output Objects and Interfaces
########################################################################
# class Connection(sgqlc.types.Interface):
#     __schema__ = schema
#     __field_names__ = ("edges", "page_info")
#     edges = sgqlc.types.Field(
#         sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("Edge"))), graphql_name="edges"
#     )
#     page_info = sgqlc.types.Field(sgqlc.types.non_null("PageInfo"), graphql_name="pageInfo")


# class Edge(sgqlc.types.Interface):
#     __schema__ = schema
#     __field_names__ = ("node", "cursor")
#     node = sgqlc.types.Field(sgqlc.types.non_null("Node"), graphql_name="node")
#     cursor = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="cursor")


# class Feature(sgqlc.types.Interface):
#     __schema__ = schema
#     __field_names__ = ("is_enabled",)
#     is_enabled = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isEnabled")


# class ITag(sgqlc.types.Interface):
#     __schema__ = schema
#     __field_names__ = ("id", "name", "slug", "logo", "tagline", "info", "posts_count")
#     id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
#     name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
#     slug = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="slug")
#     logo = sgqlc.types.Field(String, graphql_name="logo")
#     tagline = sgqlc.types.Field(String, graphql_name="tagline")
#     info = sgqlc.types.Field("Content", graphql_name="info")
#     posts_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="postsCount")


class Node(sgqlc.types.Interface):
    __schema__ = schema
    __field_names__ = ("id",)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")


# class PageConnection(sgqlc.types.Interface):
#     __schema__ = schema
#     __field_names__ = ("nodes", "page_info")
#     nodes = sgqlc.types.Field(
#         sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Node))), graphql_name="nodes"
#     )
#     page_info = sgqlc.types.Field(sgqlc.types.non_null("OffsetPageInfo"), graphql_name="pageInfo")


# class Views(sgqlc.types.Interface):
#     __schema__ = schema
#     __field_names__ = ("id", "total")
#     id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
#     total = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="total")


class AudioUrls(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("male", "female")
    male = sgqlc.types.Field(String, graphql_name="male")
    female = sgqlc.types.Field(String, graphql_name="female")


class Content(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("markdown", "html", "text")
    markdown = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="markdown")
    html = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="html")
    text = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="text")


# class CustomCSS(sgqlc.types.Type):
#     __schema__ = schema
#     __field_names__ = ("home", "post", "static", "home_minified", "post_minified", "static_minified")
#     home = sgqlc.types.Field(String, graphql_name="home")
#     post = sgqlc.types.Field(String, graphql_name="post")
#     static = sgqlc.types.Field(String, graphql_name="static")
#     home_minified = sgqlc.types.Field(String, graphql_name="homeMinified")
#     post_minified = sgqlc.types.Field(String, graphql_name="postMinified")
#     static_minified = sgqlc.types.Field(String, graphql_name="staticMinified")


class DomainInfo(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("hashnode_subdomain", "domain", "www_prefixed_domain")
    hashnode_subdomain = sgqlc.types.Field(String, graphql_name="hashnodeSubdomain")
    domain = sgqlc.types.Field("DomainStatus", graphql_name="domain")
    www_prefixed_domain = sgqlc.types.Field("DomainStatus", graphql_name="wwwPrefixedDomain")


class Mutation(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "publish_post",
        "update_post",
        "remove_post",
        "restore_post",
    )
    publish_post = sgqlc.types.Field(
        sgqlc.types.non_null("PublishPostPayload"),
        graphql_name="publishPost",
        args=sgqlc.types.ArgDict(
            (("input", sgqlc.types.Arg(sgqlc.types.non_null(PublishPostInput), graphql_name="input", default=None)),)
        ),
    )
    update_post = sgqlc.types.Field(
        sgqlc.types.non_null("UpdatePostPayload"),
        graphql_name="updatePost",
        args=sgqlc.types.ArgDict(
            (("input", sgqlc.types.Arg(sgqlc.types.non_null(UpdatePostInput), graphql_name="input", default=None)),)
        ),
    )
    remove_post = sgqlc.types.Field(
        sgqlc.types.non_null("RemovePostPayload"),
        graphql_name="removePost",
        args=sgqlc.types.ArgDict(
            (("input", sgqlc.types.Arg(sgqlc.types.non_null(RemovePostInput), graphql_name="input", default=None)),)
        ),
    )
    restore_post = sgqlc.types.Field(
        sgqlc.types.non_null("RestorePostPayload"),
        graphql_name="restorePost",
        args=sgqlc.types.ArgDict(
            (("input", sgqlc.types.Arg(sgqlc.types.non_null(RestorePostInput), graphql_name="input", default=None)),)
        ),
    )


# class OffsetPageInfo(sgqlc.types.Type):
#     __schema__ = schema
#     __field_names__ = ("has_next_page", "has_previous_page", "previous_page", "next_page")
#     has_next_page = sgqlc.types.Field(Boolean, graphql_name="hasNextPage")
#     has_previous_page = sgqlc.types.Field(Boolean, graphql_name="hasPreviousPage")
#     previous_page = sgqlc.types.Field(Int, graphql_name="previousPage")
#     next_page = sgqlc.types.Field(Int, graphql_name="nextPage")


class OpenGraphMetaData(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("image",)
    image = sgqlc.types.Field(String, graphql_name="image")


class PageInfo(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("has_next_page", "end_cursor")
    has_next_page = sgqlc.types.Field(Boolean, graphql_name="hasNextPage")
    end_cursor = sgqlc.types.Field(String, graphql_name="endCursor")


class PostCoverImage(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("url", "is_portrait", "attribution", "photographer", "is_attribution_hidden")
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")
    is_portrait = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isPortrait")
    attribution = sgqlc.types.Field(String, graphql_name="attribution")
    photographer = sgqlc.types.Field(String, graphql_name="photographer")
    is_attribution_hidden = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isAttributionHidden")


class PostFeatures(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("table_of_contents", "badges")
    table_of_contents = sgqlc.types.Field(
        sgqlc.types.non_null("TableOfContentsFeature"), graphql_name="tableOfContents"
    )


class PostPreferences(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("pinned_to_blog", "disable_comments", "stick_cover_to_bottom", "is_delisted")
    pinned_to_blog = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="pinnedToBlog")
    disable_comments = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="disableComments")
    stick_cover_to_bottom = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="stickCoverToBottom")
    is_delisted = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isDelisted")


# class PublicationFeatures(sgqlc.types.Type):
#     __schema__ = schema
#     __field_names__ = (
#         "view_count",
#         "read_time",
#         "audio_blog",
#         "text_selection_sharer",
#         "custom_css",
#         "headless_cms",
#         "pro_team",
#         "gpt_bot_crawling",
#     )
#     view_count = sgqlc.types.Field(sgqlc.types.non_null("ViewCountFeature"), graphql_name="viewCount")
#     read_time = sgqlc.types.Field(sgqlc.types.non_null("ReadTimeFeature"), graphql_name="readTime")
#     text_selection_sharer = sgqlc.types.Field(
#         sgqlc.types.non_null("TextSelectionSharerFeature"), graphql_name="textSelectionSharer"
#     )
#     custom_css = sgqlc.types.Field(sgqlc.types.non_null("CustomCSSFeature"), graphql_name="customCSS")
#     headless_cms = sgqlc.types.Field(sgqlc.types.non_null("HeadlessCMSFeature"), graphql_name="headlessCMS")
#     pro_team = sgqlc.types.Field(sgqlc.types.non_null("ProTeamFeature"), graphql_name="proTeam")
#     gpt_bot_crawling = sgqlc.types.Field(sgqlc.types.non_null("GPTBotCrawlingFeature"), graphql_name="gptBotCrawling")


class PublicationIntegrations(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "fb_pixel_id",
        "fathom_site_id",
        "fathom_custom_domain_enabled",
        "fathom_custom_domain",
        "hotjar_site_id",
        "matomo_site_id",
        "matomo_url",
        "ga_tracking_id",
        "plausible_analytics_enabled",
        "wm_payment_pointer",
        "umami_website_uuid",
        "umami_share_id",
        "g_tag_manager_id",
        "koala_public_key",
        "ms_clarity_id",
    )
    fb_pixel_id = sgqlc.types.Field(String, graphql_name="fbPixelID")
    fathom_site_id = sgqlc.types.Field(String, graphql_name="fathomSiteID")
    fathom_custom_domain_enabled = sgqlc.types.Field(Boolean, graphql_name="fathomCustomDomainEnabled")
    fathom_custom_domain = sgqlc.types.Field(String, graphql_name="fathomCustomDomain")
    hotjar_site_id = sgqlc.types.Field(String, graphql_name="hotjarSiteID")
    matomo_site_id = sgqlc.types.Field(String, graphql_name="matomoSiteID")
    matomo_url = sgqlc.types.Field(String, graphql_name="matomoURL")
    ga_tracking_id = sgqlc.types.Field(String, graphql_name="gaTrackingID")
    plausible_analytics_enabled = sgqlc.types.Field(Boolean, graphql_name="plausibleAnalyticsEnabled")
    wm_payment_pointer = sgqlc.types.Field(String, graphql_name="wmPaymentPointer")
    umami_website_uuid = sgqlc.types.Field(String, graphql_name="umamiWebsiteUUID")
    umami_share_id = sgqlc.types.Field(String, graphql_name="umamiShareId")
    g_tag_manager_id = sgqlc.types.Field(String, graphql_name="gTagManagerID")
    koala_public_key = sgqlc.types.Field(String, graphql_name="koalaPublicKey")
    ms_clarity_id = sgqlc.types.Field(String, graphql_name="msClarityID")


class PublicationLinks(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "twitter",
        "instagram",
        "github",
        "website",
        "hashnode",
        "youtube",
        "dailydev",
        "linkedin",
        "mastodon",
        "facebook",
        "bluesky",
    )
    twitter = sgqlc.types.Field(String, graphql_name="twitter")
    instagram = sgqlc.types.Field(String, graphql_name="instagram")
    github = sgqlc.types.Field(String, graphql_name="github")
    website = sgqlc.types.Field(String, graphql_name="website")
    hashnode = sgqlc.types.Field(String, graphql_name="hashnode")
    youtube = sgqlc.types.Field(String, graphql_name="youtube")
    dailydev = sgqlc.types.Field(String, graphql_name="dailydev")
    linkedin = sgqlc.types.Field(String, graphql_name="linkedin")
    mastodon = sgqlc.types.Field(String, graphql_name="mastodon")
    facebook = sgqlc.types.Field(String, graphql_name="facebook")
    bluesky = sgqlc.types.Field(String, graphql_name="bluesky")


# class PublishPostPayload(sgqlc.types.Type):
#     __schema__ = schema
#     __field_names__ = ("post",)
#     post = sgqlc.types.Field("Post", graphql_name="post")


class Query(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = (
        "tag",
        "publication",
        "post",
        "search_posts_of_publication",
    )
    tag = sgqlc.types.Field(
        "Tag",
        graphql_name="tag",
        args=sgqlc.types.ArgDict(
            (("slug", sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name="slug", default=None)),)
        ),
    )
    publication = sgqlc.types.Field(
        "Publication",
        graphql_name="publication",
        args=sgqlc.types.ArgDict(
            (
                ("id", sgqlc.types.Arg(ObjectId, graphql_name="id", default=None)),
                ("host", sgqlc.types.Arg(String, graphql_name="host", default=None)),
            )
        ),
    )
    post = sgqlc.types.Field(
        "Post",
        graphql_name="post",
        args=sgqlc.types.ArgDict((("id", sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name="id", default=None)),)),
    )
    search_posts_of_publication = sgqlc.types.Field(
        sgqlc.types.non_null("SearchPostConnection"),
        graphql_name="searchPostsOfPublication",
        args=sgqlc.types.ArgDict(
            (
                ("first", sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name="first", default=None)),
                ("after", sgqlc.types.Arg(String, graphql_name="after", default=None)),
                (
                    "filter",
                    sgqlc.types.Arg(
                        sgqlc.types.non_null(SearchPostsOfPublicationFilter), graphql_name="filter", default=None
                    ),
                ),
            )
        ),
    )


# class RemovePostPayload(sgqlc.types.Type):
#     __schema__ = schema
#     __field_names__ = ("post",)
#     post = sgqlc.types.Field("Post", graphql_name="post")


# class RestorePostPayload(sgqlc.types.Type):
#     __schema__ = schema
#     __field_names__ = ("post",)
#     post = sgqlc.types.Field("Post", graphql_name="post")


class SEO(sgqlc.types.Type):
    __schema__ = schema
    __field_names__ = ("title", "description")
    title = sgqlc.types.Field(String, graphql_name="title")
    description = sgqlc.types.Field(String, graphql_name="description")


# class UpdatePostPayload(sgqlc.types.Type):
#     __schema__ = schema
#     __field_names__ = ("post",)
#     post = sgqlc.types.Field("Post", graphql_name="post")


# class Badge(sgqlc.types.Type, Node):
#     __schema__ = schema
#     __field_names__ = ("name", "description", "image", "date_assigned", "info_url", "suppressed")
#     name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
#     description = sgqlc.types.Field(String, graphql_name="description")
#     image = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="image")
#     date_assigned = sgqlc.types.Field(DateTime, graphql_name="dateAssigned")
#     info_url = sgqlc.types.Field(String, graphql_name="infoURL")
#     suppressed = sgqlc.types.Field(Boolean, graphql_name="suppressed")


# class CustomCSSFeature(sgqlc.types.Type, Feature):
#     __schema__ = schema
#     __field_names__ = "published"
#     published = sgqlc.types.Field(CustomCSS, graphql_name="published")


# class FeedPostConnection(sgqlc.types.relay.Connection, Connection):
#     __schema__ = schema
#     __field_names__ = ()


# class PopularTag(sgqlc.types.Type, ITag, Node):
#     __schema__ = schema
#     __field_names__ = ("posts_count_in_period",)
#     posts_count_in_period = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="postsCountInPeriod")


# class PopularTagEdge(sgqlc.types.Type, Edge):
#     __schema__ = schema
#     __field_names__ = ()


class Post(sgqlc.types.Type, Node):
    __schema__ = schema
    __field_names__ = (
        "slug",
        "previous_slugs",
        "title",
        "subtitle",
        "tags",
        "url",
        "canonical_url",
        "publication",
        "cuid",
        "cover_image",
        "brief",
        "read_time_in_minutes",
        "views",
        "series",
        "reaction_count",
        "response_count",
        "featured",
        "bookmarked",
        "content",
        "featured_at",
        "published_at",
        "updated_at",
        "preferences",
        "audio_urls",
        "seo",
        "og_meta_data",
        "has_latex_in_post",
        "is_followed",
        "is_auto_published_from_rss",
        "features",
        "sourced_from_github",
    )
    slug = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="slug")
    previous_slugs = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name="previousSlugs"
    )
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="title")
    subtitle = sgqlc.types.Field(String, graphql_name="subtitle")
    tags = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null("Tag")), graphql_name="tags")
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")
    canonical_url = sgqlc.types.Field(String, graphql_name="canonicalUrl")
    publication = sgqlc.types.Field("Publication", graphql_name="publication")
    cuid = sgqlc.types.Field(String, graphql_name="cuid")
    cover_image = sgqlc.types.Field(PostCoverImage, graphql_name="coverImage")
    brief = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="brief")
    read_time_in_minutes = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="readTimeInMinutes")
    views = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="views")
    series = sgqlc.types.Field("Series", graphql_name="series")
    reaction_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="reactionCount")
    response_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="responseCount")
    featured = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="featured")
    bookmarked = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="bookmarked")
    content = sgqlc.types.Field(sgqlc.types.non_null(Content), graphql_name="content")
    featured_at = sgqlc.types.Field(DateTime, graphql_name="featuredAt")
    published_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name="publishedAt")
    updated_at = sgqlc.types.Field(DateTime, graphql_name="updatedAt")
    preferences = sgqlc.types.Field(sgqlc.types.non_null(PostPreferences), graphql_name="preferences")
    audio_urls = sgqlc.types.Field(AudioUrls, graphql_name="audioUrls")
    seo = sgqlc.types.Field(SEO, graphql_name="seo")
    og_meta_data = sgqlc.types.Field(OpenGraphMetaData, graphql_name="ogMetaData")
    has_latex_in_post = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="hasLatexInPost")
    is_followed = sgqlc.types.Field(Boolean, graphql_name="isFollowed")
    is_auto_published_from_rss = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isAutoPublishedFromRSS")
    features = sgqlc.types.Field(sgqlc.types.non_null(PostFeatures), graphql_name="features")
    sourced_from_github = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="sourcedFromGithub")


class Publication(sgqlc.types.Type, Node):
    __schema__ = schema
    __field_names__ = (
        "title",
        "display_title",
        "description_seo",
        "about",
        "url",
        "canonical_url",
        "favicon",
        "header_color",
        "integrations",
        "followers_count",
        "imprint",
        "imprint_v2",
        "is_team",
        "links",
        "domain_info",
        "is_headless",
        "series",
        "series_list",
        "posts",
        "posts_via_page",
        "pinned_post",
        "post",
        "redirected_post",
        "static_page",
        "static_pages",
        "is_git_hub_backup_enabled",
        "is_github_as_source_connected",
        "url_pattern",
        "has_badges",
    )
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="title")
    display_title = sgqlc.types.Field(String, graphql_name="displayTitle")
    description_seo = sgqlc.types.Field(String, graphql_name="descriptionSEO")
    about = sgqlc.types.Field(Content, graphql_name="about")
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")
    canonical_url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="canonicalURL")
    favicon = sgqlc.types.Field(String, graphql_name="favicon")
    header_color = sgqlc.types.Field(String, graphql_name="headerColor")
    integrations = sgqlc.types.Field(PublicationIntegrations, graphql_name="integrations")
    followers_count = sgqlc.types.Field(Int, graphql_name="followersCount")
    imprint = sgqlc.types.Field(String, graphql_name="imprint")
    imprint_v2 = sgqlc.types.Field(Content, graphql_name="imprintV2")
    is_team = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isTeam")
    links = sgqlc.types.Field(PublicationLinks, graphql_name="links")
    domain_info = sgqlc.types.Field(sgqlc.types.non_null(DomainInfo), graphql_name="domainInfo")
    is_headless = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isHeadless")
    series = sgqlc.types.Field(
        "Series",
        graphql_name="series",
        args=sgqlc.types.ArgDict(
            (("slug", sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name="slug", default=None)),)
        ),
    )
    series_list = sgqlc.types.Field(
        sgqlc.types.non_null("SeriesConnection"),
        graphql_name="seriesList",
        args=sgqlc.types.ArgDict(
            (
                ("first", sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name="first", default=None)),
                ("after", sgqlc.types.Arg(String, graphql_name="after", default=None)),
            )
        ),
    )
    posts = sgqlc.types.Field(
        sgqlc.types.non_null("PublicationPostConnection"),
        graphql_name="posts",
        args=sgqlc.types.ArgDict(
            (
                ("first", sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name="first", default=None)),
                ("after", sgqlc.types.Arg(String, graphql_name="after", default=None)),
                ("filter", sgqlc.types.Arg(PublicationPostConnectionFilter, graphql_name="filter", default=None)),
            )
        ),
    )
    posts_via_page = sgqlc.types.Field(
        sgqlc.types.non_null("PublicationPostPageConnection"),
        graphql_name="postsViaPage",
        args=sgqlc.types.ArgDict(
            (
                ("page_size", sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name="pageSize", default=None)),
                ("page", sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name="page", default=None)),
                ("filter", sgqlc.types.Arg(PublicationPostsViaPageFilter, graphql_name="filter", default=None)),
            )
        ),
    )
    pinned_post = sgqlc.types.Field(Post, graphql_name="pinnedPost")
    post = sgqlc.types.Field(
        Post,
        graphql_name="post",
        args=sgqlc.types.ArgDict(
            (("slug", sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name="slug", default=None)),)
        ),
    )
    redirected_post = sgqlc.types.Field(
        Post,
        graphql_name="redirectedPost",
        args=sgqlc.types.ArgDict(
            (("slug", sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name="slug", default=None)),)
        ),
    )
    static_page = sgqlc.types.Field(
        "StaticPage",
        graphql_name="staticPage",
        args=sgqlc.types.ArgDict(
            (("slug", sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name="slug", default=None)),)
        ),
    )
    static_pages = sgqlc.types.Field(
        sgqlc.types.non_null("StaticPageConnection"),
        graphql_name="staticPages",
        args=sgqlc.types.ArgDict(
            (
                ("first", sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name="first", default=None)),
                ("after", sgqlc.types.Arg(String, graphql_name="after", default=None)),
            )
        ),
    )
    is_git_hub_backup_enabled = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isGitHubBackupEnabled")
    is_github_as_source_connected = sgqlc.types.Field(
        sgqlc.types.non_null(Boolean), graphql_name="isGithubAsSourceConnected"
    )
    url_pattern = sgqlc.types.Field(sgqlc.types.non_null(UrlPattern), graphql_name="urlPattern")
    has_badges = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="hasBadges")


# class ReadTimeFeature(sgqlc.types.Type, Feature):
#     __schema__ = schema
#     __field_names__ = ()


# class SearchPostConnection(sgqlc.types.relay.Connection, Connection):
#     __schema__ = schema
#     __field_names__ = ()


# class Series(sgqlc.types.Type, Node):
#     __schema__ = schema
#     __field_names__ = (
#         "name",
#         "created_at",
#         "description",
#         "cover_image",
#         "author",
#         "cuid",
#         "slug",
#         "sort_order",
#         "posts",
#     )
#     name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
#     created_at = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name="createdAt")
#     description = sgqlc.types.Field(Content, graphql_name="description")
#     cover_image = sgqlc.types.Field(String, graphql_name="coverImage")
#     cuid = sgqlc.types.Field(ID, graphql_name="cuid")
#     slug = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="slug")
#     sort_order = sgqlc.types.Field(sgqlc.types.non_null(SortOrder), graphql_name="sortOrder")
#     posts = sgqlc.types.Field(
#         sgqlc.types.non_null("SeriesPostConnection"),
#         graphql_name="posts",
#         args=sgqlc.types.ArgDict(
#             (
#                 ("first", sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name="first", default=None)),
#                 ("after", sgqlc.types.Arg(String, graphql_name="after", default=None)),
#             )
#         ),
#     )


# class StaticPage(sgqlc.types.Type, Node):
#     __schema__ = schema
#     __field_names__ = ("title", "slug", "content", "hidden", "og_meta_data", "seo")
#     title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="title")
#     slug = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="slug")
#     content = sgqlc.types.Field(sgqlc.types.non_null(Content), graphql_name="content")
#     hidden = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="hidden")
#     og_meta_data = sgqlc.types.Field(OpenGraphMetaData, graphql_name="ogMetaData")
#     seo = sgqlc.types.Field(SEO, graphql_name="seo")


# class TableOfContentsFeature(sgqlc.types.Type, Feature):
#     __schema__ = schema
#     __field_names__ = ("items",)
#     items = sgqlc.types.Field(
#         sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null("TableOfContentsItem"))), graphql_name="items"
#     )


# class TableOfContentsItem(sgqlc.types.Type, Node):
#     __schema__ = schema
#     __field_names__ = ("level", "slug", "title", "parent_id")
#     level = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="level")
#     slug = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="slug")
#     title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="title")
#     parent_id = sgqlc.types.Field(ID, graphql_name="parentId")


# class Tag(sgqlc.types.Type, ITag, Node):
#     __schema__ = schema
#     __field_names__ = ("posts",)
#     posts = sgqlc.types.Field(
#         sgqlc.types.non_null(FeedPostConnection),
#         graphql_name="posts",
#         args=sgqlc.types.ArgDict(
#             (
#                 ("first", sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name="first", default=None)),
#                 ("after", sgqlc.types.Arg(String, graphql_name="after", default=None)),
#                 (
#                     "filter",
#                     sgqlc.types.Arg(sgqlc.types.non_null(TagPostConnectionFilter), graphql_name="filter", default=None),
#                 ),
#             )
#         ),
#     )


# class TagEdge(sgqlc.types.Type, Edge):
#     __schema__ = schema
#     __field_names__ = ()


# class TextSelectionSharerFeature(sgqlc.types.Type, Feature):
#     __schema__ = schema
#     __field_names__ = ()


# class ViewCountFeature(sgqlc.types.Type, Feature):
#     __schema__ = schema
#     __field_names__ = ()


########################################################################
# Schema Entry Points
########################################################################
schema.query_type = Query
schema.mutation_type = Mutation
schema.subscription_type = None
