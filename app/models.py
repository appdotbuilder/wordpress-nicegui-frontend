from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any


# ============================================================================
# PERSISTENT MODELS (Database Tables)
# ============================================================================


class User(SQLModel, table=True):
    """WordPress user/author model"""

    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    wp_id: int = Field(unique=True, index=True)  # WordPress user ID
    name: str = Field(max_length=255)
    email: str = Field(max_length=255, index=True)
    slug: str = Field(max_length=255, unique=True, index=True)
    description: str = Field(default="", max_length=2000)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    website_url: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    posts: List["Post"] = Relationship(back_populates="author")
    pages: List["Page"] = Relationship(back_populates="author")


class Category(SQLModel, table=True):
    """WordPress category model"""

    __tablename__ = "categories"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    wp_id: int = Field(unique=True, index=True)  # WordPress category ID
    name: str = Field(max_length=255, index=True)
    slug: str = Field(max_length=255, unique=True, index=True)
    description: str = Field(default="", max_length=2000)
    parent_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    count: int = Field(default=0)  # Number of posts in this category
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Self-referential relationship for parent/child categories
    parent: Optional["Category"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "Category.id"}
    )
    children: List["Category"] = Relationship(back_populates="parent")


class Tag(SQLModel, table=True):
    """WordPress tag model"""

    __tablename__ = "tags"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    wp_id: int = Field(unique=True, index=True)  # WordPress tag ID
    name: str = Field(max_length=255, index=True)
    slug: str = Field(max_length=255, unique=True, index=True)
    description: str = Field(default="", max_length=2000)
    count: int = Field(default=0)  # Number of posts with this tag
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# ASSOCIATION TABLES (Many-to-Many Relationships)
# ============================================================================


class PostCategoryLink(SQLModel, table=True):
    """Link table for Post-Category many-to-many relationship"""

    __tablename__ = "post_category_links"  # type: ignore[assignment]

    post_id: int = Field(foreign_key="posts.id", primary_key=True)
    category_id: int = Field(foreign_key="categories.id", primary_key=True)


class PostTagLink(SQLModel, table=True):
    """Link table for Post-Tag many-to-many relationship"""

    __tablename__ = "post_tag_links"  # type: ignore[assignment]

    post_id: int = Field(foreign_key="posts.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)


# ============================================================================
# MEDIA AND CONTENT MODELS
# ============================================================================


class Media(SQLModel, table=True):
    """WordPress media/attachment model"""

    __tablename__ = "media"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    wp_id: int = Field(unique=True, index=True)  # WordPress media ID
    title: str = Field(max_length=255)
    filename: str = Field(max_length=255)
    alt_text: str = Field(default="", max_length=255)
    caption: str = Field(default="", max_length=2000)
    description: str = Field(default="", max_length=2000)
    mime_type: str = Field(max_length=100, index=True)
    file_size: Optional[int] = Field(default=None)  # File size in bytes
    width: Optional[int] = Field(default=None)
    height: Optional[int] = Field(default=None)
    source_url: str = Field(max_length=500)  # Full size image URL
    sizes: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # Different image sizes
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    featured_in_posts: List["Post"] = Relationship(back_populates="featured_image")
    featured_in_pages: List["Page"] = Relationship(back_populates="featured_image")


class Post(SQLModel, table=True):
    """WordPress post model"""

    __tablename__ = "posts"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    wp_id: int = Field(unique=True, index=True)  # WordPress post ID
    title: str = Field(max_length=500, index=True)
    slug: str = Field(max_length=255, unique=True, index=True)
    content: str = Field(default="")  # Full HTML content
    excerpt: str = Field(default="", max_length=2000)
    status: str = Field(default="publish", max_length=20, index=True)  # publish, draft, private, etc.
    post_type: str = Field(default="post", max_length=50, index=True)
    comment_count: int = Field(default=0)
    view_count: int = Field(default=0)  # For analytics
    meta_title: Optional[str] = Field(default=None, max_length=255)  # SEO
    meta_description: Optional[str] = Field(default=None, max_length=500)  # SEO

    # WordPress timestamps
    wp_created_at: datetime = Field(index=True)  # WordPress publish date
    wp_updated_at: datetime = Field(index=True)  # WordPress modified date

    # Local timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign keys
    author_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    featured_image_id: Optional[int] = Field(default=None, foreign_key="media.id")

    # Relationships
    author: Optional[User] = Relationship(back_populates="posts")
    featured_image: Optional[Media] = Relationship(back_populates="featured_in_posts")
    categories: List[Category] = Relationship(link_model=PostCategoryLink)
    tags: List[Tag] = Relationship(link_model=PostTagLink)


class Page(SQLModel, table=True):
    """WordPress page model"""

    __tablename__ = "pages"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    wp_id: int = Field(unique=True, index=True)  # WordPress page ID
    title: str = Field(max_length=500, index=True)
    slug: str = Field(max_length=255, unique=True, index=True)
    content: str = Field(default="")  # Full HTML content
    status: str = Field(default="publish", max_length=20, index=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="pages.id")
    menu_order: int = Field(default=0)  # For page hierarchy/ordering
    template: Optional[str] = Field(default=None, max_length=100)  # Page template
    meta_title: Optional[str] = Field(default=None, max_length=255)  # SEO
    meta_description: Optional[str] = Field(default=None, max_length=500)  # SEO

    # WordPress timestamps
    wp_created_at: datetime = Field(index=True)
    wp_updated_at: datetime = Field(index=True)

    # Local timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign keys
    author_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    featured_image_id: Optional[int] = Field(default=None, foreign_key="media.id")

    # Relationships
    author: Optional[User] = Relationship(back_populates="pages")
    featured_image: Optional[Media] = Relationship(back_populates="featured_in_pages")
    parent: Optional["Page"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "Page.id"}
    )
    children: List["Page"] = Relationship(back_populates="parent")


