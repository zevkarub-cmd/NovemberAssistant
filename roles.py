ROLE_BARISTA = "barista"
ROLE_SENIOR = "senior_barista"
ROLE_MANAGER = "manager"
ROLE_OWNER = "owner"
ROLE_BOUTIQUE_OWNER = "boutique_owner"
ROLE_FIRED = "fired"
ROLE_VERIFICATION = "verification"

ROLE_LABELS = {
    ROLE_BARISTA: "Бариста",
    ROLE_SENIOR: "Старший бариста",
    ROLE_MANAGER: "Управляющий",
    ROLE_OWNER: "Владелец",
    ROLE_BOUTIQUE_OWNER: "Владелец бутика",
    ROLE_FIRED: "Уволенный",
    ROLE_VERIFICATION: "Верификация",
}

ALL_ROLES = (
    ROLE_BARISTA,
    ROLE_SENIOR,
    ROLE_MANAGER,
    ROLE_OWNER,
    ROLE_BOUTIQUE_OWNER,
    ROLE_FIRED,
    ROLE_VERIFICATION,
)

BLOCKED_ROLES = (
    ROLE_FIRED,
    ROLE_VERIFICATION,
)

BROADCAST_EXCLUDED_ROLES = (
    ROLE_BOUTIQUE_OWNER,
    ROLE_FIRED,
    ROLE_VERIFICATION,
)


def role_label(role):
    return ROLE_LABELS.get(role, ROLE_LABELS[ROLE_BARISTA])


def can_use_bot(role):
    return role not in BLOCKED_ROLES


def has_barista_access(role):
    return role in (
        ROLE_BARISTA,
        ROLE_SENIOR,
        ROLE_MANAGER,
        ROLE_OWNER,
        ROLE_BOUTIQUE_OWNER,
    )


def can_view_history(role):
    return role in (ROLE_SENIOR, ROLE_MANAGER, ROLE_OWNER)


def can_manage_employees(role):
    return role in (ROLE_MANAGER, ROLE_OWNER)


def can_view_employees(role):
    return role in (ROLE_MANAGER, ROLE_OWNER)


def can_manage_checklists(role):
    return role in (ROLE_MANAGER, ROLE_OWNER)


def can_broadcast(role):
    return role == ROLE_OWNER
