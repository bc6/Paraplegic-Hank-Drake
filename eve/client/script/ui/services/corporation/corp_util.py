VIEW_ROLES = 0
VIEW_GRANTABLE_ROLES = 1
VIEW_TITLES = 2
GROUP_GENERAL_ROLES = 0
GROUP_DIVISIONAL_ACCOUNTING_ROLES = 1
GROUP_DIVISIONAL_HANGAR_ROLES_AT_HQ = 2
GROUP_DIVISIONAL_CONTAINER_ROLES_AT_HQ = 3
GROUP_DIVISIONAL_HANGAR_ROLES_AT_BASE = 4
GROUP_DIVISIONAL_CONTAINER_ROLES_AT_BASE = 5
GROUP_DIVISIONAL_HANGAR_ROLES_AT_OTHER = 6
GROUP_DIVISIONAL_CONTAINER_ROLES_AT_OTHER = 7
exports = {}
for i in globals().items():
    if type(i[1]) == type(0):
        exports['corputil.' + i[0]] = i[1]


def CanEditRole(roleID, grantable, playerIsCEO, playerIsDirector, IAmCEO, viewRoleGroupingID, myBaseID, playersBaseID, myGrantableRoles, myGrantableRolesAtHQ, myGrantableRolesAtBase, myGrantableRolesAtOther):
    if grantable:
        if roleID == const.corpRoleDirector:
            return 0
        if eve.session.corprole & const.corpRoleDirector != const.corpRoleDirector:
            return 0
        if playerIsCEO:
            return 0
        if playerIsDirector:
            return 0
        return 1
    else:
        if playerIsCEO:
            return 0
        if playerIsDirector and not IAmCEO:
            return 0
        if playerIsDirector and roleID & const.corpRoleDirector != const.corpRoleDirector:
            return 0
        roleGroupings = sm.GetService('corp').GetRoleGroupings()
        if not roleGroupings.has_key(viewRoleGroupingID):
            raise RuntimeError('UnknownViewType')
        roleGroup = roleGroupings[viewRoleGroupingID]
        if roleGroup.appliesTo == 'roles':
            if myGrantableRoles & roleID != roleID:
                return 0
        elif roleGroup.appliesTo == 'rolesAtHQ':
            if myGrantableRolesAtHQ & roleID != roleID:
                return 0
        elif roleGroup.appliesTo == 'rolesAtBase':
            if IAmCEO:
                return 1
            if const.corpRoleDirector & eve.session.corprole == const.corpRoleDirector and not playerIsDirector:
                return 1
            if myBaseID != playersBaseID:
                return 0
            if myGrantableRolesAtBase & roleID != roleID:
                return 0
        elif roleGroup.appliesTo == 'rolesAtOther':
            if myGrantableRolesAtOther & roleID != roleID:
                return 0
        return 1



def CanEditBase(playerIsCEO, IAmCEO, IAmDirector):
    if playerIsCEO:
        if IAmCEO:
            return 1
    elif IAmCEO:
        return 1
    if IAmDirector:
        return 1
    return 0


exports.update({'corputil.CanEditRole': CanEditRole,
 'corputil.CanEditBase': CanEditBase})