class Menu(SQLModel, table=True):
    """WordPress navigation menu model"""

    __tablename__ = "menus"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    wp_id: int = Field(unique=True, index=True)  # WordPress menu ID
    name: str = Field(max_length=255, index=True)
    slug: str = Field(max_length=255, unique=True, index=True)
    location: Optional[str] = Field(default=None, max_length=100, index=True)  # Theme location
    count: int = Field(default=0)  # Number of menu items
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    items: List["MenuItem"] = Relationship(back_populates="menu")


class MenuItem(SQLModel, table=True):
    """WordPress menu item model"""

    __tablename__ = "menu_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    wp_id: int = Field(unique=True, index=True)  # WordPress menu item ID
    title: str = Field(max_length=255)
    url: str = Field(max_length=500)
    target: Optional[str] = Field(default=None, max_length=20)  # _blank, _self, etc.
    description: str = Field(default="", max_length=500)
    css_classes: List[str] = Field(default=[], sa_column=Column(JSON))
    order: int = Field(default=0, index=True)  # Menu item order
    parent_id: Optional[int] = Field(default=None, foreign_key="menu_items.id")

    # Object reference (for internal links)
    object_id: Optional[int] = Field(default=None)  # ID of linked post/page
    object_type: Optional[str] = Field(default=None, max_length=50)  # post, page, category, etc.

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign keys
    menu_id: int = Field(foreign_key="menus.id", index=True)

    # Relationships
    menu: Menu = Relationship(back_populates="items")
    parent: Optional["MenuItem"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "MenuItem.id"}
    )
    children: List["MenuItem"] = Relationship(back_populates="parent")


class CustomPostType(SQLModel, table=True):
    """Flexible model for WordPress custom post types"""

    __tablename__ = "custom_post_types"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    wp_id: int = Field(unique=True, index=True)  # WordPress post ID
    post_type: str = Field(max_length=50, index=True)  # Custom post type name
    title: str = Field(max_length=500, index=True)
    slug: str = Field(max_length=255, index=True)
    content: str = Field(default="")
    excerpt: str = Field(default="", max_length=2000)
    status: str = Field(default="publish", max_length=20, index=True)
    custom_fields: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # ACF fields, etc.

    # WordPress timestamps
    wp_created_at: datetime = Field(index=True)
    wp_updated_at: datetime = Field(index=True)

    # Local timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign keys
    author_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    featured_image_id: Optional[int] = Field(default=None, foreign_key="media.id")

    # Relationships
    author: Optional[User] = Relationship()
    featured_image: Optional[Media] = Relationship()


# ============================================================================
# APPLICATION SETTINGS & CACHE
# ============================================================================


class AppSettings(SQLModel, table=True):
    """Application-level settings and configuration"""

    __tablename__ = "app_settings"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(max_length=255, unique=True, index=True)
    value: str = Field(max_length=2000)
    description: str = Field(default="", max_length=500)
    is_public: bool = Field(default=False)  # Can be exposed to frontend
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CacheEntry(SQLModel, table=True):
    """Cache for GraphQL responses and computed data"""

    __tablename__ = "cache_entries"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    cache_key: str = Field(max_length=255, unique=True, index=True)
    data: Dict[str, Any] = Field(sa_column=Column(JSON))
    expires_at: Optional[datetime] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# NON-PERSISTENT SCHEMAS (API & Validation)
