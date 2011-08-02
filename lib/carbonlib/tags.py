import const
if const.world.WORLD_SPACE_SCHEMA == 'zworld':
    TAGS_SCHEMA = 'zworld'
else:
    TAGS_SCHEMA = 'tags'
_TAGS_PREFIX = TAGS_SCHEMA + '.'
TAGS_TYPE_TABLE_FULL_NAME = _TAGS_PREFIX + 'staticTypes'
TAGS_TAGS_TABLE_FULL_NAME = _TAGS_PREFIX + 'staticTags'
SELECT_TAGS = 'SelectTags'
SELECT_TAGS_MODULE = 'SelectTagsModule'
TAGS_SELECTION_EVENTS = [SELECT_TAGS, SELECT_TAGS_MODULE]
TAGS_TYPE_EDITOR = 'WoD Tag Type Editor'
TAGS_EDITOR = 'WoD Tag Editor'

