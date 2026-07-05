from loguru import logger
from sqlalchemy.orm import Session

from app.models.auth import Permission, Role, RolePermission

ROLES = [
    {"name": "Super Admin", "slug": "super-admin", "description": "Full system access", "is_system": True, "sort_order": 0},
    {"name": "Admin", "slug": "admin", "description": "Management access", "is_system": True, "sort_order": 1},
    {"name": "Editor", "slug": "editor", "description": "Create and publish content", "is_system": True, "sort_order": 2},
    {"name": "SEO Manager", "slug": "seo-manager", "description": "Manage SEO metadata", "is_system": True, "sort_order": 3},
    {"name": "Content Writer", "slug": "content-writer", "description": "Create content", "is_system": True, "sort_order": 4},
    {"name": "Reviewer", "slug": "reviewer", "description": "Review content", "is_system": True, "sort_order": 5},
    {"name": "Support", "slug": "support", "description": "Support access", "is_system": True, "sort_order": 6},
]

RESOURCES = [
    "calculator", "blog_post", "guide", "category", "media", "page",
    "navigation", "footer", "advertisement", "setting", "user", "role",
    "analytics", "newsletter", "testimonial", "redirect", "sitemap",
    "audit_log", "author", "reviewer",
]

ACTIONS = ["create", "read", "update", "delete", "publish", "unpublish", "archive", "restore", "review", "approve", "reject", "manage"]

ROLE_PERMISSIONS = {
    "super-admin": [f"{r}:{a}" for r in RESOURCES for a in ACTIONS],
    "admin": [f"{r}:{a}" for r in RESOURCES for a in ["create", "read", "update", "delete", "publish", "unpublish", "archive"]],
    "editor": [f"{r}:{a}" for r in ["calculator", "blog_post", "guide", "category", "media", "page"] for a in ["create", "read", "update", "publish", "unpublish"]],
    "seo-manager": [f"{r}:{a}" for r in ["seo", "redirect", "sitemap", "page"] for a in ["create", "read", "update", "manage"]],
    "content-writer": [f"{r}:{a}" for r in ["calculator", "blog_post", "guide"] for a in ["create", "read", "update"]] + ["media:upload"],
    "reviewer": [f"{r}:{a}" for r in ["calculator", "blog_post", "guide"] for a in ["read", "review", "approve", "reject"]],
    "support": [f"{r}:read" for r in ["calculator", "blog_post", "guide", "category"]] + ["newsletter:read", "newsletter:update"],
}


def seed_permissions(db: Session) -> list[dict]:
    created = []
    for resource in RESOURCES:
        for action in ACTIONS:
            existing = db.query(Permission).filter(
                Permission.resource == resource,
                Permission.action == action,
            ).first()
            if not existing:
                perm = Permission(
                    resource=resource,
                    action=action,
                    description=f"{action.capitalize()} {resource.replace('_', ' ')}",
                )
                db.add(perm)
                created.append(f"{resource}:{action}")
    db.commit()
    logger.info(f"Seeded {len(created)} permissions")
    return {"permissions_created": len(created)}


def seed_roles(db: Session) -> dict:
    result = {"roles_created": 0, "permissions_created": 0}

    seed_permissions(db)

    for role_data in ROLES:
        existing = db.query(Role).filter(Role.slug == role_data["slug"]).first()
        if not existing:
            role = Role(**role_data)
            db.add(role)
            db.flush()
            result["roles_created"] += 1
        else:
            role = existing

        perm_strings = ROLE_PERMISSIONS.get(role_data["slug"], [])
        for perm_str in perm_strings:
            resource, action = perm_str.split(":", 1)
            perm = db.query(Permission).filter(
                Permission.resource == resource,
                Permission.action == action,
            ).first()
            if perm:
                existing_rp = db.query(RolePermission).filter(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == perm.id,
                ).first()
                if not existing_rp:
                    rp = RolePermission(role_id=role.id, permission_id=perm.id)
                    db.add(rp)
                    result["permissions_created"] += 1

    db.commit()
    logger.info(f"Seeded roles: {result}")
    return result