# ============================================================================


class UserResponse(SQLModel, table=False):
    """Schema for user API responses"""

    id: int
    wp_id: int
    name: str
    email: str
    slug: str
    description: str
    avatar_url: Optional[str] = None
    website_url: Optional[str] = None


class CategoryResponse(SQLModel, table=False):
    """Schema for category API responses"""

    id: int
    wp_id: int
    name: str
    slug: str
    description: str
    count: int
    parent_id: Optional[int] = None


class TagResponse(SQLModel, table=False):
    """Schema for tag API responses"""

    id: int
    wp_id: int
    name: str
    slug: str
    description: str
    count: int


class MediaResponse(SQLModel, table=False):
    """Schema for media API responses"""

    id: int
    wp_id: int
    title: str
    alt_text: str
    caption: str
    mime_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    source_url: str
    sizes: Dict[str, Any] = {}


class PostSummary(SQLModel, table=False):
    """Schema for post list/summary responses"""

    id: int
    wp_id: int
    title: str
    slug: str
    excerpt: str
    status: str
    wp_created_at: str  # ISO format
    wp_updated_at: str  # ISO format
    author: Optional[UserResponse] = None
    featured_image: Optional[MediaResponse] = None
    categories: List[CategoryResponse] = []
    tags: List[TagResponse] = []


class PostDetail(SQLModel, table=False):
    """Schema for detailed post responses"""

    id: int
    wp_id: int
    title: str
    slug: str
    content: str
    excerpt: str
    status: str
    comment_count: int
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    wp_created_at: str  # ISO format
    wp_updated_at: str  # ISO format
    author: Optional[UserResponse] = None
    featured_image: Optional[MediaResponse] = None
    categories: List[CategoryResponse] = []
    tags: List[TagResponse] = []


class PageResponse(SQLModel, table=False):
    """Schema for page responses"""

    id: int
    wp_id: int
    title: str
    slug: str
    content: str
    status: str
    menu_order: int
    template: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    wp_created_at: str  # ISO format
    wp_updated_at: str  # ISO format
    author: Optional[UserResponse] = None
    featured_image: Optional[MediaResponse] = None
    parent_id: Optional[int] = None


class MenuItemResponse(SQLModel, table=False):
    """Schema for menu item responses"""

    id: int
    wp_id: int
    title: str
    url: str
    target: Optional[str] = None
    description: str
    css_classes: List[str] = []
    order: int
    parent_id: Optional[int] = None
    object_id: Optional[int] = None
    object_type: Optional[str] = None
    children: List["MenuItemResponse"] = []


# Fix forward reference for MenuItemResponse
MenuItemResponse.model_rebuild()


class MenuResponse(SQLModel, table=False):
    """Schema for menu responses"""

    id: int
    wp_id: int
    name: str
    slug: str
    location: Optional[str] = None
    items: List[MenuItemResponse] = []


class CustomPostTypeResponse(SQLModel, table=False):
    """Schema for custom post type responses"""

    id: int
    wp_id: int
    post_type: str
    title: str
    slug: str
    content: str
    excerpt: str
    status: str
    custom_fields: Dict[str, Any] = {}
    wp_created_at: str  # ISO format
    wp_updated_at: str  # ISO format
    author: Optional[UserResponse] = None
    featured_image: Optional[MediaResponse] = None


class SearchRequest(SQLModel, table=False):
    """Schema for search requests"""

    query: str = Field(min_length=1, max_length=255)
    post_type: Optional[str] = Field(default="post", max_length=50)
    category_slug: Optional[str] = Field(default=None, max_length=255)
    tag_slug: Optional[str] = Field(default=None, max_length=255)
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class SearchResponse(SQLModel, table=False):
    """Schema for search responses"""

    query: str
    total_results: int
    posts: List[PostSummary] = []
    pages: List[PageResponse] = []
    custom_posts: List[CustomPostTypeResponse] = []


class GraphQLRequest(SQLModel, table=False):
    """Schema for GraphQL request validation"""

    query: str
    variables: Optional[Dict[str, Any]] = None
    operation_name: Optional[str] = None


class GraphQLResponse(SQLModel, table=False):
    """Schema for GraphQL response validation"""

    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[Dict[str, Any]]] = None
    extensions: Optional[Dict[str, Any]] = None


class PaginationParams(SQLModel, table=False):
    """Schema for pagination parameters"""

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1, le=100)
    order_by: str = Field(default="wp_created_at", max_length=50)
    order: str = Field(default="desc", regex="^(asc|desc)$")


class PaginatedResponse(SQLModel, table=False):
    """Generic schema for paginated responses"""

    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_previous: bool
